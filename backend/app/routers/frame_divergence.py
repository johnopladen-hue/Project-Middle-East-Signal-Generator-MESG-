"""Frame-divergence notes - the map's "U.S. lens" label made a recordable
feature (D-015, O-9): where in-region self-conception diverges from the
AOR frame. Minimal first cut - the systematic divergence overlay is
deferred (MESG-Map-Interface-Orders-v0.1.md §8)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import FrameDivergenceNote, User

router = APIRouter(prefix="/frame-divergence-notes", tags=["frame-divergence"])


class NoteIn(BaseModel):
    scope_type: str
    scope_id: str
    text: str


class NoteOut(BaseModel):
    id: int
    scope_type: str
    scope_id: str
    text: str
    created_at: str
    created_by: str | None

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, row: FrameDivergenceNote) -> "NoteOut":
        return cls(
            id=row.id,
            scope_type=row.scope_type,
            scope_id=row.scope_id,
            text=row.text,
            created_at=row.created_at.isoformat(),
            created_by=row.created_by,
        )


@router.get("", response_model=list[NoteOut])
def list_notes(scope_type: str = Query(...), scope_id: str = Query(...), db: Session = Depends(get_db)):
    rows = (
        db.query(FrameDivergenceNote)
        .filter_by(scope_type=scope_type, scope_id=scope_id)
        .order_by(FrameDivergenceNote.created_at.desc())
        .all()
    )
    return [NoteOut.from_row(r) for r in rows]


@router.post("", response_model=NoteOut, status_code=201)
def create_note(payload: NoteIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = FrameDivergenceNote(
        scope_type=payload.scope_type,
        scope_id=payload.scope_id,
        text=payload.text,
        created_by=user.username,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return NoteOut.from_row(row)
