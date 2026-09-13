"""Writes HarvestResult records into Organization/Alias/Relationship rows.

The only code path allowed to create actor-layer rows (D-012's "harvest,
never generate" is enforced here, not trusted to every adapter). Resolves
Relationship endpoints by (source_dataset, source_id) against organizations
in the same result *and* already in the database - an edge that resolves to
nothing is counted as unresolved, never silently dropped and never guessed
at (O-3b, Principle 11).
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.actors.contracts import HarvestResult
from app.models import Organization, OrganizationAlias, Relationship, Theatre


@dataclass
class HarvestStats:
    organizations_created: int = 0
    organizations_updated: int = 0
    aliases_created: int = 0
    relationships_created: int = 0
    relationships_unresolved: int = 0
    unresolved_relationship_refs: list[tuple[str, str]] = None  # (source_org_id, target_org_id) pairs

    def __post_init__(self):
        if self.unresolved_relationship_refs is None:
            self.unresolved_relationship_refs = []


@dataclass
class ReconciliationReport:
    total_organizations: int
    total_relationships: int
    orphan_relationship_ids: list[int]
    organizations_with_edges: int

    @property
    def reconciles(self) -> bool:
        return len(self.orphan_relationship_ids) == 0


def _get_or_create_theatre(session: Session, name: str | None) -> Theatre | None:
    if not name:
        return None
    theatre = session.query(Theatre).filter_by(name=name).first()
    if theatre:
        return theatre
    theatre = Theatre(name=name)
    session.add(theatre)
    session.flush()
    return theatre


def apply_harvest(session: Session, result: HarvestResult) -> HarvestStats:
    stats = HarvestStats()
    by_source_id: dict[tuple[str, str], Organization] = {}

    for record in result.actors:
        key = (record.source_dataset, record.source_id)
        org = (
            session.query(Organization)
            .filter_by(source_dataset=record.source_dataset, source_id=record.source_id)
            .first()
        )
        theatre = _get_or_create_theatre(session, record.theatre)

        if org is None:
            org = Organization(
                name=record.name,
                theatre_id=theatre.id if theatre else None,
                source_dataset=record.source_dataset,
                source_id=record.source_id,
                source_url=record.source_url,
                grade=record.grade,
                last_verified=record.last_verified,
                citation=record.citation,
            )
            session.add(org)
            session.flush()
            stats.organizations_created += 1
        else:
            org.name = record.name
            org.theatre_id = theatre.id if theatre else org.theatre_id
            org.source_url = record.source_url
            org.grade = record.grade
            org.last_verified = record.last_verified
            org.citation = record.citation
            stats.organizations_updated += 1

        existing_aliases = {a.name for a in session.query(OrganizationAlias).filter_by(organization_id=org.id).all()}
        for alias_name in record.aliases:
            if alias_name in existing_aliases:
                continue
            session.add(
                OrganizationAlias(
                    organization_id=org.id,
                    name=alias_name,
                    source_dataset=record.source_dataset,
                    source_id=record.source_id,
                    source_url=record.source_url,
                )
            )
            stats.aliases_created += 1

        by_source_id[key] = org

    session.flush()

    for rel in result.relationships:
        source_org = by_source_id.get((rel.source_dataset, rel.source_org_id)) or (
            session.query(Organization).filter_by(source_dataset=rel.source_dataset, source_id=rel.source_org_id).first()
        )
        target_org = by_source_id.get((rel.source_dataset, rel.target_org_id)) or (
            session.query(Organization).filter_by(source_dataset=rel.source_dataset, source_id=rel.target_org_id).first()
        )
        if source_org is None or target_org is None:
            stats.relationships_unresolved += 1
            stats.unresolved_relationship_refs.append((rel.source_org_id, rel.target_org_id))
            continue

        session.add(
            Relationship(
                source_org_id=source_org.id,
                target_org_id=target_org.id,
                kind=rel.kind,
                start_date=rel.start_date,
                end_date=rel.end_date,
                source_dataset=rel.source_dataset,
                source_url=rel.source_url,
            )
        )
        stats.relationships_created += 1

    session.commit()
    return stats


def reconcile(session: Session) -> ReconciliationReport:
    """Both-direction check (O-3b): every edge points at organizations that
    exist, and every organization's edges are countable from either side."""
    org_ids = {org_id for (org_id,) in session.query(Organization.id).all()}
    relationships = session.query(Relationship).all()

    orphan_ids = [
        rel.id for rel in relationships if rel.source_org_id not in org_ids or rel.target_org_id not in org_ids
    ]

    orgs_with_edges = {rel.source_org_id for rel in relationships} | {rel.target_org_id for rel in relationships}

    return ReconciliationReport(
        total_organizations=len(org_ids),
        total_relationships=len(relationships),
        orphan_relationship_ids=orphan_ids,
        organizations_with_edges=len(orgs_with_edges & org_ids),
    )
