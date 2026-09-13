"""Geo endpoint tests (D-014, O-7). Self-contained, isolated temp SQLite -
fixture-driven, no live tile server, no live geocoder."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.geo.regions import seed_aor_memberships
from app.main import app
from app.models import Organization, Story, Theatre

init_db()
with SessionLocal() as _session:
    seed_aor_memberships(_session)


def _seed_geo_fixtures():
    with SessionLocal() as session:
        now = datetime.now(timezone.utc)
        session.add_all(
            [
                Story(
                    title="Located in Syria (city precision)",
                    status="open",
                    first_seen_at=now,
                    last_updated_at=now,
                    location_country="Syria",
                    location_precision="city",
                    latitude=36.2021,
                    longitude=37.1343,
                ),
                Story(
                    title="Located in Iran (country precision)",
                    status="open",
                    first_seen_at=now,
                    last_updated_at=now,
                    location_country="Iran",
                    location_precision="country",
                    latitude=32.5750,
                    longitude=54.2741,
                ),
                Story(
                    title="Genuinely unlocated story",
                    status="open",
                    first_seen_at=now,
                    last_updated_at=now,
                ),
            ]
        )
        theatre = session.query(Theatre).filter_by(name="Lebanon").first()
        if theatre is None:
            theatre = Theatre(name="Lebanon")
            session.add(theatre)
            session.flush()

        if not session.query(Organization).filter_by(source_dataset="test-fixture", source_id="geo-org-1").first():
            session.add(
                Organization(
                    name="Test Org With Theatre",
                    theatre_id=theatre.id,
                    source_dataset="test-fixture",
                    source_id="geo-org-1",
                    source_url="https://example.test/org",
                    last_verified=now,
                )
            )
        session.commit()


def test_located_and_unlocated_split_reconciles():
    _seed_geo_fixtures()
    client = TestClient(app)
    response = client.get("/geo/items", params={"aor": "CENTCOM"})
    assert response.status_code == 200
    body = response.json()

    located_titles = {f["properties"]["title"] for f in body["located"]["features"]}
    assert "Located in Syria (city precision)" in located_titles
    assert "Located in Iran (country precision)" in located_titles
    assert "Test Org With Theatre" in located_titles

    unlocated_titles = {i["title"] for i in body["unlocated"]["items"]}
    assert "Genuinely unlocated story" in unlocated_titles

    # Never a fake coordinate - the unlocated story carries no geometry at all.
    for feature in body["located"]["features"]:
        assert feature["geometry"]["coordinates"][0] is not None
        assert feature["geometry"]["coordinates"][1] is not None

    r = body["reconciliation"]
    assert r["located_count"] == len(body["located"]["features"])
    assert r["unlocated_count"] == body["unlocated"]["count"]
    assert r["total"] == r["located_count"] + r["unlocated_count"]


def test_precision_is_carried_and_differs_by_item():
    _seed_geo_fixtures()
    client = TestClient(app)
    response = client.get("/geo/items", params={"aor": "CENTCOM"})
    precisions = {f["properties"]["title"]: f["properties"]["precision"] for f in response.json()["located"]["features"]}
    assert precisions["Located in Syria (city precision)"] == "city"
    assert precisions["Located in Iran (country precision)"] == "country"
    assert precisions["Test Org With Theatre"] == "country"


def test_detail_links_deep_link_to_existing_routes():
    _seed_geo_fixtures()
    client = TestClient(app)
    response = client.get("/geo/items", params={"aor": "CENTCOM"})
    by_title = {f["properties"]["title"]: f["properties"]["detail_url"] for f in response.json()["located"]["features"]}
    assert by_title["Located in Syria (city precision)"].startswith("/stories/")
    assert by_title["Test Org With Theatre"].startswith("/organizations/")


def test_unsupported_scope_is_rejected():
    client = TestClient(app)
    response = client.get("/geo/items", params={"scope": "v2"})
    assert response.status_code == 400
