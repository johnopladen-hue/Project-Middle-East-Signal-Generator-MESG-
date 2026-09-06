"""Signals / alerts — TDD §7, §4.5.

Release/suppress require admin (TDD §7: "review gate"). Release currently
only flips status to `released` — it does not yet dispatch real email/SMS,
since no EmailProvider/SmsProvider implementation exists (translation/
analysis/email/SMS providers are all still open decisions). Wiring real
delivery in is a follow-up once those decisions are made; the review gate
and its audit trail (status transitions) are real today.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Signal, SignalStatus, Story

router = APIRouter(prefix="/signals", tags=["signals"])


class SignalOut(BaseModel):
    id: int
    story_id: int
    story_title: str
    type: str
    severity: str
    is_imminent: bool
    status: str
    created_at: str

    model_config = {"from_attributes": True}


def _to_out(signal: Signal, story_title: str) -> SignalOut:
    return SignalOut(
        id=signal.id,
        story_id=signal.story_id,
        story_title=story_title,
        type=signal.type,
        severity=signal.severity,
        is_imminent=signal.is_imminent,
        status=signal.status,
        created_at=signal.created_at.isoformat(),
    )


@router.get("", response_model=list[SignalOut])
def list_signals(
    event_type: str | None = Query(None),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    is_imminent: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Signal, Story).join(Story, Signal.story_id == Story.id)
    if event_type:
        query = query.filter(Signal.type == event_type)
    if severity:
        query = query.filter(Signal.severity == severity)
    if status:
        query = query.filter(Signal.status == status)
    if is_imminent is not None:
        query = query.filter(Signal.is_imminent == is_imminent)

    return [_to_out(signal, story.title) for signal, story in query.order_by(Signal.created_at.desc()).all()]


@router.get("/{signal_id}", response_model=SignalOut)
def get_signal(signal_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(Signal, Story)
        .join(Story, Signal.story_id == Story.id)
        .filter(Signal.id == signal_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Signal not found")
    signal, story = row
    return _to_out(signal, story.title)


def _get_signal_or_404(signal_id: int, db: Session) -> Signal:
    signal = db.query(Signal).filter_by(id=signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    return signal


@router.post("/{signal_id}/release", response_model=SignalOut, dependencies=[Depends(require_admin)])
def release_signal(signal_id: int, db: Session = Depends(get_db)):
    signal = _get_signal_or_404(signal_id, db)
    signal.status = SignalStatus.RELEASED.value
    db.commit()
    story = db.query(Story).filter_by(id=signal.story_id).first()
    return _to_out(signal, story.title)


@router.post("/{signal_id}/suppress", response_model=SignalOut, dependencies=[Depends(require_admin)])
def suppress_signal(signal_id: int, db: Session = Depends(get_db)):
    signal = _get_signal_or_404(signal_id, db)
    signal.status = SignalStatus.SUPPRESSED.value
    db.commit()
    story = db.query(Story).filter_by(id=signal.story_id).first()
    return _to_out(signal, story.title)
