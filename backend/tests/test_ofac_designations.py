"""OFAC SDN designation-list tests (D-013, O-7). Offline, against a genuine
excerpt of real rows from the live SDN.CSV (downloaded and verified during
this session; see findings.md) - includes real orgs that DO match our
already-harvested UCDP organizations (Hamas, PFLP, PFLP-GC, PIJ), a real org
that does NOT match anything we've harvested (Islamic Jihad Group), a real
individual row, and a real non-terrorism-program org row - both excluded by
the harvester's own filters, not just by chance.
"""

from __future__ import annotations

from pathlib import Path

from app.actors.apply import apply_harvest
from app.actors.contracts import ActorRecord, HarvestResult
from app.actors.harvesters.ofac import OFACSDNHarvester
from app.actors.matching import MATCH_THRESHOLD, apply_designations
from app.database import SessionLocal, init_db
from app.models import Designation

init_db()

FIXTURE = Path(__file__).parent / "fixtures" / "ofac_sdn_sample.csv"


def _seed_orgs(session):
    """A minimal, hand-built stand-in for the real UCDP-harvested orgs this
    fixture is designed to match - real names/aliases we independently
    confirmed appear in both UCDP and this OFAC excerpt (findings.md)."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    result = HarvestResult(
        actors=(
            ActorRecord(source_dataset="test-fixture", source_id="209", source_url="https://example.test",
                        name="Hamas", last_verified=now, aliases=("Islamic Resistance Movement",)),
            ActorRecord(source_dataset="test-fixture", source_id="205", source_url="https://example.test",
                        name="PFLP", last_verified=now, aliases=("Popular Front for the Liberation of Palestine",)),
            ActorRecord(source_dataset="test-fixture", source_id="206", source_url="https://example.test",
                        name="PFLP-GC", last_verified=now,
                        aliases=("Popular Front for the Liberation of Palestine-General Command",)),
            ActorRecord(source_dataset="test-fixture", source_id="208", source_url="https://example.test",
                        name="PIJ", last_verified=now, aliases=("Palestinian Islamic Jihad",)),
        ),
    )
    apply_harvest(session, result)


def test_harvester_keeps_only_org_level_terrorism_program_rows():
    records = OFACSDNHarvester(csv_path=FIXTURE).harvest()
    names = {r.raw_org_name for r in records}

    assert "HAMAS" in names
    assert "POPULAR FRONT FOR THE LIBERATION OF PALESTINE" in names
    assert "POPULAR FRONT FOR THE LIBERATION OF PALESTINE - GENERAL COMMAND" in names
    assert "PALESTINE ISLAMIC JIHAD - SHAQAQI FACTION" in names
    assert "ISLAMIC JIHAD GROUP" in names

    # Excluded: an individual (not an org) and a non-terrorism-program org.
    assert "AWDA, Abd Al Aziz" not in names
    assert "AEROCARIBBEAN AIRLINES" not in names
    assert len(records) == 5


def test_real_cross_source_matches_and_real_non_matches():
    with SessionLocal() as session:
        _seed_orgs(session)
        records = OFACSDNHarvester(csv_path=FIXTURE).harvest()
        stats = apply_designations(session, records)

        # At MATCH_THRESHOLD=0.85, only near-exact real matches auto-match:
        # Hamas (1.0), PFLP (1.0), PFLP-GC (0.984).
        assert stats.matched == 3
        # PIJ's real match (OFAC's exact wording differs from UCDP's alias, ratio 0.667) and
        # Islamic Jihad Group (no candidate at all) both land unmatched - a real partial match
        # is deliberately not auto-matched at this threshold; see matching.py's own comment.
        assert stats.unmatched == 2

        hamas_designation = session.query(Designation).filter_by(raw_org_name="HAMAS").first()
        assert hamas_designation.organization_id is not None
        assert hamas_designation.match_status == "matched"
        assert hamas_designation.match_confidence >= MATCH_THRESHOLD

        pij_designation = session.query(Designation).filter_by(
            raw_org_name="PALESTINE ISLAMIC JIHAD - SHAQAQI FACTION"
        ).first()
        assert pij_designation.organization_id is None
        assert pij_designation.match_status == "unmatched_pending_match"
        assert pij_designation.match_confidence is None

        ijg_designation = session.query(Designation).filter_by(raw_org_name="ISLAMIC JIHAD GROUP").first()
        assert ijg_designation.organization_id is None
        assert ijg_designation.match_status == "unmatched_pending_match"
        assert ijg_designation.match_confidence is None
