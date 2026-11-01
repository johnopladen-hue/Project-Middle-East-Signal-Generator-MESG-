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


def test_telegram_items_come_back_with_designation_and_verification_notes_intact():
    """Producer -> consumer contract (U-1): items the Telegram collector stores
    for the real approved tg_farsna (designated) and tg_wafagency
    (authenticity unconfirmed) rows, from genuine captured pages, are served
    by GET /raw-items?kind=telegram with both sources' notes unchanged."""
    from pathlib import Path

    from app.ingestion.telegram_collector import FIRST_PAGE_BEFORE, collect_source
    from app.sources.seed_approved import load_sources, seed_approved

    fixtures = Path(__file__).parent / "fixtures"
    pages = {
        "tg_farsna": (fixtures / "telegram_farsna_fa.html").read_text(encoding="utf-8"),
        "tg_wafagency": (fixtures / "telegram_wafagency_ar.html").read_text(encoding="utf-8"),
    }
    no_posts = (fixtures / "telegram_no_posts_found.html").read_text(encoding="utf-8")
    approved = {row["key"]: row for row in load_sources()}
    oct_11_evening = datetime(2026, 10, 11, 16, 0, tzinfo=timezone.utc)

    with SessionLocal() as db:
        seed_approved(db)
        source_ids = {}
        for key, page in pages.items():
            source = db.query(Source).filter_by(seed_key=key).one()
            collect_source(db, source, now=oct_11_evening,
                           fetch=lambda handle, before, page=page: page if before == FIRST_PAGE_BEFORE else no_posts)
            source_ids[key] = source.id

    client = TestClient(app)
    served = {}
    for key, source_id in source_ids.items():
        body = client.get("/raw-items", params={"kind": "telegram", "source_id": source_id}).json()
        assert body["total"] >= 1
        served[key] = body["items"][0]

    assert served["tg_farsna"]["designation_note"] == approved["tg_farsna"]["designation_note"]
    assert served["tg_farsna"]["verification_note"] == approved["tg_farsna"]["verification_note"]
    assert served["tg_wafagency"]["verification_note"] == approved["tg_wafagency"]["verification_note"]
    assert served["tg_wafagency"]["url"] == "https://t.me/WAFAgency/101380"


def _bbc_persian_post() -> str:
    """Genuine collected text (BBC Persian 293180), via the real collector."""
    from pathlib import Path

    from app.ingestion.telegram_collector import parse_channel_page

    html = (Path(__file__).parent / "fixtures" / "telegram_bbcpersian_fa.html").read_text(encoding="utf-8")
    posts = parse_channel_page(html, "bbcpersian", now=datetime(2026, 10, 11, 16, 0, tzinfo=timezone.utc)).posts
    return next(post.text for post in posts if post.post_id == 293180)


def test_each_item_carries_its_translation_record_or_null():
    """Contract (U-2): NLLB job -> TranslationRecord -> GET /raw-items `translation`."""
    from app.models import TranslationRecord

    with SessionLocal() as db:
        source = _make_source(db, name="BBC Persian (contract)", url="https://t.me/s/bbcpersian-contract", language="fa",
                              kind="telegram")
        translated = RawItem(source_id=source.id, original_lang="fa", original_text=_bbc_persian_post(),
                             url="https://t.me/bbcpersian/293180", content_hash="tr-1",
                             working_text="Trump: Russia and Ukraine agreed to a ceasefire on energy infrastructure")
        untranslated = RawItem(source_id=source.id, original_lang="fa", original_text=_bbc_persian_post(),
                               url="https://t.me/bbcpersian/293180?copy", content_hash="tr-2")
        db.add_all([translated, untranslated])
        db.commit()
        db.add(TranslationRecord(raw_item_id=translated.id, engine="nllb-200-distilled-600M-ct2-int8",
                                 model_sha256="0" * 64, src_code="pes_Arab", status="ok_truncated"))
        db.commit()
        source_id, translated_id = source.id, translated.id

    body = TestClient(app).get("/raw-items", params={"source_id": source_id}).json()
    by_id = {item["id"]: item["translation"] for item in body["items"]}
    assert by_id.pop(translated_id) == {"status": "ok_truncated", "engine": "nllb-200-distilled-600M-ct2-int8",
                                        "src_code": "pes_Arab"}
    assert list(by_id.values()) == [None]


def test_an_item_out_of_attempts_moves_from_awaiting_to_translation_failed():
    from app.models import TranslationRecord
    from app.translation.records import MAX_ATTEMPTS

    client = TestClient(app)
    before = client.get("/raw-items").json()

    with SessionLocal() as db:
        source = _make_source(db, name="BBC Persian (failing)", url="https://t.me/s/bbcpersian-failing", language="fa",
                              kind="telegram")
        item = RawItem(source_id=source.id, original_lang="fa", original_text=_bbc_persian_post(),
                       url="https://t.me/bbcpersian/293180?failing", content_hash="tr-fail")
        db.add(item)
        db.commit()
        db.add_all([
            TranslationRecord(raw_item_id=item.id, engine="nllb-200-distilled-600M-ct2-int8", src_code="pes_Arab",
                              status="failed", error="RuntimeError: simulated")
            for _ in range(MAX_ATTEMPTS)
        ])
        db.commit()
        source_id = source.id

    after = client.get("/raw-items").json()
    served = client.get("/raw-items", params={"source_id": source_id}).json()["items"][0]
    assert (after["translation_failed"] - before["translation_failed"],
            after["awaiting_translation"] - before["awaiting_translation"],
            served["translation"]["status"]) == (1, 0, "failed")


def test_items_are_ordered_by_publication_time_not_by_fetch_order():
    """A collection run fetches sources one after another, so the last
    source fetched must not crowd the first page: an item published earlier
    but fetched later sorts after an item published later."""
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        source_a = _make_source(db, name="Fetched first", url="https://example.test/first", kind="telegram")
        source_b = _make_source(db, name="Fetched last", url="https://example.test/last", kind="telegram")
        db.add_all([
            RawItem(source_id=source_a.id, original_lang="ar", original_text="Published later", url="https://example.test/o1",
                    content_hash="order-1", published_at=now - timedelta(minutes=5), fetched_at=now - timedelta(minutes=2)),
            RawItem(source_id=source_b.id, original_lang="ar", original_text="Published earlier", url="https://example.test/o2",
                    content_hash="order-2", published_at=now - timedelta(hours=3), fetched_at=now - timedelta(minutes=1)),
        ])
        db.commit()
        ids = {source_a.id, source_b.id}

    items = TestClient(app).get("/raw-items", params={"limit": 200}).json()["items"]
    texts = [item["original_text"] for item in items if item["source_id"] in ids]
    assert texts == ["Published later", "Published earlier"]


# --- U-4: search, time window, "new since you opened" --------------------------

AJM_NLLB = ("Coalition spokesman: An unknown assault on passenger lounge number four at King Khalid "
            "International Airport.")  # the real NLLB-200 output for this post (U-2)


def _ajmubasher_post() -> str:
    """Genuine collected text (Al Jazeera Mubasher 510450), via the real collector."""
    from pathlib import Path

    from app.ingestion.telegram_collector import parse_channel_page

    html = (Path(__file__).parent / "fixtures" / "telegram_ajmubasher_ar.html").read_text(encoding="utf-8")
    posts = parse_channel_page(html, "ajmubasher", now=datetime(2026, 10, 11, 16, 0, tzinfo=timezone.utc)).posts
    return next(post.text for post in posts if post.post_id == 510450)


def _u4_source(name: str):
    with SessionLocal() as db:
        source = _make_source(db, name=name, url=f"https://t.me/s/{name.replace(' ', '-')}", language="ar",
                              kind="telegram")
        return source.id


def _add_item(source_id: int, *, text: str, working: str | None = None, hash_: str,
              published: datetime | None = None, fetched: datetime | None = None) -> int:
    with SessionLocal() as db:
        item = RawItem(source_id=source_id, original_lang="ar", original_text=text, working_text=working,
                       url=f"https://t.me/ajmubasher/{hash_}", content_hash=hash_, published_at=published,
                       fetched_at=fetched or datetime.now(timezone.utc))
        db.add(item)
        db.commit()
        return item.id


def test_q_matches_the_english_triage_line_case_insensitively():
    """Contract (U-4): GET /raw-items?q= -> Incoming search box."""
    source_id = _u4_source("AJM search en")
    hit = _add_item(source_id, text=_ajmubasher_post(), working=AJM_NLLB, hash_="u4-en-1")
    _add_item(source_id, text=_bbc_persian_post(), hash_="u4-en-2")
    body = TestClient(app).get("/raw-items", params={"source_id": source_id, "q": "king KHALID"}).json()
    assert [item["id"] for item in body["items"]] == [hit]


def test_q_matches_the_original_script():
    source_id = _u4_source("AJM search ar")
    hit = _add_item(source_id, text=_ajmubasher_post(), hash_="u4-ar-1")
    _add_item(source_id, text=_bbc_persian_post(), hash_="u4-ar-2")
    body = TestClient(app).get("/raw-items", params={"source_id": source_id, "q": "مطار الملك خالد"}).json()
    assert [item["id"] for item in body["items"]] == [hit]


def test_q_treats_percent_and_underscore_literally():
    source_id = _u4_source("AJM search escape")
    _add_item(source_id, text=_ajmubasher_post(), hash_="u4-esc-1")
    body = TestClient(app).get("/raw-items", params={"source_id": source_id, "q": "%"}).json()
    assert body["total"] == 0


def test_window_uses_publication_time_and_falls_back_to_fetch_time():
    now = datetime.now(timezone.utc)
    source_id = _u4_source("AJM window")
    recent_pub = _add_item(source_id, text=_ajmubasher_post(), hash_="u4-w-1",
                           published=now - timedelta(minutes=30), fetched=now - timedelta(minutes=29))
    _add_item(source_id, text=_ajmubasher_post(), hash_="u4-w-2",  # fetched just now, but published 3h ago
              published=now - timedelta(hours=3), fetched=now)
    no_pub_recent_fetch = _add_item(source_id, text=_ajmubasher_post(), hash_="u4-w-3", fetched=now - timedelta(minutes=10))
    body = TestClient(app).get("/raw-items", params={"source_id": source_id, "window_hours": 1}).json()
    assert sorted(item["id"] for item in body["items"]) == sorted([recent_pub, no_pub_recent_fetch])


def test_up_to_id_freezes_the_list_and_counts_newer_items():
    source_id = _u4_source("AJM baseline")
    first = _add_item(source_id, text=_ajmubasher_post(), hash_="u4-b-1")
    opened = TestClient(app).get("/raw-items", params={"source_id": source_id}).json()
    assert (opened["max_id"], opened["newer_count"]) == (first, 0)

    second = _add_item(source_id, text=_bbc_persian_post(), hash_="u4-b-2")
    later = TestClient(app).get("/raw-items", params={"source_id": source_id, "up_to_id": opened["max_id"]}).json()
    assert ([item["id"] for item in later["items"]], later["total"], later["newer_count"]) == ([first], 1, 1)
    # max_id is the newest matching item now, not the pin - what "show" re-pins to.
    assert later["max_id"] == second


def test_newer_count_respects_the_other_filters():
    source_id = _u4_source("AJM baseline filtered")
    first = _add_item(source_id, text=_ajmubasher_post(), working=AJM_NLLB, hash_="u4-bf-1")
    _add_item(source_id, text=_bbc_persian_post(), hash_="u4-bf-2")  # newer, but does not match q
    body = TestClient(app).get("/raw-items", params={"source_id": source_id, "q": "airport", "up_to_id": first}).json()
    assert body["newer_count"] == 0
