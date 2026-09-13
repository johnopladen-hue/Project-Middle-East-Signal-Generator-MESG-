"""The harvester -> storage contract for the actor-network layer (D-012, O-2).

Every source-specific harvester (UCDP today; designation lists in Phase 3)
must emit these shapes rather than writing Organization/Relationship rows
directly. This is what keeps "harvest, never generate" enforceable at a
single boundary instead of trusting every adapter to get provenance right:
apply_harvest() is the only code path that writes actor rows, and it
requires every record to carry its source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class ActorRecord:
    """One organization, as a harvester's own source identifies it."""

    source_dataset: str
    source_id: str
    source_url: str
    name: str
    last_verified: datetime
    aliases: tuple[str, ...] = ()
    theatre: str | None = None
    grade: int | None = None
    citation: str | None = None


@dataclass(frozen=True)
class RelationshipRecord:
    """One edge between two organizations, referencing them by the
    (source_dataset, source_id) pair an ActorRecord in the same harvest
    result carries - resolved to internal Organization ids by apply_harvest,
    never guessed."""

    source_dataset: str
    source_org_id: str
    target_org_id: str
    kind: str
    source_url: str
    start_date: datetime | None = None
    end_date: datetime | None = None


@dataclass(frozen=True)
class HarvestResult:
    actors: tuple[ActorRecord, ...] = field(default_factory=tuple)
    relationships: tuple[RelationshipRecord, ...] = field(default_factory=tuple)


class SourceHarvester(Protocol):
    """What every actor/relationship source-specific adapter (UCDP, ...) implements."""

    source_dataset: str

    def harvest(self) -> HarvestResult: ...


@dataclass(frozen=True)
class DesignationRecord:
    """One characterization by a named body (O-7), from a designation-list
    harvester (OFAC, ...). Emitted as raw text - identity matching against
    an existing Organization happens separately (app.actors.matching), since
    it is uncertain and must stay a visible category, never a guess baked
    into the harvester itself."""

    raw_org_name: str
    body: str
    label: str
    list_id: str
    url: str
    date: datetime | None = None
