"""OFAC SDN list harvester, scoped to terrorism-designation programs (D-013, O-7).

Reads the real, publicly downloadable SDN.CSV (no auth, no header row - a
fixed 12-column legacy format: ent_num, sdn_name, sdn_type, program, title,
call_sign, vess_type, tonnage, grt, vess_flag, vess_owner, remarks). Keeps
only organization-level rows (sdn_type blank, "-0-") under a
terrorism-related program tag - individuals, vessels, and non-terrorism
sanctions programs (Cuba, narcotics, etc.) are out of scope for this
register's Designation records.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from app.actors.contracts import DesignationRecord

BODY = "OFAC"
LIST_ID = "ofac-sdn"
LIST_URL = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN.CSV"
TERRORISM_PROGRAM_MARKERS = ("SDGT", "SDT", "FTO")

_ENT_NUM, _SDN_NAME, _SDN_TYPE, _PROGRAM = 0, 1, 2, 3


@dataclass
class OFACSDNHarvester:
    csv_path: Path

    def harvest(self) -> list[DesignationRecord]:
        records: list[DesignationRecord] = []
        with open(self.csv_path, encoding="latin-1", newline="") as f:
            for row in csv.reader(f):
                if len(row) <= _PROGRAM:
                    continue
                ent_num = row[_ENT_NUM].strip()
                sdn_name = row[_SDN_NAME].strip()
                sdn_type = row[_SDN_TYPE].strip()
                program = row[_PROGRAM].strip()

                if sdn_type != "-0-":
                    continue  # individuals/vessels/aircraft - Designation is for organizations
                if not any(marker in program for marker in TERRORISM_PROGRAM_MARKERS):
                    continue

                records.append(
                    DesignationRecord(
                        raw_org_name=sdn_name,
                        body=BODY,
                        label=program,
                        list_id=f"{LIST_ID}-{ent_num}",
                        url=LIST_URL,
                    )
                )
        return records
