"""News items on the map (D-023): GET /geo/items `news_items` and GET /raw-items/{id}.
Isolated temp SQLite. Item texts are genuine (captured t.me fixture posts and
collected excerpts); their times sit in a June 2026 window no other test module
writes into, so the `until` window isolates them."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.geo.locate import locate_pending
from app.geo.regions import seed_aor_memberships
from app.ingestion.telegram_collector import parse_channel_page
from app.main import app
from app.models import RawItem, Source

init_db()
with SessionLocal() as _session:
    seed_aor_memberships(_session)

client = TestClient(app)
FIXTURES = Path(__file__).parent / "fixtures"
UNTIL = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)


def _post(fixture: str, handle: str, post_id: int, now: datetime) -> str:
    """A post's text, parsed with the collector's 48 h window ending at `now` (just after the post)."""
    page = parse_channel_page((FIXTURES / f"telegram_{fixture}.html").read_text(encoding="utf-8"), handle, now=now)
    return next(p.text for p in page.posts if p.post_id == post_id)


QABATIYA = 'عاجل| قوة خاصة من جيش الاحتلال تحاصر منزلا في بلدة قباطية بجنين وتطلق تجاهه قذائف "إنيرجا".'  # PIC, item 2817
IRAN_COUNTRY = (
    "Iran wrong to expect midterms to restrain Trump, former US official says\n\n"
    "Tehran is making a “total miscalculation” if it believes the US midterm elections will constrain "
    "President Donald Trump’s actions against Iran, former senior US official Morgan Ortagus told Iran International."
)  # Iran International English, item 232 - located at country level
GAZA_A = _post("abualiexpress_reply", "abualiexpress", 131721, datetime(2026, 10, 11, 12, tzinfo=timezone.utc))
GAZA_B = _post("pikudhaoref_he_p1", "PikudHaOref_all", 36058, datetime(2026, 9, 29, 20, tzinfo=timezone.utc))

_ids: dict[str, int] = {}


def _seed():
    if _ids:
        return _ids
    with SessionLocal() as db:
        source = Source(name="geo-news test source", url="https://example.invalid/geo-news", language="he", type="rss", kind="rss", active=False)
        db.add(source)
        db.flush()
        # (label, text, minutes before UNTIL). The country-level item is the NEWEST on purpose.
        for i, (label, text, minutes) in enumerate(
            [("iran", IRAN_COUNTRY, 5), ("gaza_a", GAZA_A, 30), ("gaza_b", GAZA_B, 40), ("qabatiya", QABATIYA, 60),
             ("too_old", QABATIYA, 60 * 49), ("after_until", QABATIYA, -10)]
        ):
            item = RawItem(source_id=source.id, original_lang="he", original_text=text, url=f"https://example.invalid/geo-news/{i}",
                           content_hash=f"geo-news-{i}", published_at=UNTIL - timedelta(minutes=minutes))
            db.add(item)
            db.flush()
            _ids[label] = item.id
        db.commit()
        locate_pending(db)
    return _ids


def _news(**params):
    _seed()
    body = client.get("/geo/items", params={"aor": "CENTCOM", "until": UNTIL.isoformat(), **params}).json()
    return body["news_items"]


def _by_id(news):
    return {f["properties"]["id"]: f for f in news["features"]}


def test_news_items_are_returned_as_items_that_link_to_their_own_page():
    ids = _seed()
    feature = _by_id(_news())[ids["qabatiya"]]
    assert feature["properties"]["kind"] == "item"
    assert feature["properties"]["detail_url"] == f"/incoming/{ids['qabatiya']}"
    assert feature["properties"]["matched_text"] == "قباطية"


def test_the_window_ends_at_until_and_spans_window_hours():
    ids = _seed()
    shown = _by_id(_news())
    assert ids["too_old"] not in shown and ids["after_until"] not in shown


def test_city_level_items_come_before_a_newer_country_level_item():
    ids = _seed()
    order = [f["properties"]["id"] for f in _news()["features"]]
    assert order.index(ids["qabatiya"]) < order.index(ids["iran"])


def test_item_limit_caps_the_dots_and_drops_country_level_first():
    ids = _seed()
    news = _news(item_limit=3)
    assert news["summary"]["shown"] == 3 and news["summary"]["located_in_aor"] == 4
    assert ids["iran"] not in _by_id(news)


def test_items_at_the_same_place_are_spread_around_it_not_stacked():
    ids = _seed()
    shown = _by_id(_news())
    a, b = shown[ids["gaza_a"]], shown[ids["gaza_b"]]
    assert a["properties"]["place_coordinates"] == b["properties"]["place_coordinates"]
    assert a["geometry"]["coordinates"] != b["geometry"]["coordinates"]
    lon, lat = a["properties"]["place_coordinates"]
    for feature in (a, b):
        x, y = feature["geometry"]["coordinates"]
        assert math.hypot((x - lon) * math.cos(math.radians(lat)), y - lat) < 0.1  # within ~10 km


def test_a_lone_item_sits_exactly_on_its_place():
    ids = _seed()
    feature = _by_id(_news())[ids["qabatiya"]]
    assert feature["geometry"]["coordinates"] == feature["properties"]["place_coordinates"]


def test_the_summary_counts_reconcile():
    news = _news()
    summary = news["summary"]
    assert summary["items_in_window"] == summary["located_in_aor"] + summary["not_located"] + summary["not_checked_yet"]


def test_the_item_page_endpoint_carries_the_location_and_its_evidence():
    ids = _seed()
    body = client.get(f"/raw-items/{ids['qabatiya']}").json()
    assert body["original_text"] == QABATIYA
    assert body["location"] == {
        "status": "located", "place_name": "Qabāţīyah", "country": "Palestine", "precision": "city",
        "latitude": body["location"]["latitude"], "longitude": body["location"]["longitude"], "matched_text": "قباطية",
    }


def test_an_unknown_item_is_404():
    assert client.get("/raw-items/987654321").status_code == 404
