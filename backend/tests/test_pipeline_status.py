from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db
from app.main import app
from app.models import Source

init_db()


def test_status_with_no_sources_is_zero_silent():
    client = TestClient(app)
    response = client.get("/pipeline/status")
    assert response.status_code == 200
    body = response.json()
    assert body["last_run_at"] is None
    assert body["silent_source_count"] == 0


def test_status_counts_sources_with_no_last_seen_as_silent():
    with SessionLocal() as session:
        session.add(
            Source(
                name="Test Source",
                url="https://example.com",
                language="Arabic",
                type="rss",
                active=True,
                last_seen_at=None,
            )
        )
        session.commit()

    client = TestClient(app)
    response = client.get("/pipeline/status")
    assert response.json()["silent_source_count"] >= 1
