"""Region (AOR) registry API tests (D-015, O-6). Self-contained, isolated
temp SQLite."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.geo.regions import seed_aor_memberships
from app.main import app

init_db()
with SessionLocal() as _session:
    seed_aor_memberships(_session)


def test_list_regions_names_all_six_only_centcom_has_data():
    client = TestClient(app)
    response = client.get("/regions")
    assert response.status_code == 200
    body = response.json()
    codes = {r["code"] for r in body}
    assert codes == {"NORTHCOM", "SOUTHCOM", "EUCOM", "AFRICOM", "CENTCOM", "INDOPACOM"}
    by_code = {r["code"]: r["has_data"] for r in body}
    assert by_code["CENTCOM"] is True
    assert by_code["EUCOM"] is False


def test_centcom_polygon_is_valid_geojson():
    client = TestClient(app)
    response = client.get("/regions/CENTCOM/polygon")
    assert response.status_code == 200
    body = response.json()
    assert body["type"] == "FeatureCollection"
    assert len(body["features"]) == 1
    feature = body["features"][0]
    assert feature["properties"]["aor"] == "CENTCOM"
    assert feature["properties"]["member_count"] == 22
    assert feature["geometry"]["type"] in ("Polygon", "MultiPolygon")


def test_missing_region_polygon_is_404():
    client = TestClient(app)
    response = client.get("/regions/EUCOM/polygon")
    assert response.status_code == 404


def test_centcom_members_lists_22_sourced_countries():
    client = TestClient(app)
    response = client.get("/regions/CENTCOM/members")
    assert response.status_code == 200
    body = response.json()
    assert len(body["countries"]) == 22
    assert "Israel" in body["countries"]
    assert "Bahrain" in body["countries"]
    assert body["source_date"].startswith("2022-03-30")
