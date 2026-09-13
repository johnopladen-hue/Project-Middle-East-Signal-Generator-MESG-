"""Organization profile API tests (D-012, O-8). Self-contained, isolated
temp SQLite (Keel Principle 5)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.actors.apply import apply_harvest
from app.actors.contracts import ActorRecord, HarvestResult, RelationshipRecord
from app.database import SessionLocal, init_db
from app.main import app
from app.models import Designation, Organization

init_db()


def _seed():
    with SessionLocal() as session:
        result = HarvestResult(
            actors=(
                ActorRecord(source_dataset="test-fixture", source_id="org-a", source_url="https://example.test/a",
                            name="Test Faction A", last_verified=datetime.now(timezone.utc),
                            aliases=("Faction A Alt Name",), theatre="Syria", citation="Test Citation, CC BY 4.0"),
                ActorRecord(source_dataset="test-fixture", source_id="org-b", source_url="https://example.test/b",
                            name="Test Faction B", last_verified=datetime.now(timezone.utc), theatre="Lebanon"),
            ),
            relationships=(
                RelationshipRecord(source_dataset="test-fixture", source_org_id="org-a", target_org_id="org-b",
                                    kind="ally", source_url="https://example.test/rel-1"),
            ),
        )
        apply_harvest(session, result)
        org_a = session.query(Organization).filter_by(source_dataset="test-fixture", source_id="org-a").first()
        session.add(
            Designation(
                organization_id=org_a.id,
                raw_org_name="Test Faction A",
                body="US State Department",
                label="Foreign Terrorist Organization",
                list_id="fto-test",
                date=None,
                url="https://example.test/fto-list",
                match_status="matched",
                match_confidence=0.95,
            )
        )
        session.add(
            Designation(
                organization_id=org_a.id,
                raw_org_name="Test Faction A",
                body="UN Security Council",
                label="Consolidated Sanctions List",
                list_id="un-test",
                date=None,
                url="https://example.test/un-list",
                match_status="matched",
                match_confidence=0.9,
            )
        )
        session.commit()
        return org_a.id


def test_list_organizations():
    _seed()
    client = TestClient(app)
    response = client.get("/organizations")
    assert response.status_code == 200
    names = {o["name"] for o in response.json()}
    assert "Test Faction A" in names
    assert "Test Faction B" in names


def test_organization_detail_shows_parallel_designations_and_citation():
    org_a_id = _seed()
    client = TestClient(app)
    response = client.get(f"/organizations/{org_a_id}")
    assert response.status_code == 200
    body = response.json()

    assert body["name"] == "Test Faction A"
    assert "Faction A Alt Name" in body["aliases"]
    assert body["citation"] == "Test Citation, CC BY 4.0"

    # Two designations from two different bodies, both present - neither overwrote the other.
    bodies = {d["body"] for d in body["designations"]}
    assert bodies == {"US State Department", "UN Security Council"}

    # The relationship edge is followable to the other organization. (Other tests in this
    # module also call _seed(), which can add more than one such edge in the shared temp
    # DB - assert the edge exists rather than an exact count.)
    assert len(body["relationships"]) >= 1
    assert any(
        rel["kind"] == "ally" and rel["direction"] == "outbound" and rel["other_org_name"] == "Test Faction B"
        for rel in body["relationships"]
    )


def test_organization_detail_404_for_missing_id():
    client = TestClient(app)
    response = client.get("/organizations/999999")
    assert response.status_code == 404
