"""Capture frontend test fixtures from the REAL backend, not by hand.

"Harvest, never generate" (D-012/D-013) applies to test fixtures too. This
script builds an isolated temp SQLite DB, runs the real UCDP and OFAC
harvesters over the genuine data excerpts already checked in under
backend/tests/fixtures/, seeds the real CENTCOM AOR membership, adds the
repo's own labelled synthetic story seed (app.dev_seed, every row tagged
"[SYNTHETIC — DEV SEED]" - stories have no real source yet, see test_plan.md),
then calls the real API endpoints and writes their JSON responses to
frontend/src/test/fixtures/. The frontend component tests serve those
responses through MSW.

Run from the repo root:  python scripts/capture_frontend_fixtures.py
Re-run whenever an API response shape changes; the tests then follow the
real contract rather than a stale hand-written one.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BACKEND = REPO / "backend"
OUT = REPO / "frontend" / "src" / "test" / "fixtures"

# Isolated DB, set before app.database is imported (same pattern as backend/tests/conftest.py).
_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["MESG_DATABASE_URL"] = f"sqlite:///{_db_path}"
sys.path.insert(0, str(BACKEND))

from fastapi.testclient import TestClient  # noqa: E402

from app import dev_seed  # noqa: E402
from app.actors.apply import apply_harvest  # noqa: E402
from app.actors.harvesters.ofac import OFACSDNHarvester  # noqa: E402
from app.actors.harvesters.ucdp import UCDPActorHarvester  # noqa: E402
from app.actors.matching import apply_designations  # noqa: E402
from app.database import SessionLocal, init_db  # noqa: E402
from app.geo.regions import seed_aor_memberships  # noqa: E402
from app.main import app  # noqa: E402

FIXTURES = BACKEND / "tests" / "fixtures"

# Timestamps that vary run-to-run (harvest time, seed time) are normalised so
# re-running the script produces a stable diff. Every other value is exactly
# what the API returned.
STABLE_TS = "2026-09-13T00:00:00Z"
VOLATILE_KEYS = {"last_verified", "created_at", "first_seen_at", "last_updated_at"}


def _stabilise(value):
    if isinstance(value, dict):
        return {k: (STABLE_TS if k in VOLATILE_KEYS and v else _stabilise(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [_stabilise(v) for v in value]
    return value


def _write(name: str, data) -> None:
    path = OUT / name
    path.write_text(json.dumps(_stabilise(data), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(REPO)}")


def main() -> None:
    init_db()
    with SessionLocal() as session:
        apply_harvest(session, UCDPActorHarvester(csv_path=FIXTURES / "ucdp_actor_sample.csv").harvest())
        apply_designations(session, OFACSDNHarvester(csv_path=FIXTURES / "ofac_sdn_sample.csv").harvest())
        seed_aor_memberships(session)
        dev_seed.seed(session)
        session.commit()

    client = TestClient(app)
    OUT.mkdir(parents=True, exist_ok=True)

    orgs = client.get("/organizations").json()
    _write("organizations.json", orgs)

    # Profiles for every org that carries a designation or a relationship - the
    # interesting shapes - plus nothing hand-picked beyond that rule.
    details = {}
    for org in orgs:
        detail = client.get(f"/organizations/{org['id']}").json()
        if detail["designations"] or detail["relationships"]:
            details[str(org["id"])] = detail
    _write("organization_details.json", details)

    _write("regions.json", client.get("/regions").json())
    _write("geo_items_centcom.json", client.get("/geo/items", params={"aor": "CENTCOM"}).json())

    _write("pipeline_status.json", _capture_pipeline_status(client))

    os.close(_fd)
    os.unlink(_db_path)


def _capture_pipeline_status(client) -> dict:
    """U-3: a real /pipeline/status over a real IngestRun history - scheduler
    state (when jobs ran), not collected content. The shapes the strip must
    handle: Telegram's last success 2h ago (an open collection gap), RSS
    partial (the HTTP 403 MESG actually records for Al Arabiya), translate
    failed (no model), and no scheduler in this process. Times are relative to
    the capture, then normalised so a re-capture produces a stable diff."""
    from datetime import datetime, timedelta, timezone

    from app.models import IngestRun

    now = datetime.now(timezone.utc)
    rows = [
        ("telegram", now - timedelta(hours=2), "ok", 41, 0, None),
        ("rss", now - timedelta(minutes=10), "partial", 12, 1, "Al Arabiya: HTTP 403"),
        ("translate", now - timedelta(minutes=3), "failed", 0, 0, "NllbModelMissing: NLLB model not found"),
    ]
    with SessionLocal() as session:
        for job, at, status, new, failed, notes in rows:
            session.add(IngestRun(job=job, started_at=at, finished_at=at, status=status, items_new=new,
                                  sources_failed=failed, notes=notes))
        session.commit()
    body = client.get("/pipeline/status").json()
    stamps = {"telegram": "2026-11-01T10:00:00+00:00", "rss": "2026-11-01T11:50:00+00:00",
              "translate": "2026-11-01T11:57:00+00:00"}
    for job in body["jobs"]:
        for key in ("last_run_at", "last_success_at"):
            if job[key]:
                job[key] = stamps[job["job"]]
    for gap in body["collection_gaps"]:
        gap["start"] = stamps[gap["job"]]
    body["last_run_at"] = stamps["rss"]
    return body


if __name__ == "__main__":
    main()
