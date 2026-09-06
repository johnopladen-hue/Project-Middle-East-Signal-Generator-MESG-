from fastapi.testclient import TestClient

from app.auth import hash_password
from app.database import SessionLocal, init_db, seed_dev_user
from app.main import app
from app.models import User
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


def _client_as(username: str) -> TestClient:
    client = TestClient(app)
    _failed_attempts.pop(username, None)
    response = client.post("/auth/login", json={"username": username, "password": "correct-password"})
    assert response.status_code == 200
    return client


def test_viewer_is_refused_admin_routes():
    client = _client_as("viewer1")
    assert client.get("/admin/sources").status_code == 403
    assert client.get("/admin/recipients").status_code == 403
    assert client.get("/admin/settings").status_code == 403


def test_unauthenticated_is_refused_admin_routes():
    client = TestClient(app)
    assert client.get("/admin/sources").status_code == 401


def test_admin_can_create_list_and_update_a_source():
    client = _client_as("analyst")

    create_response = client.post(
        "/admin/sources",
        json={"name": "Rudaw", "url": "https://rudaw.net", "language": "Kurdish", "type": "rss"},
    )
    assert create_response.status_code == 201
    source_id = create_response.json()["id"]
    assert create_response.json()["last_seen_at"] is None

    list_response = client.get("/admin/sources")
    assert any(row["id"] == source_id for row in list_response.json())

    patch_response = client.patch(f"/admin/sources/{source_id}", json={"active": False})
    assert patch_response.status_code == 200
    assert patch_response.json()["active"] is False
    assert patch_response.json()["name"] == "Rudaw"


def test_admin_can_create_list_and_update_a_recipient():
    client = _client_as("analyst")

    create_response = client.post(
        "/admin/recipients",
        json={"name": "Owner", "email": "owner@example.com", "channels": ["email"], "active": True},
    )
    assert create_response.status_code == 201
    recipient_id = create_response.json()["id"]

    list_response = client.get("/admin/recipients")
    assert any(row["id"] == recipient_id for row in list_response.json())

    patch_response = client.patch(f"/admin/recipients/{recipient_id}", json={"approved_by": "owner"})
    assert patch_response.status_code == 200
    assert patch_response.json()["approved_by"] == "owner"


def test_admin_settings_roundtrip():
    client = _client_as("analyst")

    initial = client.get("/admin/settings")
    assert initial.status_code == 200

    patch_response = client.patch("/admin/settings", json={"alert_severity_threshold": "high"})
    assert patch_response.status_code == 200
    assert patch_response.json()["values"]["alert_severity_threshold"] == "high"

    refetched = client.get("/admin/settings")
    assert refetched.json()["values"]["alert_severity_threshold"] == "high"
