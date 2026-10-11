"""Telegram collector tests (D-018, U-1). Self-contained, isolated temp
SQLite (Keel Principle 5). Every page is a genuine captured excerpt of a
real t.me/s/ page (tests/fixtures/telegram_*.html, captured 2026-10-11 by
MESGBot/0.1; each file's header names its URL and the posts kept).
`fetch_channel_page` (the one network-touching function) is never called:
paging tests inject a fetcher that serves those fixtures."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest

from app.database import SessionLocal, init_db
from app.ingestion.telegram_collector import (
    FIRST_PAGE_BEFORE,
    MAX_PAGES_PER_RUN,
    collect_source,
    handle_from_url,
    parse_channel_page,
)
from app.models import CollectorCursor, RawItem, Source

init_db()

FIXTURES = Path(__file__).parent / "fixtures"


def _fixture(name: str) -> str:
    return (FIXTURES / f"telegram_{name}.html").read_text(encoding="utf-8")


AR_PAGE = _fixture("ajmubasher_ar")
FA_PAGE = _fixture("bbcpersian_fa")
HE_PAGE_1 = _fixture("pikudhaoref_he_p1")  # posts 36058-36061
HE_PAGE_2 = _fixture("pikudhaoref_he_p2")  # posts 36054-36057, the page "before" 36058
FORWARD_MEDIA_PAGE = _fixture("amitsegal_forward_media")
FARS_REPLY_PAGE = _fixture("farsna_fa")
NO_POSTS_PAGE = _fixture("no_posts_found")  # what t.me serves past a channel's first post

# The ar/fa/forward fixtures were all posted 2026-10-11 06:00-15:10 UTC.
OCT_11_EVENING = datetime(2026, 10, 11, 16, 0, tzinfo=timezone.utc)
# Pikud HaOref posts span 21 Sep - 10 Oct; at this `now` only 36054 (21 Sep)
# falls outside the 48h backfill window, so the cursor - not the window - is
# what stops paging in the paging tests.
SEP_30_NOON = datetime(2026, 9, 30, 12, 0, tzinfo=timezone.utc)


def _make_source(db, handle: str, language: str) -> Source:
    source = Source(name=f"Test {handle}", url=f"https://t.me/s/{handle}", language=language,
                    type="discussion", kind="telegram", active=True)
    db.add(source)
    db.commit()
    return source


class FakeFetch:
    """Serves fixture pages keyed by the `before` value requested, and
    records every request - so a test can see exactly how far paging went.
    Any other `before` gets the real "No posts found" page."""

    def __init__(self, pages: dict[int, str], default: str = NO_POSTS_PAGE):
        self.pages = pages
        self.default = default
        self.calls: list[int] = []

    def __call__(self, handle: str, before: int) -> str:
        self.calls.append(before)
        return self.pages.get(before, self.default)


def _first_post(html: str, handle: str, now: datetime):
    return parse_channel_page(html, handle, now=now).posts[0]


# ── Parsing: one assertion per test, against each language's fixture ──────────

def test_arabic_post_id():
    assert _first_post(AR_PAGE, "ajmubasher", OCT_11_EVENING).post_id == 510449


def test_arabic_post_text():
    post = _first_post(AR_PAGE, "ajmubasher", OCT_11_EVENING)
    assert post.text == "عاجل | ترمب: وقف إطلاق النار بشأن الطاقة بين روسيا وأوكرانيا ساري المفعول فورا"


def test_arabic_post_timestamp():
    post = _first_post(AR_PAGE, "ajmubasher", OCT_11_EVENING)
    assert post.published_at == datetime(2026, 10, 11, 14, 20, 45, tzinfo=timezone.utc)


def test_persian_post_id():
    assert _first_post(FA_PAGE, "bbcpersian", OCT_11_EVENING).post_id == 293177


def test_persian_post_text():
    post = _first_post(FA_PAGE, "bbcpersian", OCT_11_EVENING)
    assert post.text.split("\n")[0] == "📻 تازه‌ترین خبرهای جهان یکشنبه ۱۹ مهر ۱۴۰۵ از رادیو بی‌بی‌سی در لندن"


def test_persian_post_timestamp():
    post = _first_post(FA_PAGE, "bbcpersian", OCT_11_EVENING)
    assert post.published_at == datetime(2026, 10, 11, 14, 36, 23, tzinfo=timezone.utc)


def test_hebrew_post_id():
    assert _first_post(HE_PAGE_1, "PikudHaOref_all", SEP_30_NOON).post_id == 36058


def test_hebrew_post_text_keeps_line_breaks():
    post = _first_post(HE_PAGE_1, "PikudHaOref_all", SEP_30_NOON)
    assert post.text.split("\n")[:3] == ["✅ עדכון (29/9/2026) 21:38", "", "האירוע הסתיים"]


def test_hebrew_post_timestamp():
    post = _first_post(HE_PAGE_1, "PikudHaOref_all", SEP_30_NOON)
    assert post.published_at == datetime(2026, 9, 29, 18, 38, 42, tzinfo=timezone.utc)


def test_item_url_is_the_canonical_post_link():
    assert _first_post(AR_PAGE, "ajmubasher", OCT_11_EVENING).url == "https://t.me/ajmubasher/510449"


@pytest.mark.parametrize(
    ("page", "handle", "language"),
    [(AR_PAGE, "ajmubasher", "ar"), (FA_PAGE, "bbcpersian", "fa"), (HE_PAGE_1, "PikudHaOref_all", "he")],
    ids=["ar", "fa", "he"],
)
def test_stored_item_language_comes_from_the_source(page, handle, language):
    with SessionLocal() as db:
        source = _make_source(db, handle, language)
        collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: page}), now=OCT_11_EVENING)
        langs = {item.original_lang for item in db.query(RawItem).filter_by(source_id=source.id)}
    assert langs == {language}


def test_a_reply_stores_the_posts_own_caption_not_the_quoted_message():
    """Genuine Fars photo-reply (467729): the quoted post's text appears first
    in the markup, under the same class as the caption."""
    posts = parse_channel_page(FARS_REPLY_PAGE, "farsna", now=OCT_11_EVENING).posts
    reply = next(post for post in posts if post.post_id == 467729)
    assert reply.text.startswith("سازمان تجارت دریایی انگلیس هم انفجار نفتکش در هرمز را تأیید کرد")


def test_a_post_from_another_channel_is_refused():
    with pytest.raises(ValueError):
        parse_channel_page(AR_PAGE, "bbcpersian", now=OCT_11_EVENING)


def test_the_no_posts_found_page_parses_as_empty():
    assert parse_channel_page(NO_POSTS_PAGE, "WAFAgency", now=OCT_11_EVENING).newest_id is None


def test_handle_from_url_reads_the_approved_source_form():
    assert handle_from_url("https://t.me/s/PikudHaOref_all") == "PikudHaOref_all"


# ── Media-only and forwarded posts ──────────────────────────────────────────

def test_media_only_post_is_counted_as_skipped():
    with SessionLocal() as db:
        source = _make_source(db, "amitsegal", "he")
        result = collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: FORWARD_MEDIA_PAGE}), now=OCT_11_EVENING)
    assert result.skipped_media_only == 1


def test_media_only_post_is_not_stored():
    with SessionLocal() as db:
        source = _make_source(db, "amitsegal", "he")
        collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: FORWARD_MEDIA_PAGE}), now=OCT_11_EVENING)
        urls = [item.url for item in db.query(RawItem).filter_by(source_id=source.id)]
    assert urls == ["https://t.me/amitsegal/65667"]


def test_forwarded_post_carries_the_harvested_attribution_line():
    post = _first_post(FORWARD_MEDIA_PAGE, "amitsegal", OCT_11_EVENING)
    assert post.text.startswith("Forwarded from מיכאל שמש\n\n‏במשטרה חושדים")


def test_a_post_that_was_not_forwarded_gets_no_attribution_line():
    """Harvest, never generate: the prefix only exists where the page shows it."""
    posts = parse_channel_page(AR_PAGE, "ajmubasher", now=OCT_11_EVENING).posts
    assert not any(post.text.startswith("Forwarded from") for post in posts)


# ── Paging, cursor, page cap, staleness ─────────────────────────────────────

def _with_cursor(db, source: Source, last_item_id: int) -> None:
    db.add(CollectorCursor(source_id=source.id, last_item_id=str(last_item_id)))
    db.commit()


def test_paging_stops_at_the_cursor():
    """Cursor == the first page's oldest id: everything older is already held,
    so the second page must never be requested."""
    fetch = FakeFetch({FIRST_PAGE_BEFORE: HE_PAGE_1, 36058: HE_PAGE_2})
    with SessionLocal() as db:
        source = _make_source(db, "PikudHaOref_all", "he")
        _with_cursor(db, source, 36058)
        collect_source(db, source, fetch=fetch, now=SEP_30_NOON)
    assert fetch.calls == [FIRST_PAGE_BEFORE]


def test_paging_continues_backwards_from_the_lowest_id_until_the_cursor():
    fetch = FakeFetch({FIRST_PAGE_BEFORE: HE_PAGE_1, 36058: HE_PAGE_2})
    with SessionLocal() as db:
        source = _make_source(db, "PikudHaOref_all", "he")
        _with_cursor(db, source, 36055)
        result = collect_source(db, source, fetch=fetch, now=SEP_30_NOON)
    assert (fetch.calls, result.new) == ([FIRST_PAGE_BEFORE, 36058], 6)  # 36056-36061


def test_hitting_the_page_cap_before_the_cursor_records_gap_possible():
    fetch = FakeFetch({}, default=AR_PAGE)  # every page inside the window, no cursor
    with SessionLocal() as db:
        source = _make_source(db, "ajmubasher", "ar")
        result = collect_source(db, source, fetch=fetch, now=OCT_11_EVENING)
    assert (len(fetch.calls), result.gap_possible) == (MAX_PAGES_PER_RUN, True)


def test_reaching_the_cursor_is_not_a_gap():
    fetch = FakeFetch({FIRST_PAGE_BEFORE: HE_PAGE_1, 36058: HE_PAGE_2})
    with SessionLocal() as db:
        source = _make_source(db, "PikudHaOref_all", "he")
        _with_cursor(db, source, 36058)
        result = collect_source(db, source, fetch=fetch, now=SEP_30_NOON)
    assert result.gap_possible is False


def test_a_first_page_older_than_the_cursor_is_a_stale_snapshot():
    with SessionLocal() as db:
        source = _make_source(db, "PikudHaOref_all", "he")
        _with_cursor(db, source, 36070)
        result = collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: HE_PAGE_1}), now=SEP_30_NOON)
    assert result.stale_snapshot is True


def test_a_stale_snapshot_stores_nothing():
    with SessionLocal() as db:
        source = _make_source(db, "PikudHaOref_all", "he")
        _with_cursor(db, source, 36070)
        collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: HE_PAGE_1}), now=SEP_30_NOON)
        stored = db.query(RawItem).filter_by(source_id=source.id).count()
    assert stored == 0


def test_the_cursor_advances_to_the_newest_post_after_a_successful_run():
    with SessionLocal() as db:
        source = _make_source(db, "ajmubasher", "ar")
        collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: AR_PAGE}), now=OCT_11_EVENING)
        cursor = db.query(CollectorCursor).filter_by(source_id=source.id).one()
    assert cursor.last_item_id == "510451"


def test_rerunning_on_the_same_page_adds_nothing():
    with SessionLocal() as db:
        source = _make_source(db, "ajmubasher", "ar")
        collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: AR_PAGE}), now=OCT_11_EVENING)
        second = collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: AR_PAGE}), now=OCT_11_EVENING)
    assert second.new == 0


def test_without_a_cursor_the_content_hash_still_dedupes():
    with SessionLocal() as db:
        source = _make_source(db, "ajmubasher", "ar")
        collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: AR_PAGE}), now=OCT_11_EVENING)
        db.query(CollectorCursor).filter_by(source_id=source.id).delete()
        db.commit()
        second = collect_source(db, source, fetch=FakeFetch({FIRST_PAGE_BEFORE: AR_PAGE}), now=OCT_11_EVENING)
    assert (second.new, second.deduped) == (0, 3)


def test_a_fetch_failure_is_reported_not_raised():
    def failing_fetch(handle: str, before: int) -> str:
        raise httpx.ConnectError("simulated outage")

    with SessionLocal() as db:
        source = _make_source(db, "ajmubasher", "ar")
        result = collect_source(db, source, fetch=failing_fetch, now=OCT_11_EVENING)
    assert result.error == "ConnectError: simulated outage"
