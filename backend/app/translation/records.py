"""What counts as translated, pending, or given up on (D-016, U-2).

One definition, shared by the translation job (what to pick up next) and
`GET /raw-items` (the `awaiting_translation` / `translation_failed` counts),
so the number on screen is the number the job will actually work through.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Query, Session

from app.models import RawItem, TranslationRecord, TranslationStatus

SUCCESS_STATUSES = (TranslationStatus.OK.value, TranslationStatus.OK_TRUNCATED.value)

# A failed item is retried until it has this many failed attempts in total,
# then left as `translation_failed` - visible, never retried forever.
MAX_ATTEMPTS = 3


def _translated_ids():
    return select(TranslationRecord.raw_item_id).where(TranslationRecord.status.in_(SUCCESS_STATUSES))


def _given_up_ids():
    return (
        select(TranslationRecord.raw_item_id)
        .where(TranslationRecord.status == TranslationStatus.FAILED.value)
        .group_by(TranslationRecord.raw_item_id)
        .having(func.count() >= MAX_ATTEMPTS)
    )


def pending_items(db: Session) -> Query:
    """Non-English items with no successful record and fewer than
    MAX_ATTEMPTS failures - newest first, so today's items are read in
    English before the backlog."""
    return (
        db.query(RawItem)
        .filter(RawItem.original_lang != "en")
        .filter(~RawItem.id.in_(_translated_ids()))
        .filter(~RawItem.id.in_(_given_up_ids()))
        .order_by(func.coalesce(RawItem.published_at, RawItem.fetched_at).desc(), RawItem.id.desc())
    )


def failed_items(db: Session) -> Query:
    """Items that used up every attempt without a success."""
    return (
        db.query(RawItem)
        .filter(RawItem.original_lang != "en")
        .filter(~RawItem.id.in_(_translated_ids()))
        .filter(RawItem.id.in_(_given_up_ids()))
    )


def reconcile(db: Session, raw_item_ids: list[int] | None = None) -> tuple[list[int], list[int]]:
    """Two paths to one fact (Keel P11): `working_text` and a successful
    TranslationRecord must agree. Returns (items with working_text but no
    successful record, items with a successful record but no working_text).
    Both empty means reconciled."""
    items = db.query(RawItem)
    if raw_item_ids is not None:
        items = items.filter(RawItem.id.in_(raw_item_ids))

    text_without_record = [
        item_id
        for (item_id,) in items.filter(RawItem.working_text.is_not(None))
        .filter(~RawItem.id.in_(_translated_ids()))
        .with_entities(RawItem.id)
    ]
    record_without_text = [
        item_id
        for (item_id,) in items.filter(RawItem.working_text.is_(None))
        .filter(RawItem.id.in_(_translated_ids()))
        .with_entities(RawItem.id)
    ]
    return text_without_record, record_without_text
