"""Pipeline status — backs the PipelineStatusStrip (UI-spec sec4/sec6).

Not part of the TDD sec7 API surface table; added because Order 4 of the
UI-spec orders requires this component to have real data to render.
Source-liveness itself is TDD sec4.1 ("a source that goes unexpectedly
silent is itself a signal"); no scheduler has run yet (that's Phase 1
pipeline work, not built here), so last_run_at is honestly null until
one has.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Source

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

SILENCE_THRESHOLD = timedelta(hours=6)


class PipelineStatus(BaseModel):
    last_run_at: str | None
    silent_source_count: int


@router.get("/status", response_model=PipelineStatus)
def status(db: Session = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - SILENCE_THRESHOLD
    silent_count = (
        db.query(Source)
        .filter(Source.active.is_(True))
        .filter((Source.last_seen_at.is_(None)) | (Source.last_seen_at < cutoff))
        .count()
    )
    return PipelineStatus(last_run_at=None, silent_source_count=silent_count)
