from fastapi.testclient import TestClient

from app.database import SessionLocal, init_db, seed_dev_user
from app.main import app
from app.models import Recipient
from app.routers.auth import _failed_attempts

init_db()
seed_dev_user()


def _login_admin(client: TestClient) -> None:
    _failed_attempts.pop("analyst", None)
    response = client.post("/auth/login", json={"username": "analyst", "password": "correct-password"})
    assert response.status_code == 200


def test_recipients_summary_counts_active_by_channel():
    with SessionLocal() as session:
        session.add(Recipient(name="Alice", email="a@example.com", channels=["email"], active=True))
        session.add(Recipient(name="Bob", phone="+15551234567", channels=["sms"], active=True))
        session.add(Recipient(name="Carol", email="c@example.com", channels=["email"], active=False))
        session.commit()

    client = TestClient(app)
    _login_admin(client)

    response = client.get("/recipients/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["active_count"] >= 2
    assert body["email_count"] >= 1
    assert body["sms_count"] >= 1


def test_recipients_summary_requires_authentication():
    client = TestClient(app)
    response = client.get("/recipients/summary")
    assert response.status_code == 401
