"""Recipient summary — backs the release blast-radius confirmation (UI-spec
§5.3). Not in TDD §7's table; full CRUD (`/admin/recipients`) lands in
Order 10. Admin-only: recipient counts are derived from PII (TDD §10)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Recipient

router = APIRouter(prefix="/recipients", tags=["recipients"])


class RecipientSummary(BaseModel):
    active_count: int
    email_count: int
    sms_count: int


@router.get("/summary", response_model=RecipientSummary, dependencies=[Depends(require_admin)])
def recipients_summary(db: Session = Depends(get_db)):
    active = db.query(Recipient).filter_by(active=True).all()
    email_count = sum(1 for r in active if "email" in (r.channels or []))
    sms_count = sum(1 for r in active if "sms" in (r.channels or []))
    return RecipientSummary(active_count=len(active), email_count=email_count, sms_count=sms_count)
