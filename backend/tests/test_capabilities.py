"""U-5 honesty banner: every capability flag tested both ways, on a fresh
SQLite per test (the suite's shared temp DB already holds items from other
tests, so "nothing collected yet" can only be tested on an empty one).

No content is invented here: collected text comes from genuine captured
Telegram/RSS excerpts through the real parsers; the dev seed is the repo's
own labelled synthetic seed; the "real" analysis is `app.fakes.FakeAnalyst`
output, the sanctioned stand-in until the Analyst order lands; the sent
alert goes through the real `DeliveryService` with `FakeEmailProvider`.
"""

from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import dev_seed
from app.delivery import DeliveryService
from app.fakes import FakeAnalyst, FakeEmailProvider, FakeSmsProvider
from app.ingestion.telegram_collector import parse_channel_page
from app.main import app
from app.models import (
    Analysis,
    Base,
    Brief,
    DeliveryChannel,
    DeliveryLog,
    RawItem,
    Recipient,
    Source,
    Story,
    TranslationRecord,
)
from app.routers.capabilities import compute_capabilities
from app.database import init_db

init_db()

FIXTURES = Path(__file__).parent / "fixtures"
FLAGS = ("rss", "telegram", "triage_translation", "graded_analysis", "daily_brief", "alert_delivery")


@pytest.fixture
def db(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'caps.db'}")
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as session:
        yield session
    engine.dispose()


def _on(caps) -> set[str]:
    return {flag for flag in FLAGS if getattr(caps, flag)}


def _telegram_item(db) -> RawItem:
    html = (FIXTURES / "telegram_ajmubasher_ar.html").read_text(encoding="utf-8")
    post = next(p for p in parse_channel_page(html, "ajmubasher", now=datetime(2026, 10, 11, 16, 0, tzinfo=timezone.utc)).posts
                if p.post_id == 510450)
    source = Source(name="Al Jazeera Mubasher", url="https://t.me/s/ajmubasher", language="ar", type="telegram",
                    kind="telegram", active=True)
    db.add(source)
    db.flush()
    item = RawItem(source_id=source.id, original_lang="ar", original_text=post.text,
                   url="https://t.me/ajmubasher/510450", content_hash="caps-tg")
    db.add(item)
    db.commit()
    return item


def _rss_item(db) -> RawItem:
    from app.ingestion.rss_collector import parse_feed

    entry = parse_feed((FIXTURES / "npr_world_sample.xml").read_bytes(),
                       now=datetime(2026, 9, 27, 18, 0, tzinfo=timezone.utc))[0]
    source = Source(name="NPR World", url="https://feeds.npr.org/1004/rss.xml", language="en", type="rss", kind="rss",
                    active=True)
    db.add(source)
    db.flush()
    db.add(RawItem(source_id=source.id, original_lang="en", original_text=entry.title, url=entry.url,
                   content_hash="caps-rss"))
    db.commit()


def test_nothing_is_running_on_an_empty_database(db):
    caps = compute_capabilities(db)
    assert (_on(caps), caps.synthetic_data_present) == (set(), False)


def test_telegram_flag_follows_collected_telegram_items(db):
    _telegram_item(db)
    assert _on(compute_capabilities(db)) == {"telegram"}


def test_rss_flag_follows_collected_rss_items(db):
    _rss_item(db)
    assert _on(compute_capabilities(db)) == {"rss"}


def test_a_failed_translation_does_not_count_as_translation_running(db):
    item = _telegram_item(db)
    db.add(TranslationRecord(raw_item_id=item.id, engine="nllb-200-distilled-600M-ct2-int8", src_code="arb_Arab",
                             status="failed", error="empty translation output"))
    db.commit()
    assert "triage_translation" not in _on(compute_capabilities(db))


def test_a_successful_translation_counts(db):
    item = _telegram_item(db)
    db.add(TranslationRecord(raw_item_id=item.id, engine="nllb-200-distilled-600M-ct2-int8", src_code="arb_Arab",
                             status="ok"))
    db.commit()
    assert "triage_translation" in _on(compute_capabilities(db))


def test_the_dev_seed_is_synthetic_not_analysis_or_a_brief(db):
    dev_seed.seed(db)
    db.commit()
    caps = compute_capabilities(db)
    assert (caps.graded_analysis, caps.daily_brief, caps.synthetic_data_present) == (False, False, True)


def test_a_non_seed_analysis_turns_graded_analysis_on(db):
    item = _telegram_item(db)
    story = Story(title=item.original_text[:80])
    db.add(story)
    db.flush()
    result = FakeAnalyst().analyze([item.original_text])
    db.add(Analysis(story_id=story.id, facts_json=result["facts"], analysis_text=result["analysis_text"],
                    probability_grade=1))
    db.commit()
    caps = compute_capabilities(db)
    assert (caps.graded_analysis, caps.synthetic_data_present) == (True, False)


def test_a_non_seed_daily_brief_turns_daily_brief_on(db):
    db.add(Brief(type="daily", for_date=datetime.now(timezone.utc), content_json={"items": []}))
    db.commit()
    assert "daily_brief" in _on(compute_capabilities(db))


def test_a_weekly_brief_is_not_a_daily_brief(db):
    db.add(Brief(type="weekly", for_date=datetime.now(timezone.utc), content_json={"items": []}))
    db.commit()
    assert "daily_brief" not in _on(compute_capabilities(db))


def _delivery_log(db, status_from_service: bool) -> None:
    recipient = Recipient(name="Owner", email="owner@example.test", channels=["email"], active=status_from_service)
    db.add(recipient)
    db.flush()
    result = DeliveryService(FakeEmailProvider(), FakeSmsProvider()).deliver(
        recipient, DeliveryChannel.EMAIL, "subject", "body")
    db.add(DeliveryLog(recipient_id=recipient.id, channel=result.channel, ref_type="signal", ref_id=0,
                       status=result.status, error=result.error))
    db.commit()


def test_a_sent_delivery_turns_alert_delivery_on(db):
    _delivery_log(db, status_from_service=True)
    assert "alert_delivery" in _on(compute_capabilities(db))


def test_a_suppressed_delivery_does_not(db):
    _delivery_log(db, status_from_service=False)  # inactive recipient -> suppressed by the whitelist
    assert "alert_delivery" not in _on(compute_capabilities(db))


def test_capabilities_endpoint_serves_every_flag():
    """Contract (U-5): GET /capabilities -> HonestyBanner."""
    body = TestClient(app).get("/capabilities").json()
    assert set(body) == set(FLAGS) | {"synthetic_data_present"}
    assert all(isinstance(value, bool) for value in body.values())
