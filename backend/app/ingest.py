"""Real ingestion entrypoint (I-2/I-6 of MESG-Orders-Ingest-Now-v0.1.md,
U-1 of MESG-Orders-Usable-Today-v0.1.md).

`python -m app.ingest --once` runs one real collection pass: every active
`kind=rss` Source, then every active `kind=telegram` Source. Translation
(U-2) is not wired in yet.
"""

from __future__ import annotations

import sys
import time

from app.database import SessionLocal, init_db
from app.ingestion import rss_collector, telegram_collector
from app.ingestion.rss_collector import CollectResult
from app.models import Source


def _active_sources(db, kind: str) -> list[Source]:
    return db.query(Source).filter(Source.kind == kind, Source.active.is_(True)).order_by(Source.name).all()


def run_rss(db) -> list[CollectResult]:
    return [rss_collector.collect_source(db, source) for source in _active_sources(db, "rss")]


def run_telegram(db) -> list[CollectResult]:
    return [telegram_collector.collect_source(db, source) for source in _active_sources(db, "telegram")]


def _print_rss_report(results: list[CollectResult], elapsed_s: float) -> None:
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


def _print_telegram_report(results: list[CollectResult], elapsed_s: float) -> None:
    failures = [r for r in results if r.error]
    print(f"Telegram collection: {len(results)} sources, {elapsed_s:.1f}s wall-clock")
    print(
        f"  fetched={sum(r.fetched for r in results)} new={sum(r.new for r in results)}"
        f" deduped={sum(r.deduped for r in results)}"
        f" skipped_media_only={sum(r.skipped_media_only for r in results)}"
        f" gap_possible={sum(r.gap_possible for r in results)}"
        f" stale_snapshot={sum(r.stale_snapshot for r in results)} failures={len(failures)}"
    )
    print()
    for r in results:
        if r.error:
            status = f"error: {r.error}"
        else:
            status = (
                f"fetched={r.fetched} new={r.new} deduped={r.deduped} skipped_media_only={r.skipped_media_only}"
                f" gap_possible={r.gap_possible} stale_snapshot={r.stale_snapshot}"
            )
        print(f"  {r.source_name:40s} {status}")


def main() -> None:
    if "--once" not in sys.argv:
        print("Usage: python -m app.ingest --once", file=sys.stderr)
        raise SystemExit(1)

    init_db()
    with SessionLocal() as db:
        start = time.monotonic()
        rss_results = run_rss(db)
        rss_elapsed = time.monotonic() - start

        start = time.monotonic()
        telegram_results = run_telegram(db)
        telegram_elapsed = time.monotonic() - start

    _print_rss_report(rss_results, rss_elapsed)
    print()
    _print_telegram_report(telegram_results, telegram_elapsed)


if __name__ == "__main__":
    main()
