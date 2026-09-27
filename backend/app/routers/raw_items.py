"""Raw collected items — the Incoming page's API (D-018, I-5/S-5 of the
Ingest-Now and Approved-Sources orders). Real collected content never
leaves this machine (D-018) - this endpoint only ever serves it to the
Owner's own authenticated session, never republished elsewhere.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RawItem, Source

router = APIRouter(prefix="/raw-items", tags=["raw-items"])

# Matches pipeline.py's silence threshold - a source with no successful
# collection in this window counts as "returned nothing this run."
SILENCE_THRESHOLD = timedelta(hours=6)


class RawItemOut(BaseModel):
    id: int
    source_id: int
    source_name: str
    kind: str | None
    source_class: str | None
    pair_id: str | None
    designation_note: str | None
    verification_note: str | None
    fetched_at: datetime
    published_at: datetime | None
    original_lang: str
    original_text: str
    working_text: str | None
    url: str

    model_config = {"from_attributes": True}


class RawItemsPage(BaseModel):
    items: list[RawItemOut]
    total: int
    awaiting_translation: int
    silent_sources: list[str]


def _to_out(raw_item: RawItem, source: Source) -> RawItemOut:
    return RawItemOut(
        id=raw_item.id,
        source_id=source.id,
        source_name=source.name,
        kind=source.kind,
        source_class=source.source_class,
        pair_id=source.pair_id,
        designation_note=source.designation_note,
        verification_note=source.verification_note,
        fetched_at=raw_item.fetched_at,
        published_at=raw_item.published_at,
        original_lang=raw_item.original_lang,
        original_text=raw_item.original_text,
        working_text=raw_item.working_text,
        url=raw_item.url,
    )


@router.get("", response_model=RawItemsPage)
def list_raw_items(
    source_id: int | None = Query(None),
    language: str | None = Query(None),
    source_class: str | None = Query(None),
    kind: str | None = Query(None),
    since: datetime | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(RawItem, Source).join(Source, RawItem.source_id == Source.id)
    if source_id is not None:
        query = query.filter(RawItem.source_id == source_id)
    if language:
        query = query.filter(RawItem.original_lang == language)
    if source_class:
        query = query.filter(Source.source_class == source_class)
    if kind:
        query = query.filter(Source.kind == kind)
    if since:
        query = query.filter(RawItem.fetched_at >= since)

    total = query.count()
    rows = query.order_by(RawItem.fetched_at.desc()).offset(offset).limit(limit).all()
    items = [_to_out(raw_item, source) for raw_item, source in rows]

    awaiting_translation = (
        db.query(RawItem)
        .join(Source, RawItem.source_id == Source.id)
        .filter(RawItem.working_text.is_(None))
        .filter(Source.language != "en")
        .count()
    )

    cutoff = datetime.now(timezone.utc) - SILENCE_THRESHOLD
    silent_sources = [
        name
        for (name,) in db.query(Source.name)
        .filter(Source.active.is_(True))
        .filter(Source.kind.in_(["rss", "telegram"]))
        .filter((Source.last_seen_at.is_(None)) | (Source.last_seen_at < cutoff))
        .order_by(Source.name)
        .all()
    ]

    return RawItemsPage(
        items=items,
        total=total,
        awaiting_translation=awaiting_translation,
        silent_sources=silent_sources,
    )
