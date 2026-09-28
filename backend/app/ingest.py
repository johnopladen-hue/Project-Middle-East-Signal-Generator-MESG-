"""Real ingestion entrypoint (I-2/I-6 of MESG-Orders-Ingest-Now-v0.1.md).

`python -m app.ingest --once` runs one real collection pass over every
active `kind=rss` Source. Telegram (I-3) and translation (I-4) are not
wired in yet - this run is RSS-only, matching this session's first
stopping point.
"""

from __future__ import annotations

import sys
import time

from app.database import SessionLocal, init_db
from app.ingestion.rss_collector import CollectResult, collect_source
from app.models import Source


def run_rss(db) -> list[CollectResult]:
    sources = db.query(Source).filter(Source.kind == "rss", Source.active.is_(True)).order_by(Source.name).all()
    return [collect_source(db, source) for source in sources]


def _print_report(results: list[CollectResult], elapsed_s: float) -> None:
    total_fetched = sum(r.fetched for r in results)
    total_new = sum(r.new for r in results)
    total_deduped = sum(r.deduped for r in results)
    failures = [r for r in results if r.error]

    print(f"RSS collection: {len(results)} sources, {elapsed_s:.1f}s wall-clock")
    print(f"  fetched={total_fetched} new={total_new} deduped={total_deduped} failures={len(failures)}")
    print()
    for r in results:
        status = f"error: {r.error}" if r.error else f"fetched={r.fetched} new={r.new} deduped={r.deduped}"
        print(f"  {r.source_name:40s} {status}")


def main() -> None:
    if "--once" not in sys.argv:
        print("Usage: python -m app.ingest --once", file=sys.stderr)
        raise SystemExit(1)

    init_db()
    start = time.monotonic()
    with SessionLocal() as db:
        results = run_rss(db)
    elapsed = time.monotonic() - start
    _print_report(results, elapsed)


if __name__ == "__main__":
    main()
