from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.auth import hash_password
from app.database import SessionLocal, init_db, seed_dev_user
from app.main import app
from app.models import Signal, Story, User
from app.routers.auth import _failed_attempts

init_db()
seed_dev_user()


def _ensure_viewer():
    with SessionLocal() as session:
        if session.query(User).filter_by(username="viewer1").first():
            return
        session.add(
            User(username="viewer1", password_hash=hash_password("correct-password"), role="viewer", active=True)
        )
        session.commit()


_ensure_viewer()


def _build_signal():
    with SessionLocal() as session:
        story = Story(title="Reported mobilization", status="open")
        session.add(story)
        session.flush()
        signal = Signal(
            story_id=story.id,
            type="military_event",
            severity="critical",
            is_imminent=True,
            status="new",
            created_at=datetime(2026, 9, 6, tzinfo=timezone.utc),
        )
        session.add(signal)
        session.commit()
        return signal.id


def _login(client: TestClient, username: str) -> None:
    _failed_attempts.pop(username, None)
    response = client.post("/auth/login", json={"username": username, "password": "correct-password"})
    assert response.status_code == 200


def test_list_signals_filters_by_status():
    signal_id = _build_signal()
    client = TestClient(app)

    response = client.get("/signals", params={"status": "new"})
    assert response.status_code == 200
    assert any(row["id"] == signal_id for row in response.json())

    response = client.get("/signals", params={"status": "released"})
    assert all(row["id"] != signal_id for row in response.json())


def test_viewer_cannot_release_or_suppress():
    signal_id = _build_signal()
    client = TestClient(app)
    _login(client, "viewer1")

    release_response = client.post(f"/signals/{signal_id}/release")
    assert release_response.status_code == 403

    suppress_response = client.post(f"/signals/{signal_id}/suppress")
    assert suppress_response.status_code == 403


def test_admin_can_release_and_it_reflects_in_status():
    signal_id = _build_signal()
    client = TestClient(app)
    _login(client, "analyst")

    response = client.post(f"/signals/{signal_id}/release")
    assert response.status_code == 200
    assert response.json()["status"] == "released"

    detail = client.get(f"/signals/{signal_id}")
    assert detail.json()["status"] == "released"


def test_admin_can_suppress():
    signal_id = _build_signal()
    client = TestClient(app)
    _login(client, "analyst")

    response = client.post(f"/signals/{signal_id}/suppress")
    assert response.status_code == 200
    assert response.json()["status"] == "suppressed"


def test_unauthenticated_cannot_release():
    signal_id = _build_signal()
    client = TestClient(app)
    response = client.post(f"/signals/{signal_id}/release")
    assert response.status_code == 401
