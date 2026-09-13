"""Organization profile - the actor-network layer's first visible surface
(D-012, O-8). Designations render as parallel sourced characterizations,
never a resolved verdict; every surfaced record carries its citation
(Standing Order 6)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Designation, Organization, OrganizationAlias, Relationship

router = APIRouter(prefix="/organizations", tags=["organizations"])


class OrganizationSummary(BaseModel):
    id: int
    name: str
    theatre: str | None
    source_dataset: str


class DesignationOut(BaseModel):
    id: int
    body: str
    label: str
    list_id: str
    date: str | None
    url: str
    match_status: str
    match_confidence: float | None


class RelationshipOut(BaseModel):
    id: int
    kind: str
    direction: str  # "outbound" | "inbound"
    other_org_id: int
    other_org_name: str
    start_date: str | None
    end_date: str | None


class OrganizationDetail(BaseModel):
    id: int
    name: str
    aliases: list[str]
    theatre: str | None
    source_dataset: str
    source_id: str
    source_url: str
    citation: str | None
    last_verified: str | None
    designations: list[DesignationOut]
    relationships: list[RelationshipOut]


@router.get("", response_model=list[OrganizationSummary])
def list_organizations(db: Session = Depends(get_db)):
    orgs = db.query(Organization).order_by(Organization.name).all()
    return [
        OrganizationSummary(
            id=org.id,
            name=org.name,
            theatre=org.theatre.name if org.theatre else None,
            source_dataset=org.source_dataset,
        )
        for org in orgs
    ]


@router.get("/{organization_id}", response_model=OrganizationDetail)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter_by(id=organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    aliases = [a.name for a in db.query(OrganizationAlias).filter_by(organization_id=org.id).order_by(OrganizationAlias.name).all()]

    designations = [
        DesignationOut(
            id=d.id,
            body=d.body,
            label=d.label,
            list_id=d.list_id,
            date=d.date.isoformat() if d.date else None,
            url=d.url,
            match_status=d.match_status,
            match_confidence=d.match_confidence,
        )
        for d in db.query(Designation).filter_by(organization_id=org.id).order_by(Designation.body).all()
    ]

    outbound = (
        db.query(Relationship, Organization)
        .join(Organization, Relationship.target_org_id == Organization.id)
        .filter(Relationship.source_org_id == org.id)
        .all()
    )
    inbound = (
        db.query(Relationship, Organization)
        .join(Organization, Relationship.source_org_id == Organization.id)
        .filter(Relationship.target_org_id == org.id)
        .all()
    )

    relationships = [
        RelationshipOut(
            id=rel.id,
            kind=rel.kind,
            direction="outbound",
            other_org_id=other.id,
            other_org_name=other.name,
            start_date=rel.start_date.isoformat() if rel.start_date else None,
            end_date=rel.end_date.isoformat() if rel.end_date else None,
        )
        for rel, other in outbound
    ] + [
        RelationshipOut(
            id=rel.id,
            kind=rel.kind,
            direction="inbound",
            other_org_id=other.id,
            other_org_name=other.name,
            start_date=rel.start_date.isoformat() if rel.start_date else None,
            end_date=rel.end_date.isoformat() if rel.end_date else None,
        )
        for rel, other in inbound
    ]

    return OrganizationDetail(
        id=org.id,
        name=org.name,
        aliases=aliases,
        theatre=org.theatre.name if org.theatre else None,
        source_dataset=org.source_dataset,
        source_id=org.source_id,
        source_url=org.source_url,
        citation=org.citation,
        last_verified=org.last_verified.isoformat() if org.last_verified else None,
        designations=designations,
        relationships=relationships,
    )
