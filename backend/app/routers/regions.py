"""Region (AOR) registry - D-015, O-6. Six terrestrial UCP AORs named;
only CENTCOM has membership + a polygon in v1."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.geo.regions import REGIONAL_AORS
from app.models import AorMembership

router = APIRouter(prefix="/regions", tags=["regions"])

_POLYGON_PATHS = {
    "CENTCOM": Path(__file__).resolve().parent.parent / "geo" / "aor_centcom.geojson",
}


class RegionSummary(BaseModel):
    code: str
    label: str
    has_data: bool


@router.get("", response_model=list[RegionSummary])
def list_regions(db: Session = Depends(get_db)):
    aors_with_data = {row.aor for row in db.query(AorMembership.aor).distinct().all()}
    return [
        RegionSummary(code=r["code"], label=r["label"], has_data=r["code"] in aors_with_data)
        for r in REGIONAL_AORS
    ]


@router.get("/{aor}/polygon")
def get_region_polygon(aor: str):
    path = _POLYGON_PATHS.get(aor.upper())
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail=f"No polygon for region {aor!r} yet")
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/{aor}/members")
def get_region_members(aor: str, db: Session = Depends(get_db)):
    rows = db.query(AorMembership).filter_by(aor=aor.upper()).order_by(AorMembership.country_name).all()
    if not rows:
        raise HTTPException(status_code=404, detail=f"No membership data for region {aor!r} yet")
    return {
        "aor": aor.upper(),
        "source": rows[0].source,
        "source_url": rows[0].source_url,
        "source_date": rows[0].source_date.isoformat(),
        "countries": [r.country_name for r in rows],
    }
