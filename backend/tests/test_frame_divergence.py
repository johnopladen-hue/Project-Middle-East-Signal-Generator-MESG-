"""Frame-divergence note tests (D-015, O-9). Self-contained, isolated temp
SQLite, real login flow (matches existing auth test conventions)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.auth import hash_password
from app.database import SessionLocal, init_db
from app.main import app
from app.models import User

init_db()

# A dedicated user, not "analyst" - other test modules deliberately trip
# analyst's login rate limit (module-level state, shared for the whole
# pytest process), which would otherwise 429 a login here too.
with SessionLocal() as _session:
    if not _session.query(User).filter_by(username="frame_divergence_tester").first():
        _session.add(
            User(username="frame_divergence_tester", password_hash=hash_password("test-password"), role="admin", active=True)
        )
        _session.commit()


def _login_client() -> TestClient:
    client = TestClient(app)
    response = client.post("/auth/login", json={"username": "frame_divergence_tester", "password": "test-password"})
    assert response.status_code == 200
    return client


def test_create_and_list_note_for_a_region():
    client = _login_client()
    create = client.post(
        "/frame-divergence-notes",
        json={"scope_type": "region", "scope_id": "CENTCOM", "text": "In-region framing differs from the U.S. lens here."},
    )
    assert create.status_code == 201
    body = create.json()
    assert body["scope_type"] == "region"
    assert body["created_by"] == "frame_divergence_tester"

    listing = client.get("/frame-divergence-notes", params={"scope_type": "region", "scope_id": "CENTCOM"})
    assert listing.status_code == 200
    assert any(n["id"] == body["id"] for n in listing.json())


def test_unauthenticated_create_is_401():
    client = TestClient(app)
    response = client.post(
        "/frame-divergence-notes",
        json={"scope_type": "region", "scope_id": "CENTCOM", "text": "x"},
    )
    assert response.status_code == 401


def test_notes_are_scoped_by_id():
    client = _login_client()
    client.post("/frame-divergence-notes", json={"scope_type": "region", "scope_id": "EUCOM", "text": "eucom note"})
    listing = client.get("/frame-divergence-notes", params={"scope_type": "region", "scope_id": "CENTCOM"})
    assert all("eucom" not in n["text"] for n in listing.json())
