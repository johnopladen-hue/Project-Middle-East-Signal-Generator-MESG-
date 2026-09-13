"""Identity matching for DesignationRecord against existing Organizations
(O-7, Principle 11). Matching a free-text sanctions-list name against our
register is inherently uncertain, so the uncertainty is a stored category,
not resolved into a guess: below MATCH_THRESHOLD, a Designation is written
unmatched-pending-match (organization_id=None) - never dropped, never
silently treated as "not designated."
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.actors.contracts import DesignationRecord
from app.models import Designation, DesignationMatchStatus, Organization, OrganizationAlias

# Raised from an initial 0.6 (see findings.md): at real scale that cutoff
# produced false positives ("NATIONAL IRANIAN OIL COMPANY" matching an
# unrelated faction on shared generic tokens) - a wrong terrorism-designation
# match is real-world harm, so precision wins over recall here even though
# it pushes some real partial matches into unmatched-pending-match instead.
MATCH_THRESHOLD = 0.85


@dataclass
class MatchStats:
    matched: int = 0
    unmatched: int = 0


def _best_match(raw_name: str, orgs: list[Organization], aliases_by_org: dict[int, list[str]]) -> tuple[Organization | None, float]:
    upper_raw = raw_name.upper()
    best_org: Organization | None = None
    best_ratio = 0.0
    for org in orgs:
        candidates = [org.name, *aliases_by_org.get(org.id, [])]
        ratio = max(difflib.SequenceMatcher(None, upper_raw, c.upper()).ratio() for c in candidates)
        if ratio > best_ratio:
            best_ratio = ratio
            best_org = org
    return best_org, best_ratio


def apply_designations(session: Session, records: list[DesignationRecord]) -> MatchStats:
    stats = MatchStats()
    orgs = session.query(Organization).all()
    aliases_by_org: dict[int, list[str]] = {}
    for alias in session.query(OrganizationAlias).all():
        aliases_by_org.setdefault(alias.organization_id, []).append(alias.name)

    for record in records:
        org, ratio = _best_match(record.raw_org_name, orgs, aliases_by_org)
        matched = org is not None and ratio >= MATCH_THRESHOLD

        session.add(
            Designation(
                organization_id=org.id if matched else None,
                raw_org_name=record.raw_org_name,
                body=record.body,
                label=record.label,
                list_id=record.list_id,
                date=record.date,
                url=record.url,
                match_status=(
                    DesignationMatchStatus.MATCHED.value
                    if matched
                    else DesignationMatchStatus.UNMATCHED_PENDING_MATCH.value
                ),
                match_confidence=ratio if matched else None,
            )
        )
        if matched:
            stats.matched += 1
        else:
            stats.unmatched += 1

    session.commit()
    return stats
