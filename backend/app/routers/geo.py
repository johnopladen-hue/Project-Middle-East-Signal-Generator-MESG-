"""Geo endpoint - located items (stories/signals share a Story's location;
organizations) as GeoJSON, scoped by AOR + time window + D-008 source scope
as three separate filters (D-014, O-7). Unknown-location items are a
separate, visible set - never a fake pin (Principle 11)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AorMembership, Organization, Story

router = APIRouter(prefix="/geo", tags=["geo"])

_CENTROIDS_PATH = Path(__file__).resolve().parent.parent / "geo" / "country_centroids.json"
_CENTROIDS = json.loads(_CENTROIDS_PATH.read_text(encoding="utf-8"))

# D-008: the only source scope this v1 register actually has. Accepted as a
# real filter parameter (not silently ignored) rather than pretended-away;
# there is nothing else to filter to yet.
SUPPORTED_SCOPES = ("v1",)


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

    return {
        "located": {"type": "FeatureCollection", "features": located_features},
        "unlocated": {"count": len(unlocated_items), "items": unlocated_items},
        "reconciliation": {
            "located_count": len(located_features),
            "unlocated_count": len(unlocated_items),
            "total": len(located_features) + len(unlocated_items),
        },
    }
