"""U-3 scheduler (D-019 scheduler & runtime). Self-contained (Keel P5): the
real collectors and the NLLB model are never called; every job runner here
is a stand-in passed through `runners=`, and time is an injected clock.

The run histories built below are scheduler state (when a job ran), not
collected content, so "harvest, never generate" is not engaged; where a
CollectResult carries an error string it is one MESG actually recorded
(findings.md, 2026-10-11: Al Arabiya HTTP 403, Press TV ReadTimeout).
"""

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from filelock import FileLock

from app import scheduler as sched
from app.database import SessionLocal, init_db, seed_dev_user
from app.ingestion.rss_collector import CollectResult
from app.main import app
from app.models import IngestRun, IngestRunStatus
from app.routers.auth import _failed_attempts

init_db()
seed_dev_user()

T0 = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)
FIFTEEN = timedelta(minutes=15)


@pytest.fixture(autouse=True)
def _clean_state():
    with SessionLocal() as db:
        db.query(IngestRun).delete()
        sched.set_paused(db, False)
        db.commit()
    yield
    sched.stop_scheduler()
    with SessionLocal() as db:
        db.query(IngestRun).delete()
        sched.set_paused(db, False)
        db.commit()


# Stand-in runners for every test that starts a real scheduler: even with
# hold_jobs=True, nothing here may ever reach a real collector (Keel P5).
NO_OP_RUNNERS = {job: (lambda db, ctx: sched.JobOutcome()) for job in sched.JOB_INTERVALS}
START = {"runners": NO_OP_RUNNERS, "hold_jobs": True, "clock": lambda: T0}


def _ctx(clock=lambda: T0):
    return sched.SchedulerContext(session_factory=SessionLocal, clock=clock)


def _add_runs(job: str, times: list[datetime], status: str = "ok") -> None:
    with SessionLocal() as db:
        for t in times:
            db.add(IngestRun(job=job, started_at=t, finished_at=t, status=status))
        db.commit()


def _admin_client() -> TestClient:
    client = TestClient(app)
    _failed_attempts.pop("analyst", None)
    assert client.post("/auth/login", json={"username": "analyst", "password": "correct-password"}).status_code == 200
    return client


# --- Start guards ------------------------------------------------------------


def test_env_flag_absent_means_no_scheduler(tmp_path):
    assert sched.start_scheduler(SessionLocal, env={}, lock_path=tmp_path / "s.lock") is None
    assert sched.is_running() is False


def test_started_scheduler_registers_all_four_jobs_with_their_intervals(tmp_path):
    running = sched.start_scheduler(SessionLocal, env={"MESG_SCHEDULER": "1"}, lock_path=tmp_path / "s.lock", **START)
    jobs = {job.id: job for job in running.scheduler.get_jobs()}
    assert {job_id: (j.trigger.interval, j.max_instances, j.coalesce) for job_id, j in jobs.items()} == {
        "rss": (timedelta(minutes=30), 1, True),
        "telegram": (timedelta(minutes=15), 1, True),
        "translate": (timedelta(minutes=5), 1, True),
        "locate": (timedelta(minutes=5), 1, True),
    }


def test_env_flag_other_than_1_means_no_scheduler(tmp_path):
    assert sched.start_scheduler(SessionLocal, env={"MESG_SCHEDULER": "true"}, lock_path=tmp_path / "s.lock") is None


def test_lock_held_by_another_holder_refuses_second_start(tmp_path):
    lock_path = tmp_path / "s.lock"
    other = FileLock(str(lock_path))
    other.acquire()
    try:
        assert sched.start_scheduler(SessionLocal, env={"MESG_SCHEDULER": "1"}, lock_path=lock_path, **START) is None
    finally:
        other.release()


def test_first_start_holds_lock_and_second_start_refuses(tmp_path):
    lock_path = tmp_path / "s.lock"
    first = sched.start_scheduler(SessionLocal, env={"MESG_SCHEDULER": "1"}, lock_path=lock_path, **START)
    assert first is not None
    assert sched.start_scheduler(SessionLocal, env={"MESG_SCHEDULER": "1"}, lock_path=lock_path, **START) is None


# --- Catch-up after wake ------------------------------------------------------


def test_never_run_job_runs_immediately():
    assert sched.initial_next_run(None, FIFTEEN, T0) == T0


def test_last_success_older_than_interval_runs_immediately():
    assert sched.initial_next_run(T0 - timedelta(hours=3), FIFTEEN, T0) == T0


def test_last_success_within_interval_keeps_cadence():
    assert sched.initial_next_run(T0 - timedelta(minutes=5), FIFTEEN, T0) == T0 + timedelta(minutes=10)


def test_started_scheduler_schedules_catch_up_from_ingest_run_history(tmp_path):
    _add_runs("telegram", [T0 - timedelta(hours=2)])  # stale -> now
    _add_runs("rss", [T0 - timedelta(minutes=10)])  # fresh -> +20 min
    running = sched.start_scheduler(SessionLocal, env={"MESG_SCHEDULER": "1"}, lock_path=tmp_path / "s.lock", **START)
    assert running.next_runs == {
        "rss": T0 + timedelta(minutes=20),
        "telegram": T0,
        "translate": T0,
        "locate": T0,  # never run -> now
    }


def test_failed_run_does_not_count_as_success_for_catch_up():
    _add_runs("rss", [T0 - timedelta(minutes=2)], status="failed")
    with SessionLocal() as db:
        assert sched.last_success_at(db, "rss") is None


# --- Pause ---------------------------------------------------------------------


def test_paused_run_writes_skipped_paused_and_does_not_collect():
    calls = []
    with SessionLocal() as db:
        sched.set_paused(db, True)
    run = sched.run_job("telegram", _ctx(), runners={"telegram": lambda db, ctx: calls.append(1)})
    assert (run.status, calls) == ("skipped_paused", [])


def test_resumed_run_collects_again():
    with SessionLocal() as db:
        sched.set_paused(db, True)
        sched.set_paused(db, False)
    run = sched.run_job("rss", _ctx(), runners={"rss": lambda db, ctx: sched.JobOutcome(items_new=3, sources_total=1)})
    assert (run.status, run.items_new) == ("ok", 3)


def test_admin_pause_and_resume_endpoints_flip_the_flag():
    client = _admin_client()
    assert client.post("/admin/pipeline/pause").json() == {"paused": True}
    assert client.get("/pipeline/status").json()["paused"] is True
    assert client.post("/admin/pipeline/resume").json() == {"paused": False}
    assert client.get("/pipeline/status").json()["paused"] is False


def test_pause_endpoint_refuses_unauthenticated():
    assert TestClient(app).post("/admin/pipeline/pause").status_code == 401


# --- IngestRun status mapping --------------------------------------------------


def _result(name: str, new: int = 0, error: str | None = None) -> CollectResult:
    return CollectResult(source_id=0, source_name=name, new=new, error=error)


def test_some_sources_failed_is_partial():
    outcome = sched._collection_outcome([_result("Maariv", new=20), _result("Al Arabiya", error="HTTP 403")])
    assert (outcome.status, outcome.items_new, outcome.sources_failed) == (IngestRunStatus.PARTIAL, 20, 1)


def test_every_source_failed_is_failed():
    outcome = sched._collection_outcome([_result("Press TV", error="ReadTimeout")])
    assert outcome.status is IngestRunStatus.FAILED


def test_job_that_raises_is_recorded_failed_with_the_exception():
    def boom(db, ctx):
        raise RuntimeError("database is locked")

    run = sched.run_job("rss", _ctx(), runners={"rss": boom})
    assert (run.status, run.notes) == ("failed", "RuntimeError: database is locked")


def test_missing_translator_is_a_failed_run_with_the_instruction_not_a_skip():
    from app.translation.nllb import NllbModelMissing

    def missing():
        raise NllbModelMissing("NLLB model not found at backend/models/...; see U-2")

    ctx = sched.SchedulerContext(session_factory=SessionLocal, clock=lambda: T0, translator_factory=missing)
    run = sched.run_job("translate", ctx)
    assert (run.status, run.notes) == ("failed", "NllbModelMissing: NLLB model not found at backend/models/...; see U-2")


# --- Collection gaps (strict: exactly 2x interval is NOT a gap) ---------------


def test_runs_exactly_two_intervals_apart_are_not_a_gap():
    times = [T0 - 2 * FIFTEEN, T0]
    assert sched.collection_gaps(times, "telegram", FIFTEEN, now=T0) == []


def test_runs_just_over_two_intervals_apart_are_a_gap():
    times = [T0 - 2 * FIFTEEN - timedelta(seconds=1), T0]
    gaps = sched.collection_gaps(times, "telegram", FIFTEEN, now=T0)
    assert [(g.start, g.end) for g in gaps] == [(times[0], T0)]


def test_last_success_exactly_two_intervals_ago_is_not_an_open_gap():
    assert sched.collection_gaps([T0 - 2 * FIFTEEN], "telegram", FIFTEEN, now=T0) == []


def test_last_success_older_than_two_intervals_is_an_open_gap():
    gaps = sched.collection_gaps([T0 - timedelta(hours=1)], "telegram", FIFTEEN, now=T0)
    assert [(g.start, g.ongoing) for g in gaps] == [(T0 - timedelta(hours=1), True)]


def test_gap_that_ended_before_the_seven_day_window_is_not_reported():
    times = [T0 - timedelta(days=9), T0 - timedelta(days=8), T0]
    gaps = sched.collection_gaps(times, "rss", timedelta(minutes=30), now=T0)
    assert [(g.start, g.end) for g in gaps] == [(T0 - timedelta(days=8), T0)]


def test_no_runs_at_all_is_no_gap():
    assert sched.collection_gaps([], "rss", timedelta(minutes=30), now=T0) == []


# --- Contract: IngestRun -> GET /pipeline/status (consumer: PipelineStatusStrip) -


def test_status_endpoint_reports_per_job_runs_gaps_and_scheduler_state():
    now = datetime.now(timezone.utc).replace(microsecond=0)
    _add_runs("telegram", [now - timedelta(hours=3), now - timedelta(minutes=1)])
    _add_runs("rss", [now - timedelta(minutes=5)], status="partial")
    _add_runs("translate", [now - timedelta(minutes=2)], status="skipped_paused")

    body = TestClient(app).get("/pipeline/status").json()

    jobs = {j["job"]: j for j in body["jobs"]}
    assert jobs["telegram"] == {
        "job": "telegram",
        "interval_minutes": 15,
        "last_run_at": (now - timedelta(minutes=1)).isoformat(),
        "last_status": "ok",
        "last_success_at": (now - timedelta(minutes=1)).isoformat(),
    }
    assert (jobs["rss"]["last_status"], jobs["rss"]["last_success_at"]) == (
        "partial", (now - timedelta(minutes=5)).isoformat())
    assert (jobs["translate"]["last_status"], jobs["translate"]["last_success_at"]) == ("skipped_paused", None)
    assert body["collection_gaps"] == [
        {"job": "telegram", "start": (now - timedelta(hours=3)).isoformat(),
         "end": (now - timedelta(minutes=1)).isoformat(), "ongoing": False}
    ]
    assert body["last_run_at"] == (now - timedelta(minutes=1)).isoformat()
    assert body["scheduler_running"] is False
    assert body["paused"] is False
