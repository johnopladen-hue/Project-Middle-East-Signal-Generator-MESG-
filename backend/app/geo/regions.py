"""The six-AOR region registry (D-015, O-6) and the CENTCOM membership seed
(O-5). Only CENTCOM has data in v1; the other five are named so the
registry is complete, with no polygon/membership until a later increment
(deliberately deferred - MESG-Map-Interface-Orders-v0.1.md §8)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.geo.build_aor_polygon import CENTCOM_MEMBERS
from app.models import AorMembership

REGIONAL_AORS = (
    {"code": "NORTHCOM", "label": "U.S. Northern Command"},
    {"code": "SOUTHCOM", "label": "U.S. Southern Command"},
    {"code": "EUCOM", "label": "U.S. European Command"},
    {"code": "AFRICOM", "label": "U.S. Africa Command"},
    {"code": "CENTCOM", "label": "U.S. Central Command"},
    {"code": "INDOPACOM", "label": "U.S. Indo-Pacific Command"},
)

CENTCOM_SOURCE = "CRS IF11428 v3, \"United States Central Command,\" Updated March 30, 2022"
CENTCOM_SOURCE_URL = "https://www.congress.gov/crs_external_products/IF/PDF/IF11428/IF11428.3.pdf"
CENTCOM_SOURCE_DATE = datetime(2022, 3, 30, tzinfo=timezone.utc)


def seed_aor_memberships(session: Session) -> int:
    """Idempotent: skips countries already recorded for CENTCOM. Returns
    the number of rows created."""
    existing = {
        row.country_name
        for row in session.query(AorMembership).filter_by(aor="CENTCOM").all()
    }
    created = 0
    for country in sorted(CENTCOM_MEMBERS):
        if country in existing:
            continue
        session.add(
            AorMembership(
                aor="CENTCOM",
                country_name=country,
                source=CENTCOM_SOURCE,
                source_url=CENTCOM_SOURCE_URL,
                source_date=CENTCOM_SOURCE_DATE,
            )
        )
        created += 1
    session.commit()
    return created
