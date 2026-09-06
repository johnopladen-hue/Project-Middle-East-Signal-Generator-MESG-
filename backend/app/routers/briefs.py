"""Briefs — TDD §7, §4.6.

`Brief.content_json` is the rendered snapshot the pipeline produces each
cycle (facts/analysis/grade per story, TDD §6) — this router serves it
as-is; it does not itself join Story/Analysis/RawItem, since nothing has
written those yet (no ingestion pipeline exists — see documents/decisions.md
open list for translation/analysis provider). Once that pipeline is built,
it is what populates content_json; this API surface does not change.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Brief

router = APIRouter(prefix="/briefs", tags=["briefs"])


class BriefSummary(BaseModel):
    id: int
    type: str
    for_date: datetime

    model_config = {"from_attributes": True}


class BriefDetail(BaseModel):
    id: int
    type: str
    for_date: datetime
    content: dict
    released_at: datetime | None

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_brief(cls, brief: Brief) -> "BriefDetail":
        return cls(
            id=brief.id,
            type=brief.type,
            for_date=brief.for_date,
            content=brief.content_json,
            released_at=brief.released_at,
        )


@router.get("", response_model=list[BriefSummary])
def list_briefs(type: str = Query(...), db: Session = Depends(get_db)):
    briefs = db.query(Brief).filter_by(type=type).order_by(Brief.for_date.desc()).all()
    return briefs


@router.get("/{brief_id}", response_model=BriefDetail)
def get_brief(brief_id: int, db: Session = Depends(get_db)):
    brief = db.query(Brief).filter_by(id=brief_id).first()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    return BriefDetail.from_orm_brief(brief)
