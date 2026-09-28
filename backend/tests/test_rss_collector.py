"""RSS collector tests (D-018, I-2). Self-contained, isolated temp SQLite
(Keel Principle 5) - parsing is tested against a genuine captured feed
excerpt (tests/fixtures/npr_world_sample.xml, 3 real items from NPR World,
2026-09-27); `fetch_feed` (the one network-touching function) is never
called here."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from app.database import SessionLocal, init_db
from app.ingestion.rss_collector import collect_source, parse_feed, store_items
from app.models import RawItem, Source

init_db()

FIXTURE = Path(__file__).parent / "fixtures" / "npr_world_sample.xml"
FEED_BYTES = FIXTURE.read_bytes()

YNET_HTML_FIXTURE = Path(__file__).parent / "fixtures" / "ynet_html_description_sample.xml"
YNET_HTML_BYTES = YNET_HTML_FIXTURE.read_bytes()

# All 3 fixture items are dated 2026-09-27, 08:00-09:01 America/New_York.
SHORTLY_AFTER = datetime(2026, 9, 27, 18, 0, tzinfo=timezone.utc)
NINE_DAYS_LATER = datetime(2026, 10, 6, 18, 0, tzinfo=timezone.utc)


def _make_source(**overrides) -> Source:
    fields = dict(
        name="NPR World",
        url="https://feeds.npr.org/1004/rss.xml",
        language="en",
        type="rss",
        active=True,
    )
    fields.update(overrides)
    return Source(**fields)


def test_parse_feed_returns_all_items_within_the_backfill_window():
    items = parse_feed(FEED_BYTES, now=SHORTLY_AFTER)
    assert len(items) == 3
    assert items[0].title == "South Africa reels from spate of mass shootings that killed 38 people in a week"
    assert items[0].url.startswith("https://www.npr.org/")
    assert items[0].published_at is not None


def test_parse_feed_strips_embedded_html_from_the_description():
    """Ynet's real feed embeds raw HTML (img/a tags) in <description> -
    the genuine article this fixture captures does, in its actual live
    feed. The stripped summary must read as plain text, no tags."""
    items = parse_feed(YNET_HTML_BYTES, now=datetime(2026, 9, 28, tzinfo=timezone.utc))
    assert len(items) == 1
    assert "<div>" not in items[0].summary
    assert "<img" not in items[0].summary
    assert "<a href" not in items[0].summary
    assert "אלכסנדר ווצ'יץ'" in items[0].summary


def test_parse_feed_excludes_items_older_than_the_48h_backfill_window():
    """Keel Principle 6: prove the window actually excludes, not just include."""
    items = parse_feed(FEED_BYTES, now=NINE_DAYS_LATER)
    assert items == []


def test_store_items_writes_new_raw_items_and_updates_last_seen_at():
    with SessionLocal() as session:
        source = _make_source()
        session.add(source)
        session.commit()

        items = parse_feed(FEED_BYTES, now=SHORTLY_AFTER)
        result = store_items(session, source, items)

        assert result.fetched == 3
        assert result.new == 3
        assert result.deduped == 0
        assert source.last_seen_at is not None

        stored = session.query(RawItem).filter_by(source_id=source.id).all()
        assert len(stored) == 3
        assert all(r.original_lang == "en" for r in stored)
        assert all(r.published_at is not None for r in stored)


def test_reseeding_the_same_items_dedupes_instead_of_duplicating():
    with SessionLocal() as session:
        source = _make_source(name="NPR World 2", url="https://feeds.npr.org/1004/rss.xml#2")
        session.add(source)
        session.commit()

        items = parse_feed(FEED_BYTES, now=SHORTLY_AFTER)
        store_items(session, source, items)
        second = store_items(session, source, items)

        assert second.new == 0
        assert second.deduped == 3
        assert session.query(RawItem).filter_by(source_id=source.id).count() == 3


def test_collect_source_reports_a_fetch_failure_instead_of_raising(monkeypatch):
    def _boom(url, **kwargs):
        raise ConnectionError("simulated DNS failure")

    monkeypatch.setattr("app.ingestion.rss_collector.fetch_feed", _boom)

    with SessionLocal() as session:
        source = _make_source(name="Unreachable Outlet", url="https://example.test/dead-feed")
        session.add(source)
        session.commit()

        result = collect_source(session, source)

    assert result.error is not None
    assert "simulated DNS failure" in result.error
    assert result.new == 0
