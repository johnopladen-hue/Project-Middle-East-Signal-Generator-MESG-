"""Geo endpoint - located items (stories/signals share a Story's location;
organizations) as GeoJSON, scoped by AOR + time window + D-008 source scope
as three separate filters (D-014, O-7). Unknown-location items are a
separate, visible set - never a fake pin (Principle 11)."""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AorMembership, ItemLocation, Organization, RawItem, Source, Story, TranslationRecord

router = APIRouter(prefix="/geo", tags=["geo"])

_CENTROIDS_PATH = Path(__file__).resolve().parent.parent / "geo" / "country_centroids.json"
_CENTROIDS = json.loads(_CENTROIDS_PATH.read_text(encoding="utf-8"))

# D-008: the only source scope this v1 register actually has. Accepted as a
# real filter parameter (not silently ignored) rather than pretended-away;
# there is nothing else to filter to yet.
SUPPORTED_SCOPES = ("v1",)

# D-023: real news items on the map. The map shows at most ITEM_LIMIT of them
# (the Owner's "top 10-20 where they occurred", 2026-11-01): city- and
# province-level placements first, then country-level, newest first within
# each. Country-level placements were the least reliable in the build's
# spot-check (findings.md), so they only fill spare slots.
ITEM_WINDOW_HOURS = 48
ITEM_LIMIT = 20
ITEM_LIMIT_MAX = 50
TITLE_MAX = 140
# Items sharing one place are spread on a small circle around it so each dot
# stays clickable: "in the vicinity". Degrees, roughly 6 / 25 / 60 km.
SPREAD_RADIUS_DEG = {"city": 0.06, "province": 0.25, "country": 0.6}
_PRECISION_ORDER = {"city": 0, "province": 0, "country": 1}


def _headline(raw_item: RawItem, translated: bool) -> str:
    text = raw_item.working_text if translated and raw_item.working_text else raw_item.original_text
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("Forwarded from")]
    title = lines[0] if lines else text.strip()
    return title if len(title) <= TITLE_MAX else title[: TITLE_MAX - 1].rstrip() + "…"


def _spread(selected: list[tuple]) -> dict[int, tuple[float, float]]:
    """Display coordinates per item id: the place itself for a lone item,
    evenly spaced around it when several items share the place."""
    groups: dict[tuple[float, float], list[tuple]] = {}
    for row in selected:
        location = row[1]
        groups.setdefault((location.longitude, location.latitude), []).append(row)
    display: dict[int, tuple[float, float]] = {}
    for (lon, lat), rows in groups.items():
        if len(rows) == 1:
            display[rows[0][0].id] = (lon, lat)
            continue
        radius = SPREAD_RADIUS_DEG[rows[0][1].precision]
        for k, row in enumerate(rows):
            angle = 2 * math.pi * k / len(rows)
            display[row[0].id] = (
                round(lon + radius * math.cos(angle) / max(math.cos(math.radians(lat)), 0.2), 4),
                round(lat + radius * math.sin(angle), 4),
            )
    return display


def _news_items(
    db: Session, aor_countries: set[str], window_hours: int, limit: int, until: datetime | None
) -> tuple[list[dict], dict]:
    # The window ends at `until` (the endpoint's existing time-window parameter), else now.
    item_time = func.coalesce(RawItem.published_at, RawItem.fetched_at)
    end = until or datetime.now(timezone.utc)
    cutoff = end - timedelta(hours=window_hours)
    in_window = db.query(RawItem.id).filter(item_time >= cutoff).filter(item_time <= end)

    query = (
        db.query(RawItem, ItemLocation, Source)
        .join(ItemLocation, ItemLocation.raw_item_id == RawItem.id)
        .join(Source, Source.id == RawItem.source_id)
        .filter(ItemLocation.status == "located")
        .filter(item_time >= cutoff)
        .filter(item_time <= end)
    )
    if aor_countries:
        query = query.filter(ItemLocation.country.in_(aor_countries))
    rows = query.order_by(item_time.desc(), RawItem.id.desc()).all()
    rows.sort(key=lambda row: _PRECISION_ORDER[row[1].precision])  # stable: newest first within each tier
    selected = rows[:limit]

    translated_ids = {
        raw_item_id
        for (raw_item_id,) in db.query(TranslationRecord.raw_item_id)
        .filter(TranslationRecord.raw_item_id.in_([row[0].id for row in selected]))
        .filter(TranslationRecord.status.in_(("ok", "ok_truncated")))
    }
    display = _spread(selected)
    features = []
    for raw_item, location, source in selected:
        published = raw_item.published_at or raw_item.fetched_at
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": list(display[raw_item.id])},
                "properties": {
                    "kind": "item",
                    "id": raw_item.id,
                    "title": _headline(raw_item, raw_item.id in translated_ids),
                    "precision": location.precision,
                    "country": location.country,
                    "place_name": location.place_name,
                    "place_coordinates": [location.longitude, location.latitude],
                    "matched_text": location.matched_text,
                    "source_name": source.name,
                    "original_lang": raw_item.original_lang,
                    "published_at": published.isoformat() if published else None,
                    "detail_url": f"/incoming/{raw_item.id}",
                },
            }
        )

    total_in_window = in_window.count()
    checked = db.query(ItemLocation.raw_item_id).filter(ItemLocation.raw_item_id.in_(in_window))
    summary = {
        "window_hours": window_hours,
        "items_in_window": total_in_window,
        "located_in_aor": len(rows),
        "shown": len(selected),
        "not_located": checked.filter(ItemLocation.status == "none").count(),
        "not_checked_yet": total_in_window - checked.count(),
        "attribution": "Item places: GeoNames (geonames.org), CC BY 4.0. Machine-matched from the original text; not verified.",
    }
    return features, summary


def _story_feature(story, detail_url: str) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [story.longitude, story.latitude]},
        "properties": {
            "kind": "story",
            "id": story.id,
            "title": story.title,
            "precision": story.location_precision,
            "country": story.location_country,
            "detail_url": detail_url,
        },
    }


def _organization_feature(org: Organization, detail_url: str) -> dict:
    lon, lat = _CENTROIDS[org.theatre.name]
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "kind": "organization",
            "id": org.id,
            "title": org.name,
            "precision": "country",
            "country": org.theatre.name,
            "detail_url": detail_url,
        },
    }


@router.get("/items")
def get_geo_items(
    aor: str = Query("CENTCOM"),
    since: datetime | None = Query(None),
    until: datetime | None = Query(None),
    scope: str = Query("v1"),
    item_window_hours: int = Query(ITEM_WINDOW_HOURS, ge=1, le=24 * 7),
    item_limit: int = Query(ITEM_LIMIT, ge=1, le=ITEM_LIMIT_MAX),
    db: Session = Depends(get_db),
):
    if scope not in SUPPORTED_SCOPES:
        raise HTTPException(status_code=400, detail=f"Unsupported scope {scope!r}; only {SUPPORTED_SCOPES} exist")

    aor_countries = {
        row.country_name for row in db.query(AorMembership).filter_by(aor=aor.upper()).all()
    }

    story_query = db.query(Story)
    if since is not None:
        story_query = story_query.filter(Story.first_seen_at >= since)
    if until is not None:
        story_query = story_query.filter(Story.first_seen_at <= until)
    stories = story_query.all()

    located_features = []
    unlocated_items = []

    for story in stories:
        if story.location_precision is None:
            unlocated_items.append({"kind": "story", "id": story.id, "title": story.title})
            continue
        if aor_countries and story.location_country not in aor_countries:
            continue  # out of the requested AOR scope entirely - not unlocated, just elsewhere
        located_features.append(_story_feature(story, f"/stories/{story.id}"))

    orgs = db.query(Organization).all()
    for org in orgs:
        country = org.theatre.name if org.theatre else None
        if country is None or country not in _CENTROIDS:
            unlocated_items.append({"kind": "organization", "id": org.id, "title": org.name})
            continue
        if aor_countries and country not in aor_countries:
            continue
        located_features.append(_organization_feature(org, f"/organizations/{org.id}"))

    item_features, item_summary = _news_items(db, aor_countries, item_window_hours, item_limit, until)

    return {
        "located": {"type": "FeatureCollection", "features": located_features},
        # D-023: real news items, separate from the Story/Organization set and
        # its reconciliation, which they would otherwise swamp.
        "news_items": {"type": "FeatureCollection", "features": item_features, "summary": item_summary},
        "unlocated": {"count": len(unlocated_items), "items": unlocated_items},
        "reconciliation": {
            "located_count": len(located_features),
            "unlocated_count": len(unlocated_items),
            "total": len(located_features) + len(unlocated_items),
        },
    }
