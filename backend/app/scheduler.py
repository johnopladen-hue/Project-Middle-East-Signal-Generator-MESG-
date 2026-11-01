"""In-app scheduler for continuous ingestion (D-019 scheduler & runtime, U-3).

Three jobs run inside the FastAPI backend on the Owner's PC:

    rss        every 30 min   app.ingest.run_rss
    telegram   every 15 min   app.ingest.run_telegram
    translate  every  5 min   app.translation.run.translate_pending (NLLB triage, D-016)

Each job writes one `IngestRun` row per run, with `max_instances=1` and
`coalesce=True`. On start, a job whose last successful run is older than its
interval (or which has never run) runs immediately. That is D-019's
catch-up-after-wake, done explicitly in `initial_next_run` instead of relying
on APScheduler's misfire grace, which knows nothing about runs from before
this process started.

`/pipeline/status` reads `IngestRun` back through `last_runs` and
`collection_gaps`, so a missed run is visible in the UI, never hidden (D-019).
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import IngestRun, IngestRunStatus, Settings

logger = logging.getLogger("mesg.scheduler")

Clock = Callable[[], datetime]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    """SQLite hands `DateTime(timezone=True)` back naive; every value MESG
    writes is UTC, so a naive value read back is UTC."""
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


JOB_INTERVALS: dict[str, timedelta] = {
    "rss": timedelta(minutes=30),
    "telegram": timedelta(minutes=15),
    "translate": timedelta(minutes=5),
}

# A run that ended in one of these counts as "the job ran". `partial` counts
# because the job did collect; `failed` and `skipped_paused` do not.
SUCCESS_STATUSES = (IngestRunStatus.OK.value, IngestRunStatus.PARTIAL.value)

# Two consecutive successful runs further apart than this multiple of the
# job's interval are a collection gap. STRICT: exactly 2x is NOT a gap (one
# run late by a full interval is tolerated, since a long Telegram run or a
# coalesced misfire can push the next run back that far); anything over 2x is.
GAP_MULTIPLE = 2
GAP_LOOKBACK = timedelta(days=7)

# Caps one translate run at roughly 10 minutes at the measured 0.79 items/s
# (findings.md, 2026-10-11 U-2 backlog run), so a pause takes effect and
# IngestRun rows stay regular. Steady state is ~10 items per 5-minute run;
# the cap only bites while catching up after the PC was off, newest first.
TRANSLATE_LIMIT_PER_RUN = 500

LOCK_PATH = Path(__file__).resolve().parent.parent / "data" / "scheduler.lock"
ENV_FLAG = "MESG_SCHEDULER"


# --- Pause flag (Settings.values["ingest_paused"], existing JSON column) ---


def is_paused(db: Session) -> bool:
    settings = db.query(Settings).filter_by(id=1).first()
    return bool(settings and (settings.values or {}).get("ingest_paused"))


def set_paused(db: Session, paused: bool) -> None:
    settings = db.query(Settings).filter_by(id=1).first()
    if settings is None:
        settings = Settings(id=1, values={})
        db.add(settings)
    # Reassign rather than mutate: a plain JSON column does not track in-place changes.
    settings.values = {**(settings.values or {}), "ingest_paused": paused}
    db.commit()


# --- Job outcomes -> IngestRun --------------------------------------------


@dataclass
class JobOutcome:
    items_new: int = 0
    sources_total: int = 0
    sources_failed: int = 0
    notes: str | None = None
    failed: bool = False  # the job could not do its work at all (e.g. no translator)

    @property
    def status(self) -> IngestRunStatus:
        if self.failed:
            return IngestRunStatus.FAILED
        if self.sources_total and self.sources_failed == self.sources_total:
            return IngestRunStatus.FAILED
        if self.sources_failed:
            return IngestRunStatus.PARTIAL
        return IngestRunStatus.OK


def _collection_outcome(results) -> JobOutcome:
    failed = [r for r in results if r.error]
    notes = [f"{r.source_name}: {r.error}" for r in failed]
    extras = {
        name: sum(getattr(r, name, 0) for r in results)
        for name in ("skipped_media_only", "gap_possible", "stale_snapshot")
    }
    flagged = {name: n for name, n in extras.items() if n}
    if flagged:
        notes.insert(0, " ".join(f"{name}={n}" for name, n in flagged.items()))
    return JobOutcome(
        items_new=sum(r.new for r in results),
        sources_total=len(results),
        sources_failed=len(failed),
        notes="\n".join(notes) or None,
    )


def run_rss_job(db: Session, _ctx: "SchedulerContext") -> JobOutcome:
    from app.ingest import run_rss

    return _collection_outcome(run_rss(db))


def run_telegram_job(db: Session, _ctx: "SchedulerContext") -> JobOutcome:
    from app.ingest import run_telegram

    return _collection_outcome(run_telegram(db))


def run_translate_job(db: Session, ctx: "SchedulerContext") -> JobOutcome:
    from app.translation.run import translate_pending

    translator = ctx.get_translator()
    if translator is None:
        return JobOutcome(failed=True, notes=ctx.translator_error)
    result = translate_pending(db, translator, limit=TRANSLATE_LIMIT_PER_RUN)
    ok = result.by_status.get("ok", 0) + result.by_status.get("ok_truncated", 0)
    failed = result.by_status.get("failed", 0)
    notes = " ".join(f"{s}={result.by_status.get(s, 0)}" for s in ("ok", "ok_truncated", "failed"))
    # Translation has no "sources"; a run where every attempt failed is a failed run.
    return JobOutcome(items_new=ok, notes=notes, failed=bool(failed and not ok))


JobRunner = Callable[[Session, "SchedulerContext"], JobOutcome]

DEFAULT_RUNNERS: dict[str, JobRunner] = {
    "rss": run_rss_job,
    "telegram": run_telegram_job,
    "translate": run_translate_job,
}


@dataclass
class SchedulerContext:
    """What a job needs besides its DB session. The translator is built once
    and kept, because loading the NLLB model takes seconds; a missing model
    is retried on the next run, so installing it later needs no restart."""

    session_factory: Callable[[], Session]
    clock: Clock = utcnow
    translator_factory: Callable[[], object] | None = None
    translator: object | None = None
    translator_error: str | None = None

    def get_translator(self):
        if self.translator is not None:
            return self.translator
        factory = self.translator_factory or _default_translator_factory
        try:
            self.translator = factory()
            self.translator_error = None
        except Exception as exc:  # NllbModelMissing, or ctranslate2 not installed
            self.translator_error = f"{type(exc).__name__}: {exc}"
            logger.error("Translate job cannot run: %s", self.translator_error)
        return self.translator


def _default_translator_factory():
    from app.translation.nllb import NllbTranslator

    return NllbTranslator()


def run_job(job: str, ctx: SchedulerContext, runners: dict[str, JobRunner] | None = None) -> IngestRun:
    """Run one job and write its IngestRun row. Never raises: a job that
    throws is recorded as `failed` with the exception in `notes`."""
    runner = (runners or DEFAULT_RUNNERS)[job]
    with ctx.session_factory() as db:
        run = IngestRun(job=job, started_at=ctx.clock(), status=IngestRunStatus.FAILED.value)
        if is_paused(db):
            run.status = IngestRunStatus.SKIPPED_PAUSED.value
            run.finished_at = ctx.clock()
            db.add(run)
            db.commit()
            db.refresh(run)
            db.expunge(run)
            return run
        try:
            outcome = runner(db, ctx)
        except Exception as exc:
            logger.exception("Scheduled job %s raised", job)
            db.rollback()
            outcome = JobOutcome(failed=True, notes=f"{type(exc).__name__}: {exc}")
        run.status = outcome.status.value
        run.items_new = outcome.items_new
        run.sources_failed = outcome.sources_failed
        run.notes = outcome.notes
        run.finished_at = ctx.clock()
        db.add(run)
        db.commit()
        db.refresh(run)
        db.expunge(run)
        logger.info("Job %s: %s, %d new, %d sources failed", job, run.status, run.items_new, run.sources_failed)
        return run


# --- Reading IngestRun back -------------------------------------------------


def last_success_at(db: Session, job: str) -> datetime | None:
    row = (
        db.query(IngestRun.started_at)
        .filter(IngestRun.job == job, IngestRun.status.in_(SUCCESS_STATUSES))
        .order_by(IngestRun.started_at.desc())
        .first()
    )
    return as_utc(row[0]) if row else None


def initial_next_run(last_success: datetime | None, interval: timedelta, now: datetime) -> datetime:
    """Catch-up after wake (D-019): never run, or last success older than one
    interval -> run now. Otherwise keep the cadence from the last success."""
    if last_success is None or now - last_success >= interval:
        return now
    return last_success + interval


@dataclass
class Gap:
    job: str
    start: datetime
    end: datetime | None  # None = still open: no successful run since `start`

    @property
    def ongoing(self) -> bool:
        return self.end is None


def collection_gaps(
    success_times: list[datetime], job: str, interval: timedelta, now: datetime, lookback: timedelta = GAP_LOOKBACK
) -> list[Gap]:
    """Gaps between consecutive successful runs longer than GAP_MULTIPLE x
    interval (strict), within `lookback`. If the newest success is itself
    older than that, the gap is still open (`end=None`): this is what makes a
    scheduler that never started visible in the status strip.

    A paused stretch is reported as a gap too: nothing was collected, and the
    reader of a brief needs to know that whatever the reason."""
    threshold = interval * GAP_MULTIPLE
    window_start = now - lookback
    times = sorted(as_utc(t) for t in success_times)
    gaps: list[Gap] = []
    for earlier, later in zip(times, times[1:]):
        if later >= window_start and later - earlier > threshold:
            gaps.append(Gap(job, earlier, later))
    if times and now - times[-1] > threshold:
        gaps.append(Gap(job, times[-1], None))
    return gaps


def job_gaps(db: Session, job: str, now: datetime) -> list[Gap]:
    interval = JOB_INTERVALS[job]
    # One run before the window, so a gap that started before it is still found.
    rows = (
        db.query(IngestRun.started_at)
        .filter(IngestRun.job == job, IngestRun.status.in_(SUCCESS_STATUSES))
        .filter(IngestRun.started_at >= now - GAP_LOOKBACK - interval * GAP_MULTIPLE)
        .order_by(IngestRun.started_at)
        .all()
    )
    return collection_gaps([r[0] for r in rows], job, interval, now)


# --- Starting the scheduler -------------------------------------------------


@dataclass
class RunningScheduler:
    scheduler: object
    lock: object
    ctx: SchedulerContext
    next_runs: dict[str, datetime] = field(default_factory=dict)

    def shutdown(self) -> None:
        try:
            self.scheduler.shutdown(wait=False)
        finally:
            self.lock.release()


_running: RunningScheduler | None = None


def is_running() -> bool:
    return _running is not None


def start_scheduler(
    session_factory: Callable[[], Session],
    *,
    clock: Clock = utcnow,
    lock_path: Path = LOCK_PATH,
    env: dict | None = None,
    runners: dict[str, JobRunner] | None = None,
    translator_factory: Callable[[], object] | None = None,
    hold_jobs: bool = False,
) -> RunningScheduler | None:
    """Start the background scheduler, or return None if a guard says no.

    Guard 1, opt-in by environment: starts only when MESG_SCHEDULER=1. The
    test suite never sets it, and neither does scripts/dev.py. This guard
    stands aside when the variable is missing, which is acceptable ONLY
    because a missing scheduler is visible: /pipeline/status reports
    `scheduler_running: false`, the last-run time goes stale, and an open
    collection gap appears in the status strip. It does NOT cover someone
    setting the flag in an environment that should not collect.

    Guard 2, single-instance lock (filelock on backend/data/scheduler.lock):
    if another process in this checkout already holds it, log loudly and do
    not start a second scheduler. Covers a uvicorn --reload respawn
    overlapping its predecessor and a second backend started by accident.
    It does NOT cover two different checkouts or two different databases:
    each has its own lock file.

    `hold_jobs=True` starts the scheduler with every job held (APScheduler's
    paused start), so the test suite can inspect the schedule without any
    job firing in a background thread (Keel P5).
    """
    global _running
    env = os.environ if env is None else env
    if env.get(ENV_FLAG) != "1":
        logger.info("Scheduler not started: %s is not set to 1 (scripts/run.py sets it)", ENV_FLAG)
        return None

    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    from filelock import FileLock, Timeout

    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(str(lock_path))
    try:
        lock.acquire(timeout=0)
    except Timeout:
        logger.error(
            "SCHEDULER NOT STARTED: lock %s is held by another process. "
            "Another MESG backend is already collecting from this checkout; stop it first.",
            lock_path,
        )
        return None

    if not logger.handlers:  # uvicorn configures its own loggers, not ours: one console line per job run
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [scheduler] %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    ctx = SchedulerContext(session_factory=session_factory, clock=clock, translator_factory=translator_factory)
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    now = clock()
    next_runs: dict[str, datetime] = {}
    with session_factory() as db:
        for job, interval in JOB_INTERVALS.items():
            next_runs[job] = initial_next_run(last_success_at(db, job), interval, now)
    for job, interval in JOB_INTERVALS.items():
        scheduler.add_job(
            run_job,
            IntervalTrigger(seconds=interval.total_seconds(), timezone=timezone.utc),
            args=(job, ctx, runners),
            id=job,
            next_run_time=next_runs[job],
            max_instances=1,
            coalesce=True,
            misfire_grace_time=int(interval.total_seconds()),
        )
    scheduler.start(paused=hold_jobs)
    _running = RunningScheduler(scheduler=scheduler, lock=lock, ctx=ctx, next_runs=next_runs)
    logger.warning(
        "Scheduler started: %s",
        ", ".join(f"{job} next {when.isoformat(timespec='seconds')}" for job, when in next_runs.items()),
    )
    return _running


def stop_scheduler() -> None:
    global _running
    if _running is not None:
        _running.shutdown()
        _running = None
