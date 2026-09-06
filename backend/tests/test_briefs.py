from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.main import app
from app.models import Brief

init_db()


def test_list_briefs_empty_when_none_exist():
    client = TestClient(app)
    response = client.get("/briefs", params={"type": "daily"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_and_get_brief_roundtrip():
    with SessionLocal() as session:
        brief = Brief(
            type="daily",
            for_date=datetime(2026, 9, 6, tzinfo=timezone.utc),
            content_json={"items": [{"story_id": 1, "probability_grade": 4}]},
        )
        session.add(brief)
        session.commit()
        brief_id = brief.id

    client = TestClient(app)

    list_response = client.get("/briefs", params={"type": "daily"})
    assert list_response.status_code == 200
    assert any(item["id"] == brief_id for item in list_response.json())

    detail_response = client.get(f"/briefs/{brief_id}")
    assert detail_response.status_code == 200
    body = detail_response.json()
    assert body["content"]["items"][0]["probability_grade"] == 4


def test_get_missing_brief_is_404():
    client = TestClient(app)
    response = client.get("/briefs/999999")
    assert response.status_code == 404
