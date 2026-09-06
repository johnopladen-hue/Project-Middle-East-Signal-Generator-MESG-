"""Admin — TDD §7, §10. Everything here is admin-only (require_admin)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import Recipient, Settings, Source

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


# --- Sources -----------------------------------------------------------


class SourceIn(BaseModel):
    name: str
    url: str
    language: str
    dialect: str | None = None
    type: str
    region: str | None = None
    credibility_prior: float = 0.5
    active: bool = True


class SourcePatch(BaseModel):
    name: str | None = None
    url: str | None = None
    language: str | None = None
    dialect: str | None = None
    type: str | None = None
    region: str | None = None
    credibility_prior: float | None = None
    active: bool | None = None


class SourceOut(BaseModel):
    id: int
    name: str
    url: str
    language: str
    dialect: str | None
    type: str
    region: str | None
    credibility_prior: float
    last_seen_at: datetime | None
    active: bool

    model_config = {"from_attributes": True}


@router.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.name).all()


@router.post("/sources", response_model=SourceOut, status_code=201)
def create_source(payload: SourceIn, db: Session = Depends(get_db)):
    source = Source(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.patch("/sources/{source_id}", response_model=SourceOut)
def update_source(source_id: int, payload: SourcePatch, db: Session = Depends(get_db)):
    source = db.query(Source).filter_by(id=source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(source, field, value)
    db.commit()
    db.refresh(source)
    return source


# --- Recipients ----------------------------------------------------------


class RecipientIn(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    channels: list[str] = []
    active: bool = False
    approved_by: str | None = None


class RecipientPatch(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    channels: list[str] | None = None
    active: bool | None = None
    approved_by: str | None = None


class RecipientOut(BaseModel):
    id: int
    name: str
    email: str | None
    phone: str | None
    channels: list[str]
    active: bool
    approved_by: str | None

    model_config = {"from_attributes": True}


@router.get("/recipients", response_model=list[RecipientOut])
def list_recipients(db: Session = Depends(get_db)):
    return db.query(Recipient).order_by(Recipient.name).all()


@router.post("/recipients", response_model=RecipientOut, status_code=201)
def create_recipient(payload: RecipientIn, db: Session = Depends(get_db)):
    recipient = Recipient(**payload.model_dump())
    db.add(recipient)
    db.commit()
    db.refresh(recipient)
    return recipient


@router.patch("/recipients/{recipient_id}", response_model=RecipientOut)
def update_recipient(recipient_id: int, payload: RecipientPatch, db: Session = Depends(get_db)):
    recipient = db.query(Recipient).filter_by(id=recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(recipient, field, value)
    db.commit()
    db.refresh(recipient)
    return recipient


# --- Settings (singleton) -------------------------------------------------


class SettingsOut(BaseModel):
    values: dict


def _get_or_create_settings(db: Session) -> Settings:
    settings = db.query(Settings).filter_by(id=1).first()
    if not settings:
        settings = Settings(id=1, values={})
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/settings", response_model=SettingsOut)
def get_settings(db: Session = Depends(get_db)):
    return SettingsOut(values=_get_or_create_settings(db).values)


@router.patch("/settings", response_model=SettingsOut)
def update_settings(payload: dict, db: Session = Depends(get_db)):
    settings = _get_or_create_settings(db)
    settings.values = {**settings.values, **payload}
    db.commit()
    return SettingsOut(values=settings.values)
