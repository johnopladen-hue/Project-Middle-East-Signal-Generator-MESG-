"""Pipeline status - backs the PipelineStatusStrip (UI-spec sec4/sec6).

Not part of the TDD sec7 API surface table; added because Order 4 of the
UI-spec orders requires this component to have real data to render.
Source-liveness itself is TDD sec4.1 ("a source that goes unexpectedly
silent is itself a signal").

Since U-3 (D-019 scheduler & runtime) the run fields are real, read from
`IngestRun`: per-job last run, collection gaps over the last 7 days
(D-019 requires them shown, not hidden), the pause flag, and whether a
scheduler is running in this process.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import scheduler as sched
from app.database import get_db
from app.llm_budget import caps as llm_caps
from app.llm_budget import current_spend
from app.models import IngestRun, Source

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

SILENCE_THRESHOLD = timedelta(hours=6)


class JobStatus(BaseModel):
    job: str
    interval_minutes: int
    last_run_at: str | None  # newest run of any status
    last_status: str | None
    last_success_at: str | None


class CollectionGap(BaseModel):
    job: str
    start: str
    end: str | None  # null = still open
    ongoing: bool


class PipelineStatus(BaseModel):
    last_run_at: str | None  # newest successful run of any job
    silent_source_count: int
    llm_daily_spend_usd: float
    llm_monthly_spend_usd: float
    llm_daily_cap_usd: float
    llm_monthly_cap_usd: float
    jobs: list[JobStatus]
    collection_gaps: list[CollectionGap]
    paused: bool
    scheduler_running: bool


def _iso(value: datetime | None) -> str | None:
    return sched.as_utc(value).isoformat() if value else None


@router.get("/status", response_model=PipelineStatus)
def status(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    cutoff = now - SILENCE_THRESHOLD
    silent_count = (
        db.query(Source)
        .filter(Source.active.is_(True))
        .filter((Source.last_seen_at.is_(None)) | (Source.last_seen_at < cutoff))
        .count()
    )
    daily_cap, monthly_cap = llm_caps(db)
    daily_spend, monthly_spend = current_spend(db)

    jobs: list[JobStatus] = []
    gaps: list[CollectionGap] = []
    for job, interval in sched.JOB_INTERVALS.items():
        newest = db.query(IngestRun).filter(IngestRun.job == job).order_by(IngestRun.started_at.desc()).first()
        jobs.append(
            JobStatus(
                job=job,
                interval_minutes=int(interval.total_seconds() // 60),
                last_run_at=_iso(newest.started_at) if newest else None,
                last_status=newest.status if newest else None,
                last_success_at=_iso(sched.last_success_at(db, job)),
            )
        )
        gaps.extend(
            CollectionGap(job=g.job, start=_iso(g.start), end=_iso(g.end), ongoing=g.ongoing)
            for g in sched.job_gaps(db, job, now)
        )

    successes = [j.last_success_at for j in jobs if j.last_success_at]
    return PipelineStatus(
        last_run_at=max(successes) if successes else None,
        silent_source_count=silent_count,
        llm_daily_spend_usd=daily_spend,
        llm_monthly_spend_usd=monthly_spend,
        llm_daily_cap_usd=daily_cap,
        llm_monthly_cap_usd=monthly_cap,
        jobs=jobs,
        collection_gaps=gaps,
        paused=sched.is_paused(db),
        scheduler_running=sched.is_running(),
    )
