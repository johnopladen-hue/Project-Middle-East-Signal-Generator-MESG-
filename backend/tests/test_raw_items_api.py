"""Raw items API tests (D-018, I-5/S-5). Self-contained, isolated temp
SQLite (Keel Principle 5)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.main import app
from app.models import RawItem, Source

init_db()


def _make_source(db, **overrides) -> Source:
    fields = dict(name="Test Source", url="https://example.test/feed", language="ar", type="rss", active=True)
    fields.update(overrides)
    source = Source(**fields)
    db.add(source)
    db.commit()
    return source


def test_empty_state_returns_no_items():
    client = TestClient(app)
    response = client.get("/raw-items", params={"source_id": 999999})
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0


def test_lists_items_newest_first_with_source_metadata():
    with SessionLocal() as db:
        source = _make_source(db, name="Al-Manar", language="ar", kind="rss", source_class="native",
                               designation_note="Hezbollah-owned. US SDGT (2006).")
        older = RawItem(source_id=source.id, original_lang="ar", original_text="Older item", url="https://example.test/1",
                         content_hash="h1", fetched_at=datetime.now(timezone.utc) - timedelta(hours=1))
        newer = RawItem(source_id=source.id, original_lang="ar", original_text="Newer item", url="https://example.test/2",
                         content_hash="h2", fetched_at=datetime.now(timezone.utc))
        db.add_all([older, newer])
        db.commit()
        source_id = source.id

    client = TestClient(app)
    response = client.get("/raw-items", params={"source_id": source_id})
    body = response.json()
    assert body["total"] == 2
    assert [item["original_text"] for item in body["items"]] == ["Newer item", "Older item"]
    assert body["items"][0]["designation_note"] == "Hezbollah-owned. US SDGT (2006)."


def test_filters_by_language_source_class_and_kind():
    with SessionLocal() as db:
        ar_native = _make_source(db, name="Ar Native", language="ar", kind="rss", source_class="native")
        en_comparison = _make_source(db, name="En Comparison", url="https://example.test/en-feed",
                                      language="en", kind="rss", source_class="english_comparison")
        db.add_all([
            RawItem(source_id=ar_native.id, original_lang="ar", original_text="Arabic item", url="https://example.test/a",
                    content_hash="ha"),
            RawItem(source_id=en_comparison.id, original_lang="en", original_text="English item", url="https://example.test/b",
                    content_hash="hb"),
        ])
        db.commit()

    client = TestClient(app)
    ar_only = client.get("/raw-items", params={"language": "ar"}).json()
    assert all(item["original_lang"] == "ar" for item in ar_only["items"])
    assert any(item["original_text"] == "Arabic item" for item in ar_only["items"])

    comparison_only = client.get("/raw-items", params={"source_class": "english_comparison"}).json()
    assert all(item["source_class"] == "english_comparison" for item in comparison_only["items"])


def test_pagination_limit_and_offset():
    with SessionLocal() as db:
        source = _make_source(db, name="Paginated Source", url="https://example.test/paginated")
        for i in range(5):
            db.add(RawItem(source_id=source.id, original_lang="ar", original_text=f"Item {i}",
                            url=f"https://example.test/p{i}", content_hash=f"p{i}"))
        db.commit()
        source_id = source.id

    client = TestClient(app)
    page1 = client.get("/raw-items", params={"source_id": source_id, "limit": 2, "offset": 0}).json()
    page2 = client.get("/raw-items", params={"source_id": source_id, "limit": 2, "offset": 2}).json()
    assert page1["total"] == 5
    assert len(page1["items"]) == 2
    assert len(page2["items"]) == 2
    assert {i["id"] for i in page1["items"]}.isdisjoint({i["id"] for i in page2["items"]})


def test_awaiting_translation_counts_untranslated_non_english_items():
    with SessionLocal() as db:
        native = _make_source(db, name="Needs Translation", url="https://example.test/native", language="fa")
        english = _make_source(db, name="Already English", url="https://example.test/en", language="en")
        db.add_all([
            RawItem(source_id=native.id, original_lang="fa", original_text="Persian item", url="https://example.test/fa1",
                    content_hash="fa1", working_text=None),
            RawItem(source_id=english.id, original_lang="en", original_text="English item", url="https://example.test/en1",
                    content_hash="en1", working_text=None),
        ])
        db.commit()

    client = TestClient(app)
    body = client.get("/raw-items").json()
    assert body["awaiting_translation"] >= 1


def test_silent_sources_lists_active_ingestible_sources_with_no_recent_collection():
    with SessionLocal() as db:
        _make_source(db, name="Never Collected", url="https://example.test/never", kind="rss", last_seen_at=None)
        db.commit()

    client = TestClient(app)
    body = client.get("/raw-items").json()
    assert "Never Collected" in body["silent_sources"]
