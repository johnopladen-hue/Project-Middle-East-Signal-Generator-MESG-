"""Telegram public web-preview collector (D-018, U-1 of MESG-Orders-Usable-Today-v0.1.md).

Split exactly like rss_collector.py: `parse_channel_page` is pure and
gate-tested against genuine captured excerpts of t.me/s/ pages (Keel
Principle 5 - no test touches the network); `fetch_channel_page` is the one
function that does, exercised only by app.ingest's real run.

Selectors follow the live markup captured 2026-10-11, not the order's
"as last seen" list, in two places:
- The post's own text is the first `.tgme_widget_message_text` in the bubble
  that is not inside `.tgme_widget_message_reply`. A reply carries the
  *quoted* message's text under that class too, and comes first in the page;
  selecting the first match anywhere would store someone else's words as
  this post (a captionless Fars photo-reply would have been stored as the
  quoted post's text). Photo/video captions sit one level deeper, in
  `.media_supported_cont`, so "direct child of the bubble" is not enough.
- The post time is `a.tgme_widget_message_date time[datetime]`. A video post
  has a second `<time>` (its duration) with no datetime attribute.
"""

from __future__ import annotations

import hashlib
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.ingestion.rss_collector import BACKFILL_WINDOW, USER_AGENT, CollectResult
from app.models import CollectorCursor, RawItem, Source

TELEGRAM_BASE = "https://t.me"

# The plain preview served stale snapshots during verification (findings.md,
# 2026-09-27; A-009). Asking for posts "before" an id far above any real one
# returned the live newest page; paging then continues from the lowest id seen.
FIRST_PAGE_BEFORE = 99999999

MAX_PAGES_PER_RUN = 10

# Politeness (Standing Order 8): at most one request per 2s to t.me, sequential.
MIN_REQUEST_INTERVAL_S = 2.0
_last_request_at: float | None = None

_WHITESPACE_RE = re.compile(r"\s+")
_HANDLE_RE = re.compile(r"^https?://t\.me/(?:s/)?([A-Za-z0-9_]+)/?$")


@dataclass
class ParsedPost:
    post_id: int
    url: str
    text: str | None  # None = media-only (no caption); never stored
    published_at: datetime | None
    content_hash: str


@dataclass
class ParsedPage:
    posts: list[ParsedPost]  # posts inside the backfill window, page order (oldest first)
    oldest_id: int | None  # over every post on the page, in or out of the window
    newest_id: int | None
    crossed_window: bool  # at least one post on the page is older than the backfill window


FetchPage = Callable[[str, int], str]


def handle_from_url(url: str) -> str:
    """`https://t.me/s/farsna` -> `farsna` (approved_sources_v1.yaml form)."""
    match = _HANDLE_RE.match(url.strip())
    if not match:
        raise ValueError(f"not a t.me channel URL: {url!r}")
    return match.group(1)


def _content_hash(handle: str, post_id: int) -> str:
    return hashlib.sha256(f"tg|{handle}|{post_id}".encode("utf-8")).hexdigest()


def _outside_reply(tag) -> bool:
    return tag.find_parent(class_="tgme_widget_message_reply") is None


def _post_text(bubble) -> str | None:
    # First match in document order is the outermost one (some posts nest a
    # second .tgme_widget_message_text inside the first).
    text_div = next((div for div in bubble.select("div.tgme_widget_message_text") if _outside_reply(div)), None)
    if text_div is None:
        return None
    for br in text_div.find_all("br"):
        br.replace_with("\n")
    text = text_div.get_text().strip()
    if not text:
        return None

    forwarded = next((div for div in bubble.select("div.tgme_widget_message_forwarded_from") if _outside_reply(div)), None)
    if forwarded is not None:
        # The attribution line exactly as Telegram renders it ("Forwarded from <name>"),
        # harvested from the page - not composed by MESG.
        attribution = _WHITESPACE_RE.sub(" ", forwarded.get_text()).strip()
        text = f"{attribution}\n\n{text}"
    return text


def _post_time(bubble) -> datetime | None:
    time_tag = bubble.select_one("a.tgme_widget_message_date time[datetime]")
    if time_tag is None:
        return None
    return datetime.fromisoformat(time_tag["datetime"]).astimezone(timezone.utc)


def parse_channel_page(html: str, handle: str, *, now: datetime | None = None) -> ParsedPage:
    """Pure parse: no network, no DB access. `now` is injectable so the
    backfill-window cutoff is deterministic in tests."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - BACKFILL_WINDOW
    soup = BeautifulSoup(html, "html.parser")

    posts: list[ParsedPost] = []
    ids: list[int] = []
    crossed_window = False
    for message in soup.select("div.tgme_widget_message[data-post]"):
        channel, _, raw_id = message["data-post"].partition("/")
        if channel.casefold() != handle.casefold():
            raise ValueError(f"post {message['data-post']!r} is not from channel {handle!r}")
        post_id = int(raw_id)
        ids.append(post_id)

        bubble = message.find("div", class_="tgme_widget_message_bubble")
        published_at = _post_time(bubble)
        if published_at is not None and published_at < cutoff:
            crossed_window = True
            continue

        posts.append(
            ParsedPost(
                post_id=post_id,
                url=f"{TELEGRAM_BASE}/{handle}/{post_id}",
                text=_post_text(bubble),
                published_at=published_at,
                content_hash=_content_hash(handle, post_id),
            )
        )

    return ParsedPage(
        posts=posts,
        oldest_id=min(ids) if ids else None,
        newest_id=max(ids) if ids else None,
        crossed_window=crossed_window,
    )


def fetch_channel_page(handle: str, before: int | None = None, *, timeout: float = 15.0) -> str:
    """Real network I/O. Never called from the offline test suite."""
    global _last_request_at
    if _last_request_at is not None:
        wait = MIN_REQUEST_INTERVAL_S - (time.monotonic() - _last_request_at)
        if wait > 0:
            time.sleep(wait)
    try:
        response = httpx.get(
            f"{TELEGRAM_BASE}/s/{handle}",
            params={"before": before if before is not None else FIRST_PAGE_BEFORE},
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            follow_redirects=True,
        )
    finally:
        _last_request_at = time.monotonic()
    response.raise_for_status()
    return response.text


def _get_cursor(db: Session, source: Source) -> CollectorCursor | None:
    return db.query(CollectorCursor).filter(CollectorCursor.source_id == source.id).first()


def collect_source(
    db: Session,
    source: Source,
    *,
    fetch: FetchPage = fetch_channel_page,
    now: datetime | None = None,
) -> CollectResult:
    """Page backwards from the newest post, store new text posts, advance
    the cursor. A failure is reported, not raised, so one bad channel never
    aborts the run. `fetch` is injectable so paging is testable offline."""
    now = now or datetime.now(timezone.utc)
    result = CollectResult(source_id=source.id, source_name=source.name)

    try:
        handle = handle_from_url(source.url)
        cursor_row = _get_cursor(db, source)
        cursor = int(cursor_row.last_item_id) if cursor_row else None

        new_posts: list[ParsedPost] = []
        newest_seen: int | None = None
        before = FIRST_PAGE_BEFORE
        for page_number in range(MAX_PAGES_PER_RUN):
            page = parse_channel_page(fetch(handle, before), handle, now=now)
            if page.newest_id is None:
                break  # past the start of the channel

            if page_number == 0:
                newest_seen = page.newest_id
                if cursor is not None and page.newest_id < cursor:
                    # Older than what we already hold: a stale cached snapshot.
                    result.stale_snapshot = True
                    return result

            fresh = [post for post in page.posts if cursor is None or post.post_id > cursor]
            result.fetched += len(fresh)
            new_posts.extend(fresh)

            if cursor is not None and page.oldest_id <= cursor:
                break  # reached what the previous run already collected
            if page.crossed_window:
                break
            before = page.oldest_id
        else:
            # Page cap hit before the cursor or the window edge: posts in
            # between may never be collected. Recorded, not silently truncated.
            result.gap_possible = True
    except Exception as exc:
        db.rollback()
        result.error = f"{type(exc).__name__}: {exc}"
        return result

    for post in new_posts:
        if post.text is None:
            result.skipped_media_only += 1
            continue
        existing = (
            db.query(RawItem)
            .filter(RawItem.source_id == source.id)
            .filter((RawItem.content_hash == post.content_hash) | (RawItem.url == post.url))
            .first()
        )
        if existing:
            result.deduped += 1
            continue
        db.add(
            RawItem(
                source_id=source.id,
                original_lang=source.language,
                original_text=post.text,
                url=post.url,
                content_hash=post.content_hash,
                published_at=post.published_at,
            )
        )
        result.new += 1

    source.last_seen_at = datetime.now(timezone.utc)
    db.commit()

    # Only now that the items are committed does the cursor move forward.
    if newest_seen is not None and (cursor is None or newest_seen > cursor):
        cursor_row = _get_cursor(db, source)
        if cursor_row is None:
            cursor_row = CollectorCursor(source_id=source.id, last_item_id=str(newest_seen))
            db.add(cursor_row)
        else:
            cursor_row.last_item_id = str(newest_seen)
        cursor_row.updated_at = datetime.now(timezone.utc)
        db.commit()

    return result
