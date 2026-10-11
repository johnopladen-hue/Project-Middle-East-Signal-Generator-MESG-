"""NLLB triage translator + job tests (D-016, U-2). No model files, no
ctranslate2, no network (Keel P5): token assembly is tested with a stub
sentencepiece-like object, and the job runs against `app.fakes.FakeTranslator`.

Job tests use their own in-memory SQLite, so "newest first" and the pending
counts see only the items each test creates. Item text is genuine collected
text, parsed from the captured Telegram fixtures by the real collector."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.fakes import FakeTranslator
from app.ingestion.telegram_collector import parse_channel_page
from app.models import Base, RawItem, Source, TranslationRecord
from app.translation import records
from app.translation.nllb import (
    LANGUAGE_CODES,
    NllbModelMissing,
    NllbTranslator,
    source_tokens,
    strip_target_prefix,
    triage_excerpt,
)
from app.translation.run import translate_pending

FIXTURES = Path(__file__).parent / "fixtures"
OCT_11_EVENING = datetime(2026, 10, 11, 16, 0, tzinfo=timezone.utc)


def _posts(name: str, handle: str, now: datetime = OCT_11_EVENING) -> dict[int, str]:
    html = (FIXTURES / f"telegram_{name}.html").read_text(encoding="utf-8")
    return {post.post_id: post.text for post in parse_channel_page(html, handle, now=now).posts if post.text}


AR = _posts("ajmubasher_ar", "ajmubasher")
FA = _posts("bbcpersian_fa", "bbcpersian")
HE = _posts("pikudhaoref_he_p1", "PikudHaOref_all", now=datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc))


class StubSentencePiece:
    """Stands in for sentencepiece.SentencePieceProcessor: whitespace pieces
    with the "▁" word-start marker, the shape the real one returns."""

    def encode(self, text, out_type=str):
        return ["▁" + word for word in text.split()]

    def decode(self, pieces):
        return " ".join(piece.lstrip("▁") for piece in pieces)


@pytest.fixture
def db():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _source(db, language: str) -> Source:
    source = Source(name=f"Test {language}", url=f"https://t.me/s/test_{language}", language=language,
                    type="discussion", kind="telegram", active=True)
    db.add(source)
    db.commit()
    return source


def _item(db, source: Source, text: str, published_at: datetime, url_suffix: str) -> RawItem:
    item = RawItem(source_id=source.id, original_lang=source.language, original_text=text,
                   url=f"https://t.me/test/{url_suffix}", content_hash=url_suffix, published_at=published_at)
    db.add(item)
    db.commit()
    return item


# ── Adapter pieces: tokens, output stripping, language map, missing model ────

def test_source_tokens_are_language_code_then_pieces_then_end_marker():
    assert source_tokens(StubSentencePiece(), "عاجل | ترمب", "arb_Arab") == ["arb_Arab", "▁عاجل", "▁|", "▁ترمب", "</s>"]


def test_the_leading_target_language_token_is_dropped_from_output():
    assert strip_target_prefix(["eng_Latn", "▁Urgent", "▁|", "▁Trump"]) == ["▁Urgent", "▁|", "▁Trump"]


def test_output_without_the_target_token_is_left_intact():
    assert strip_target_prefix(["▁Urgent", "▁Trump"]) == ["▁Urgent", "▁Trump"]


def test_language_map_covers_exactly_the_v1_native_languages():
    assert LANGUAGE_CODES == {"ar": "arb_Arab", "fa": "pes_Arab", "he": "heb_Hebr"}


def test_missing_model_files_are_a_hard_error(tmp_path):
    with pytest.raises(NllbModelMissing):
        NllbTranslator(model_dir=tmp_path)


def test_the_missing_model_error_names_the_path_and_the_order(tmp_path):
    with pytest.raises(NllbModelMissing, match=r"NLLB model not found at .*see U-2"):
        NllbTranslator(model_dir=tmp_path)


# ── Triage excerpt (D-016: headline + lede only) ────────────────────────────

def _words(text: str) -> int:
    return len(text.split())


def test_a_short_post_is_kept_whole():
    text = AR[510449]
    assert triage_excerpt(text, _words, max_tokens=400) == (text, False)


def test_a_long_post_is_cut_on_a_boundary_and_marked_truncated():
    text = FA[293179]  # a multi-paragraph BBC Persian post
    excerpt, truncated = triage_excerpt(text, _words, max_tokens=30)
    assert (truncated, text.startswith(excerpt.split("\n")[0]), _words(excerpt) <= 30) == (True, True, True)


def test_line_breaks_survive_the_excerpt():
    excerpt, _ = triage_excerpt(HE[36058], _words, max_tokens=400)
    assert excerpt.split("\n")[:2] == ["✅ עדכון (29/9/2026) 21:38", "האירוע הסתיים"]


# ── The job ─────────────────────────────────────────────────────────────────

def test_newest_items_are_translated_first(db):
    source = _source(db, "ar")
    older = _item(db, source, AR[510449], OCT_11_EVENING - timedelta(hours=2), "older")
    newer = _item(db, source, AR[510450], OCT_11_EVENING - timedelta(hours=1), "newer")
    translator = FakeTranslator()
    translate_pending(db, translator, limit=1)
    assert (newer.working_text is not None, older.working_text) == (True, None)


def test_english_items_are_skipped(db):
    source = _source(db, "en")
    _item(db, source, "Israel Defense Forces statement", OCT_11_EVENING, "en1")
    translator = FakeTranslator()
    translate_pending(db, translator)
    assert translator.calls == []


def test_a_cut_item_is_recorded_ok_truncated(db):
    item = _item(db, _source(db, "fa"), FA[293179], OCT_11_EVENING, "fa-long")
    translate_pending(db, FakeTranslator(), max_tokens=30)
    record = db.query(TranslationRecord).filter_by(raw_item_id=item.id).one()
    assert record.status == "ok_truncated"


def test_a_whole_item_is_recorded_ok_with_engine_and_code(db):
    item = _item(db, _source(db, "he"), HE[36058], OCT_11_EVENING, "he-1")
    translate_pending(db, FakeTranslator())
    record = db.query(TranslationRecord).filter_by(raw_item_id=item.id).one()
    assert (record.status, record.engine, record.src_code) == ("ok", "fake-translator", "he")


def test_an_already_translated_item_is_not_translated_again(db):
    _item(db, _source(db, "ar"), AR[510449], OCT_11_EVENING, "ar-once")
    translate_pending(db, FakeTranslator())
    second = FakeTranslator()
    translate_pending(db, second)
    assert second.calls == []


def test_a_failed_item_is_retried_until_three_attempts_then_left_failed(db):
    item = _item(db, _source(db, "ar"), AR[510450], OCT_11_EVENING, "ar-fails")
    failing = FakeTranslator(fail_on={"المتحدث باسم التحالف"})
    for _ in range(5):
        translate_pending(db, failing)
    failed = db.query(TranslationRecord).filter_by(raw_item_id=item.id, status="failed").count()
    assert failed == 3


def test_an_item_out_of_attempts_counts_as_translation_failed_not_awaiting(db):
    item = _item(db, _source(db, "ar"), AR[510450], OCT_11_EVENING, "ar-gave-up")
    failing = FakeTranslator(fail_on={"المتحدث باسم التحالف"})
    for _ in range(3):
        translate_pending(db, failing)
    counts = ([i.id for i in records.failed_items(db)], records.pending_items(db).count())
    assert counts == ([item.id], 0)


def test_one_failing_item_does_not_fail_its_batch(db):
    source = _source(db, "ar")
    bad = _item(db, source, AR[510450], OCT_11_EVENING, "ar-bad")
    good = _item(db, source, AR[510451], OCT_11_EVENING - timedelta(minutes=1), "ar-good")
    translate_pending(db, FakeTranslator(fail_on={"المسافرين رقم 4"}))
    assert (bad.working_text, good.working_text is not None) == (None, True)


# ── Reconciliation (Keel P11): working_text <-> TranslationRecord ────────────

def test_after_a_run_working_text_and_records_reconcile(db):
    source = _source(db, "ar")
    ids = [_item(db, source, AR[post_id], OCT_11_EVENING, f"rec-{post_id}").id for post_id in AR]
    translate_pending(db, FakeTranslator(fail_on={"المسافرين رقم 4"}))
    assert records.reconcile(db, ids) == ([], [])


def test_reconcile_flags_working_text_without_a_successful_record(db):
    item = _item(db, _source(db, "ar"), AR[510449], OCT_11_EVENING, "text-no-record")
    item.working_text = "Urgent | Trump: energy ceasefire between Russia and Ukraine in effect immediately"
    db.commit()
    assert records.reconcile(db, [item.id]) == ([item.id], [])


def test_reconcile_flags_a_successful_record_without_working_text(db):
    item = _item(db, _source(db, "ar"), AR[510449], OCT_11_EVENING, "record-no-text")
    db.add(TranslationRecord(raw_item_id=item.id, engine="fake-translator", src_code="ar", status="ok"))
    db.commit()
    assert records.reconcile(db, [item.id]) == ([], [item.id])
