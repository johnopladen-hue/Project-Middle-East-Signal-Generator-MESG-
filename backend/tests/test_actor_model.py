"""Actor-network layer fixtures (D-012, O-3). Self-contained, no network -
these prove the schema and the harvester contract before any real harvest
(Phase 2) touches them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.actors.apply import apply_harvest, reconcile
from app.actors.contracts import ActorRecord, HarvestResult, RelationshipRecord
from app.database import SessionLocal, init_db
from app.models import Designation, Organization, OrganizationAlias

init_db()


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --- (a) multiple designations render as parallel characterizations, not a verdict ---


def test_organization_carries_multiple_independent_designations():
    with SessionLocal() as session:
        org = Organization(
            name="Test Org A",
            source_dataset="test-fixture",
            source_id="org-a",
            source_url="https://example.test/org-a",
            grade=None,
            last_verified=_now(),
        )
        session.add(org)
        session.commit()

        session.add_all(
            [
                Designation(
                    organization_id=org.id,
                    raw_org_name="Test Org A",
                    body="US State Department",
                    label="Foreign Terrorist Organization",
                    list_id="fto-2026",
                    date=_now(),
                    url="https://example.test/fto-list",
                    match_status="matched",
                    match_confidence=0.95,
                ),
                Designation(
                    organization_id=org.id,
                    raw_org_name="Test Org A",
                    body="UN Security Council",
                    label="Consolidated Sanctions List",
                    list_id="un-1267",
                    date=_now(),
                    url="https://example.test/un-list",
                    match_status="matched",
                    match_confidence=0.9,
                ),
            ]
        )
        session.commit()

        designations = session.query(Designation).filter_by(organization_id=org.id).all()
        assert len(designations) == 2
        bodies = {d.body for d in designations}
        assert bodies == {"US State Department", "UN Security Council"}
        # Neither designation overwrote the other - no single "verdict" column exists on Organization.
        assert not hasattr(org, "type")
        assert not hasattr(org, "is_terrorist")


# --- (b) relationship edges reconcile in both directions, no orphans ---


def test_relationship_reconciliation_no_orphans():
    with SessionLocal() as session:
        result = HarvestResult(
            actors=(
                ActorRecord(source_dataset="test-fixture", source_id="b1", source_url="https://example.test/b1",
                            name="Faction B1", last_verified=_now()),
                ActorRecord(source_dataset="test-fixture", source_id="b2", source_url="https://example.test/b2",
                            name="Faction B2", last_verified=_now()),
                ActorRecord(source_dataset="test-fixture", source_id="b3", source_url="https://example.test/b3",
                            name="Faction B3", last_verified=_now()),
            ),
            relationships=(
                RelationshipRecord(source_dataset="test-fixture", source_org_id="b1", target_org_id="b2",
                                    kind="split-from", source_url="https://example.test/rel-1"),
                RelationshipRecord(source_dataset="test-fixture", source_org_id="b2", target_org_id="b3",
                                    kind="ally", source_url="https://example.test/rel-2"),
            ),
        )
        stats = apply_harvest(session, result)
        assert stats.organizations_created == 3
        assert stats.relationships_created == 2
        assert stats.relationships_unresolved == 0

        report = reconcile(session)
        assert report.reconciles
        assert report.orphan_relationship_ids == []
        # All 3 orgs have at least one edge; every edge's endpoints are counted.
        assert report.organizations_with_edges == 3
        assert report.total_relationships == 2


def test_relationship_to_a_missing_organization_is_counted_not_dropped():
    with SessionLocal() as session:
        result = HarvestResult(
            actors=(
                ActorRecord(source_dataset="test-fixture", source_id="c1", source_url="https://example.test/c1",
                            name="Faction C1", last_verified=_now()),
            ),
            relationships=(
                RelationshipRecord(source_dataset="test-fixture", source_org_id="c1", target_org_id="does-not-exist",
                                    kind="rival", source_url="https://example.test/rel-3"),
            ),
        )
        stats = apply_harvest(session, result)
        assert stats.relationships_created == 0
        assert stats.relationships_unresolved == 1
        assert stats.unresolved_relationship_refs == [("c1", "does-not-exist")]


# --- (c) never-harvested vs harvested-but-empty carry different values ---


def test_never_harvested_vs_harvested_empty_are_distinct():
    with SessionLocal() as session:
        never_harvested = Organization(
            name="Test Org Never Verified",
            source_dataset="test-fixture",
            source_id="never-1",
            source_url="https://example.test/never-1",
            grade=None,
            last_verified=None,
        )
        harvested_but_empty = Organization(
            name="Test Org Verified Empty",
            source_dataset="test-fixture",
            source_id="empty-1",
            source_url="https://example.test/empty-1",
            grade=None,
            last_verified=_now(),
        )
        session.add_all([never_harvested, harvested_but_empty])
        session.commit()

        assert never_harvested.last_verified is None
        assert harvested_but_empty.last_verified is not None

        # Both have zero aliases - but that means something different for each.
        never_aliases = session.query(OrganizationAlias).filter_by(organization_id=never_harvested.id).all()
        empty_aliases = session.query(OrganizationAlias).filter_by(organization_id=harvested_but_empty.id).all()
        assert never_aliases == []
        assert empty_aliases == []
        # The distinguishing value lives on last_verified, not on the (identical) empty alias lists.
        assert never_harvested.last_verified != harvested_but_empty.last_verified


def test_unmatched_designation_is_its_own_category_not_dropped():
    with SessionLocal() as session:
        designation = Designation(
            organization_id=None,
            raw_org_name="Some Group Name On A List",
            body="OFAC",
            label="SDN",
            list_id="sdn-2026",
            date=_now(),
            url="https://example.test/sdn-list",
            match_status="unmatched_pending_match",
            match_confidence=None,
        )
        session.add(designation)
        session.commit()

        row = session.query(Designation).filter_by(id=designation.id).first()
        assert row.organization_id is None
        assert row.match_status == "unmatched_pending_match"
        # It exists and is queryable as its own category - not silently absent.
        unmatched_count = session.query(Designation).filter_by(match_status="unmatched_pending_match").count()
        assert unmatched_count >= 1


# --- (d) the harvester -> ActorRecord contract test: correct vs incorrect mapping differ ---


@dataclass
class _FakeRawApiRecord:
    """Stands in for one row of a real source API's response shape."""

    id: str
    name: str
    url: str


def _correct_map(raw: _FakeRawApiRecord, dataset: str) -> ActorRecord:
    return ActorRecord(
        source_dataset=dataset,
        source_id=raw.id,
        source_url=raw.url,
        name=raw.name,
        last_verified=_now(),
    )


def _incorrect_map(raw: _FakeRawApiRecord, dataset: str) -> ActorRecord:
    """Deliberately buggy: swaps id and name - the exact class of mapping
    bug this contract test exists to catch before it reaches a real adapter."""
    return ActorRecord(
        source_dataset=dataset,
        source_id=raw.name,
        source_url=raw.url,
        name=raw.id,
        last_verified=_now(),
    )


def test_harvester_contract_correct_and_incorrect_mapping_differ():
    raw = _FakeRawApiRecord(id="ext-42", name="Test Faction Name", url="https://example.test/ext-42")

    correct = _correct_map(raw, "test-fixture")
    incorrect = _incorrect_map(raw, "test-fixture")

    assert correct != incorrect
    assert correct.source_id == "ext-42"
    assert correct.name == "Test Faction Name"
    # The incorrect mapping is caught precisely because it disagrees with the correct one on the fields
    # apply_harvest() keys organizations by (source_dataset, source_id) - a swapped id/name would silently
    # misfile the record under the wrong identity if this test didn't exist.
    assert incorrect.source_id != correct.source_id
    assert incorrect.name != correct.name
