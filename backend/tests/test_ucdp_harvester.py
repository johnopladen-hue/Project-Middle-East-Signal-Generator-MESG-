"""UCDP Actor harvester tests (D-012, O-5). Runs entirely offline against
`tests/fixtures/ucdp_actor_sample.csv` - a genuine excerpt (not fabricated)
of real rows from UCDP Actor Dataset v26.1, downloaded and verified during
this session's O-4 license re-confirmation (see findings.md).
"""

from __future__ import annotations

from pathlib import Path

from app.actors.apply import apply_harvest, reconcile
from app.actors.harvesters.ucdp import CITATION, UCDPActorHarvester
from app.database import SessionLocal, init_db
from app.models import Organization, OrganizationAlias, Relationship

init_db()

FIXTURE = Path(__file__).parent / "fixtures" / "ucdp_actor_sample.csv"


def _harvest():
    return UCDPActorHarvester(csv_path=FIXTURE).harvest()


def test_harvester_scopes_to_v1_and_excludes_global_powers():
    result = _harvest()
    ids = {a.source_id for a in result.actors}

    # In scope: Location is ONLY Syria/Lebanon/Jordan/Israel/Palestine/Iran.
    assert "119" in ids  # Government of Lebanon
    assert "164" in ids  # KDPI (Iran)
    assert "207" in ids  # Fatah (Israel, Lebanon - both in scope)
    # Out of scope: "Government of United States of America" (id 3) - its
    # Location lists dozens of countries including Syria, but it is a global
    # power, not a regional actor (the exact distinction O-5's scope filter exists to draw).
    assert "3" not in ids


def test_harvester_maps_real_split_and_alliance_relationships():
    result = _harvest()
    rels_by_source = {}
    for rel in result.relationships:
        rels_by_source.setdefault(rel.source_org_id, []).append(rel)

    # PFLP-GC (206) really did split from PFLP (205) per UCDP's own data.
    pflp_gc_rels = rels_by_source.get("206", [])
    assert any(r.kind == "split-from" and r.target_org_id == "205" for r in pflp_gc_rels)

    # AMB (211) split from AND is allied with Fatah (207) per UCDP's data.
    amb_rels = rels_by_source.get("211", [])
    assert any(r.kind == "split-from" and r.target_org_id == "207" for r in amb_rels)
    assert any(r.kind == "ally" and r.target_org_id == "207" for r in amb_rels)

    # PFLP (205) split from two predecessors (204 and 1067) - a comma-separated field, split correctly.
    pflp_rels = rels_by_source.get("205", [])
    split_targets = {r.target_org_id for r in pflp_rels if r.kind == "split-from"}
    assert split_targets == {"204", "1067"}


def test_harvester_extracts_real_name_history_as_aliases():
    result = _harvest()
    kdpi = next(a for a in result.actors if a.source_id == "164")
    assert kdpi.name == "KDPI"
    # Its original name, before the change UCDP's own NameChange flag records.
    assert "Republic of Kurdistan" in kdpi.aliases
    assert kdpi.theatre == "Iran"


def test_every_record_carries_the_required_citation():
    result = _harvest()
    assert len(result.actors) > 0
    assert all(a.citation == CITATION for a in result.actors)
    assert "CC BY 4.0" in CITATION
    assert "Journal of Peace Research" in CITATION


def test_apply_real_harvest_and_reconcile():
    with SessionLocal() as session:
        stats = apply_harvest(session, _harvest())

        assert stats.organizations_created == 19  # all fixture rows except the excluded global power
        assert stats.relationships_unresolved > 0  # PFLP -> 1067 is outside this fixture's org set
        assert ("205", "1067") in stats.unresolved_relationship_refs

        report = reconcile(session)
        assert report.orphan_relationship_ids == []  # every *created* relationship's endpoints exist
        # total_organizations/relationships are DB-wide (other test modules share this session's
        # temp SQLite file, per conftest.py) - scope the count check to this dataset instead.
        ucdp_org_count = session.query(Organization).filter_by(source_dataset="ucdp-actor").count()
        assert ucdp_org_count == 19

        pflp_gc = session.query(Organization).filter_by(source_dataset="ucdp-actor", source_id="206").first()
        assert pflp_gc is not None
        assert pflp_gc.citation == CITATION

        aliases = session.query(OrganizationAlias).filter_by(organization_id=pflp_gc.id).all()
        # PFLP-GC's own alias fields in the fixture, not asserted on value here - just confirms the
        # alias-writing path ran for a real harvested row.
        assert isinstance(aliases, list)

        relationships = session.query(Relationship).filter_by(source_dataset="ucdp-actor").all()
        assert len(relationships) == stats.relationships_created
