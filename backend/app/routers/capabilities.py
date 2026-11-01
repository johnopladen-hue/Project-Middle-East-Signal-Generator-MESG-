"""What MESG actually does today, read from data (U-5, the honesty banner).

Every flag is derived from rows that exist, never from configuration or
hard-coded copy, so the banner changes on its own as each track lands: the
first real Analyst output flips `graded_analysis`, the first real daily
brief flips `daily_brief`, the first sent delivery flips `alert_delivery`.

"Real" means not the dev seed: `app.dev_seed` tags every analysis and brief
it writes with `[SYNTHETIC — DEV SEED]`, and `synthetic_data_present` says
so, so seeded briefs on the Dashboard are never mistaken for analysis.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import exists
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis, Brief, DeliveryLog, DeliveryStatus, RawItem, Source, TranslationRecord
from app.translation.records import SUCCESS_STATUSES

router = APIRouter(tags=["capabilities"])

# ASCII prefix of app.dev_seed.TAG: JSON columns store non-ASCII escaped, so the em dash can't be matched there.
SYNTHETIC_PREFIX = "[SYNTHETIC"


class Capabilities(BaseModel):
    rss: bool
    telegram: bool
    triage_translation: bool
    graded_analysis: bool
    daily_brief: bool
    alert_delivery: bool
    synthetic_data_present: bool


def _collected(db: Session, kind: str) -> bool:
    return db.query(exists().where(RawItem.source_id == Source.id, Source.kind == kind)).scalar()


def _is_synthetic_brief(brief: Brief) -> bool:
    return SYNTHETIC_PREFIX in json.dumps(brief.content_json or {})


def compute_capabilities(db: Session) -> Capabilities:
    real_analysis = db.query(exists().where(~Analysis.analysis_text.startswith(SYNTHETIC_PREFIX))).scalar()
    synthetic_analysis = db.query(exists().where(Analysis.analysis_text.startswith(SYNTHETIC_PREFIX))).scalar()

    daily = db.query(Brief).filter(Brief.type == "daily").all()
    real_daily = any(not _is_synthetic_brief(b) for b in daily)
    synthetic_brief = any(_is_synthetic_brief(b) for b in db.query(Brief).all())

    return Capabilities(
        rss=_collected(db, "rss"),
        telegram=_collected(db, "telegram"),
        triage_translation=db.query(exists().where(TranslationRecord.status.in_(SUCCESS_STATUSES))).scalar(),
        graded_analysis=real_analysis,
        daily_brief=real_daily,
        alert_delivery=db.query(exists().where(DeliveryLog.status == DeliveryStatus.SENT.value)).scalar(),
        synthetic_data_present=synthetic_analysis or synthetic_brief,
    )


@router.get("/capabilities", response_model=Capabilities)
def capabilities(db: Session = Depends(get_db)):
    return compute_capabilities(db)
