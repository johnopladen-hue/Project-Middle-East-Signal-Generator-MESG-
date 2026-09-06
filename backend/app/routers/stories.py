"""Story detail — TDD §7, §8.

Unlike Brief (a rendered JSON snapshot), Story/Analysis/SourceAssessment/
Divergence are genuine relational tables (TDD §6) — this router actually
joins them. RawItems referenced by facts_json's raw_item_ids are resolved
into a lookup map, same shape as Brief's, so the frontend's resolveRawItem
works unchanged across both.

Known simplification (see documents/findings.md): Analysis has no stored
has_corroborating_artefact column. It's derived here as probability_grade
>= 4, since the grading cap (backend/app/grading.py) guarantees nothing
above 3 is ever stored without one. This is not reversible for grades 1-3
(genuinely doubtful/false vs. merely uncorroborated look the same); revisit
once the analysis engine is real and can persist the flag directly.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis, Divergence, RawItem, Source, SourceAssessment, Story, StoryItem

router = APIRouter(prefix="/stories", tags=["stories"])


class DivergenceOut(BaseModel):
    in_region_summary: str
    english_media_summary: str
    divergence_points: list[str]
    convergence_points: list[str]


class SourceAssessmentOut(BaseModel):
    source_id: int
    source_name: str
    access_level: str
    reliability: float
    rationale: str


class StoryDetail(BaseModel):
    id: int
    title: str
    event_type: str | None
    status: str
    facts: list[dict]
    analysis_text: str | None
    probability_grade: int | None
    contrary_evidence: str | None
    has_corroborating_artefact: bool
    source_assessments: list[SourceAssessmentOut]
    divergence: DivergenceOut | None
    raw_items: dict
    timeline: list[int]


def _resolve_raw_item(raw_item: RawItem) -> dict:
    return {
        "id": raw_item.id,
        "source_name": raw_item.source.name,
        "access_level": None,
        "url": raw_item.url,
        "fetched_at": raw_item.fetched_at.isoformat() if raw_item.fetched_at else None,
        "original_lang": raw_item.original_lang,
        "content_hash": raw_item.content_hash,
        "original_text": raw_item.original_text,
        "working_text": raw_item.working_text,
    }


@router.get("/{story_id}", response_model=StoryDetail)
def get_story(story_id: int, db: Session = Depends(get_db)):
    story = db.query(Story).filter_by(id=story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    analysis = (
        db.query(Analysis)
        .filter_by(story_id=story_id)
        .order_by(Analysis.generated_at.desc())
        .first()
    )
    facts = analysis.facts_json if analysis else []
    probability_grade = analysis.probability_grade if analysis else None
    has_corroborating_artefact = probability_grade is not None and probability_grade >= 4

    assessments = []
    if analysis:
        rows = (
            db.query(SourceAssessment, Source)
            .join(Source, SourceAssessment.source_id == Source.id)
            .filter(SourceAssessment.analysis_id == analysis.id)
            .all()
        )
        assessments = [
            SourceAssessmentOut(
                source_id=source.id,
                source_name=source.name,
                access_level=assessment.access_level,
                reliability=assessment.reliability,
                rationale=assessment.rationale,
            )
            for assessment, source in rows
        ]

    divergence_row = db.query(Divergence).filter_by(story_id=story_id).first()
    divergence = (
        DivergenceOut(
            in_region_summary=divergence_row.in_region_summary,
            english_media_summary=divergence_row.english_media_summary,
            divergence_points=divergence_row.divergence_points,
            convergence_points=divergence_row.convergence_points,
        )
        if divergence_row
        else None
    )

    referenced_ids = {rid for fact in facts for rid in fact.get("raw_item_ids", [])}
    timeline_ids = [
        row.raw_item_id
        for row in db.query(StoryItem)
        .filter_by(story_id=story_id)
        .join(RawItem, StoryItem.raw_item_id == RawItem.id)
        .order_by(RawItem.fetched_at.asc())
        .all()
    ]
    all_ids = referenced_ids | set(timeline_ids)

    raw_items = {}
    if all_ids:
        for raw_item in db.query(RawItem).filter(RawItem.id.in_(all_ids)).all():
            raw_items[str(raw_item.id)] = _resolve_raw_item(raw_item)

    return StoryDetail(
        id=story.id,
        title=story.title,
        event_type=story.event_type,
        status=story.status,
        facts=facts,
        analysis_text=analysis.analysis_text if analysis else None,
        probability_grade=probability_grade,
        contrary_evidence=analysis.contrary_evidence if analysis else None,
        has_corroborating_artefact=has_corroborating_artefact,
        source_assessments=assessments,
        divergence=divergence,
        raw_items=raw_items,
        timeline=timeline_ids,
    )
