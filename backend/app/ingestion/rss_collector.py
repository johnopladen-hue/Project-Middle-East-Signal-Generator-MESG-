"""RSS/Atom collector (D-018, I-2 of MESG-Orders-Ingest-Now-v0.1.md).

Split like MESG's existing harvesters (app/actors/harvesters/): parsing is
pure and gate-tested (Keel Principle 5 - no test touches the network);
`fetch_feed` is the one function that does, exercised only by app.ingest's
real run, never by the offline suite.
"""

from __future__ import annotations

import calendar
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html import unescape

import feedparser
import httpx
from sqlalchemy.orm import Session

from app.models import RawItem, Source

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_html(text: str) -> str:
    """Some feeds (e.g. Ynet) embed raw HTML - img/a tags, entities - in
    their description field. This is presentation cleanup of the captured
    lede, not a content change: no words are added or removed, only markup."""
    without_tags = _TAG_RE.sub(" ", text)
    return _WHITESPACE_RE.sub(" ", unescape(without_tags)).strip()

USER_AGENT = (
    "MESGBot/0.1 (+https://github.com/johnopladen-hue/Project-Middle-East-Signal-Generator-MESG-; "
    "personal research project, read-only)"
)

# First-run backfill window (I-2): don't flood on the first pass.
BACKFILL_WINDOW = timedelta(hours=48)


@dataclass
class ParsedItem:
    url: str
    title: str
    summary: str
    published_at: datetime | None
    content_hash: str


@dataclass
class CollectResult:
    source_id: int
    source_name: str
    fetched: int = 0
    new: int = 0
    deduped: int = 0
    error: str | None = None


def _content_hash(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode("utf-8")).hexdigest()


def _entry_published(entry: dict) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime.fromtimestamp(calendar.timegm(parsed), tz=timezone.utc)


def parse_feed(feed_bytes: bytes, *, now: datetime | None = None) -> list[ParsedItem]:
    """Pure parse: no network, no DB access. `now` is injectable for tests
    so the backfill-window cutoff is deterministic."""
    now = now or datetime.now(timezone.utc)
    cutoff = now - BACKFILL_WINDOW
    parsed = feedparser.parse(feed_bytes)

    items: list[ParsedItem] = []
    for entry in parsed.entries:
        url = entry.get("link") or ""
        title = _strip_html(entry.get("title") or "")
        if not url or not title:
            continue

        published_at = _entry_published(entry)
        if published_at is not None and published_at < cutoff:
            continue

        summary = _strip_html(entry.get("summary") or entry.get("description") or "")
        items.append(
            ParsedItem(
                url=url,
                title=title,
                summary=summary,
                published_at=published_at,
                content_hash=_content_hash(url, title),
            )
        )
    return items


def store_items(db: Session, source: Source, items: list[ParsedItem]) -> CollectResult:
    """Write new RawItems for `source`. Dedupes on content_hash OR url
    (O-5: 'dedupes on content_hash plus URL') - either match is the same
    item. Updates Source.last_seen_at, since this is only called after a
    successful fetch."""
    result = CollectResult(source_id=source.id, source_name=source.name, fetched=len(items))

    for item in items:
        existing = (
            db.query(RawItem)
            .filter(RawItem.source_id == source.id)
            .filter((RawItem.content_hash == item.content_hash) | (RawItem.url == item.url))
            .first()
        )
        if existing:
            result.deduped += 1
            continue

        original_text = item.title if not item.summary else f"{item.title}\n\n{item.summary}"
        db.add(
            RawItem(
                source_id=source.id,
                original_lang=source.language,
                original_text=original_text,
                url=item.url,
                content_hash=item.content_hash,
                published_at=item.published_at,
            )
        )
        result.new += 1

    source.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    return result


def fetch_feed(url: str, *, timeout: float = 15.0) -> bytes:
    """Real network I/O. Never called from the offline test suite."""
    response = httpx.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    return response.content


def collect_source(db: Session, source: Source) -> CollectResult:
    """Fetch + parse + store for one real RSS/Atom source. The only
    function here that touches the network - a failure is reported, not
    raised, so one bad feed never aborts the run."""
    try:
        raw = fetch_feed(source.url)
    except Exception as exc:
        return CollectResult(source_id=source.id, source_name=source.name, error=f"{type(exc).__name__}: {exc}")

    try:
        items = parse_feed(raw)
    except Exception as exc:
        return CollectResult(source_id=source.id, source_name=source.name, error=f"parse error: {type(exc).__name__}: {exc}")

    return store_items(db, source, items)
