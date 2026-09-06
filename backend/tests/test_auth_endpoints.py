from fastapi.testclient import TestClient

from app.database import init_db, seed_dev_user
from app.main import app
from app.routers.auth import _failed_attempts

init_db()
seed_dev_user()


def _fresh_client():
    _failed_attempts.clear()
    return TestClient(app)


def test_me_is_401_when_not_authenticated():
    client = _fresh_client()
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_login_with_wrong_password_is_401():
    client = _fresh_client()
    response = client.post("/auth/login", json={"username": "analyst", "password": "wrong"})
    assert response.status_code == 401


def test_login_then_me_roundtrip():
    client = _fresh_client()
    login_response = client.post(
        "/auth/login", json={"username": "analyst", "password": "correct-password"}
    )
    assert login_response.status_code == 200
    assert login_response.json()["username"] == "analyst"

    me_response = client.get("/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["role"] == "admin"


def test_logout_clears_the_session():
    client = _fresh_client()
    client.post("/auth/login", json={"username": "analyst", "password": "correct-password"})

    logout_response = client.post("/auth/logout")
    assert logout_response.status_code == 204

    me_response = client.get("/auth/me")
    assert me_response.status_code == 401


def test_rate_limit_blocks_after_max_attempts():
    client = _fresh_client()
    for _ in range(5):
        client.post("/auth/login", json={"username": "analyst", "password": "wrong"})

    blocked_response = client.post("/auth/login", json={"username": "analyst", "password": "wrong"})
    assert blocked_response.status_code == 429
    assert "Retry-After" in blocked_response.headers
