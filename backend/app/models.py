"""Core data model — TDD-001 §6.

SQLAlchemy 2.0 declarative models for the entities MESG stores. Provenance is
structural, not a convention: RawItem is the only entity a Story's Analysis
may cite, and Analysis rows carry facts_json entries that name the RawItem
each fact came from (TDD Design Principle 1, "Provenance-first").
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class SignalStatus(str, enum.Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    RELEASED = "released"
    SUPPRESSED = "suppressed"


class BriefType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class DeliveryChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"


class DeliveryStatus(str, enum.Enum):
    SENT = "sent"
    FAILED = "failed"
    SUPPRESSED = "suppressed"  # blocked by whitelist enforcement


class SourceAccessLevel(str, enum.Enum):
    DIRECT = "direct"
    ONE_STEP = "one_step"
    AGGREGATOR = "aggregator"
    COMMENTARY = "commentary"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="analyst")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Recipient(Base):
    """The delivery whitelist. PII — see TDD §10 and Keel Principle 10 (Private tripwire)."""

    __tablename__ = "recipients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    channels: Mapped[list[str]] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(1024))
    language: Mapped[str] = mapped_column(String(64))
    dialect: Mapped[str | None] = mapped_column(String(64), nullable=True)
    type: Mapped[str] = mapped_column(String(32))  # rss | scraper | api | discussion
    region: Mapped[str | None] = mapped_column(String(64), nullable=True)
    credibility_prior: Mapped[float] = mapped_column(Float, default=0.5)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class RawItem(Base):
    """The artefact of record. Nothing is analyzed that has no fetch record (TDD §4.1)."""

    __tablename__ = "raw_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    original_lang: Mapped[str] = mapped_column(String(64))
    original_text: Mapped[str] = mapped_column(Text)
    working_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1024))
    content_hash: Mapped[str] = mapped_column(String(64), index=True)

    source: Mapped[Source] = relationship()


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(512))
    event_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    last_updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)


class StoryItem(Base):
    __tablename__ = "story_items"

    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), primary_key=True)
    raw_item_id: Mapped[int] = mapped_column(ForeignKey("raw_items.id"), primary_key=True)


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    facts_json: Mapped[list[dict]] = mapped_column(JSON, default=list)
    analysis_text: Mapped[str] = mapped_column(Text)
    probability_grade: Mapped[int] = mapped_column(Integer)
    contrary_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    reviewed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)


class SourceAssessment(Base):
    __tablename__ = "source_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(ForeignKey("analyses.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    access_level: Mapped[str] = mapped_column(String(32))
    reliability: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(Text)


class Divergence(Base):
    __tablename__ = "divergences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    in_region_summary: Mapped[str] = mapped_column(Text)
    english_media_summary: Mapped[str] = mapped_column(Text)
    divergence_points: Mapped[list[str]] = mapped_column(JSON, default=list)
    convergence_points: Mapped[list[str]] = mapped_column(JSON, default=list)


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"))
    type: Mapped[str] = mapped_column(String(64))
    severity: Mapped[str] = mapped_column(String(32))
    is_imminent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    status: Mapped[str] = mapped_column(String(32), default=SignalStatus.NEW.value)


class Brief(Base):
    __tablename__ = "briefs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(16))
    for_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    content_json: Mapped[dict] = mapped_column(JSON, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    released_by: Mapped[str | None] = mapped_column(String(64), nullable=True)


class DeliveryLog(Base):
    """Provenance for every send (TDD §4.7). Every attempt is logged, sent or not."""

    __tablename__ = "delivery_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("recipients.id"))
    channel: Mapped[str] = mapped_column(String(16))
    ref_type: Mapped[str] = mapped_column(String(32))
    ref_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class Settings(Base):
    """Thresholds/cadence (TDD §5, §7 admin/settings). Not in the TDD §6
    entity table — added as a singleton row since Admin needs somewhere
    real to read/write; actual threshold/cadence fields are still open
    (documents/decisions.md: scheduler mechanism), so this holds a free-form
    JSON bag rather than named columns that would need picking now."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    values: Mapped[dict] = mapped_column(JSON, default=dict)
