"""UCDP Actor Dataset harvester (D-012, O-5).

Corrected during O-4's license gate (2026-09-13, findings.md): the Actor
Dataset - the one that carries name history and split/alliance/faction
relationships - is distributed as a plain public CSV download (CC BY 4.0,
no auth), not through UCDP's token-gated JSON API (which covers different
resources - gedevents, dyadic, etc. - and has no dedicated actor endpoint).
This harvester reads the downloaded CSV directly; it does not call the API.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from app.actors.contracts import ActorRecord, HarvestResult, RelationshipRecord

SOURCE_DATASET = "ucdp-actor"
DATASET_URL = "https://ucdp.uu.se/downloads/actor/ucdp-actor-261-csv.zip"
CITATION = (
    "Shawn Davies, Therese Pettersson, Magnus Oberg, Organized violence 1989-2025, and violent "
    "political protests, Journal of Peace Research, 2026. UCDP Actor Dataset v26.1, CC BY 4.0 "
    "(https://ucdp.uu.se/downloads/actor/ucdp-actor-codebook-261.pdf). Data has been normalized "
    "for MESG; this normalized form is not produced or endorsed by UCDP."
)

# v1 scope (D-008): Levantine Arabic + Iranian Persian. An actor whose Location
# is ONLY these countries counts as regional; a global power's incidental
# historical involvement in the region (e.g. "Government of United States of
# America", whose Location lists dozens of countries including Syria) does not.
V1_THEATRES = ("Syria", "Lebanon", "Jordan", "Israel", "Palestine", "Iran")

_RELATIONSHIP_FIELDS = (
    ("ActorIdPrev", "split-from"),
    ("ActorIdAlliance", "ally"),
    ("ActorIdGroup", "faction-of"),
)


def _split_ids(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _locations(raw: str) -> set[str]:
    return {part.strip() for part in raw.split(",") if part.strip()}


def _pick_theatre(raw_location: str) -> str | None:
    locations = _locations(raw_location)
    for candidate in V1_THEATRES:
        if candidate in locations:
            return candidate
    return None


def _in_v1_scope(raw_location: str) -> bool:
    locations = _locations(raw_location)
    return bool(locations) and locations <= set(V1_THEATRES)


@dataclass
class UCDPActorHarvester:
    """Reads the UCDP Actor Dataset CSV and emits v1-scoped ActorRecord /
    RelationshipRecord rows. Never widens scope past D-008."""

    csv_path: Path
    source_dataset: str = SOURCE_DATASET

    def harvest(self) -> HarvestResult:
        now = datetime.now(timezone.utc)

        with open(self.csv_path, encoding="latin-1", newline="") as f:
            rows = list(csv.DictReader(f))

        scoped_ids = {row["ActorId"] for row in rows if _in_v1_scope(row["Location"])}

        actors: list[ActorRecord] = []
        relationships: list[RelationshipRecord] = []

        for row in rows:
            if row["ActorId"] not in scoped_ids:
                continue

            name = row["NameData"] or row["NameOrigFullEng"]
            aliases = tuple(
                sorted(
                    {
                        value
                        for value in (row["NameOrig"], row["NameOrigFullEng"], row["NewName"])
                        if value and value not in ("n/a", name)
                    }
                )
            )
            actors.append(
                ActorRecord(
                    source_dataset=self.source_dataset,
                    source_id=row["ActorId"],
                    source_url=DATASET_URL,
                    name=name,
                    last_verified=now,
                    aliases=aliases,
                    theatre=_pick_theatre(row["Location"]),
                    grade=None,
                    citation=CITATION,
                )
            )
            for field, kind in _RELATIONSHIP_FIELDS:
                for target_id in _split_ids(row[field]):
                    relationships.append(
                        RelationshipRecord(
                            source_dataset=self.source_dataset,
                            source_org_id=row["ActorId"],
                            target_org_id=target_id,
                            kind=kind,
                            source_url=DATASET_URL,
                        )
                    )

        return HarvestResult(actors=tuple(actors), relationships=tuple(relationships))
