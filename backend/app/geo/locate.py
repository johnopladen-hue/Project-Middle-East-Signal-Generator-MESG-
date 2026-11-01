"""Locate pending items (D-023, map item geolocation).

Writes one `ItemLocation` per RawItem: "located" with the place its original
text names, or "none". An item is pending if it has no row yet, or its row
came from an older gazetteer build, so rebuilding the gazetteer re-checks
everything on the next run. Run alone with `python -m app.geo.locate --once`,
as the scheduler's `locate` job, or as the last step of `app.ingest --once`.
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.geo.gazetteer import GAZETTEER_PATH, Gazetteer, load_gazetteer
from app.models import ItemLocation, RawItem

BATCH_SIZE = 500


def gazetteer_version() -> str:
    return hashlib.sha256(GAZETTEER_PATH.read_bytes()).hexdigest()[:12]


@dataclass
class LocateResult:
    checked: int = 0
    located: int = 0
    by_precision: dict[str, int] = field(default_factory=dict)

    @property
    def not_located(self) -> int:
        return self.checked - self.located


def locate_pending(db: Session, *, gazetteer: Gazetteer | None = None, version: str | None = None) -> LocateResult:
    gazetteer = gazetteer or load_gazetteer()
    version = version or gazetteer_version()
    result = LocateResult()

    current = db.query(ItemLocation.raw_item_id).filter(ItemLocation.gazetteer_version == version)
    pending = db.query(RawItem).filter(~RawItem.id.in_(current)).order_by(RawItem.id)
    existing = {row.raw_item_id: row for row in db.query(ItemLocation).filter(ItemLocation.gazetteer_version != version)}

    for item in pending.yield_per(BATCH_SIZE):
        match = gazetteer.locate(item.original_text)
        row = existing.get(item.id) or ItemLocation(raw_item_id=item.id)
        row.gazetteer_version = version
        row.located_at = datetime.now(timezone.utc)
        if match is None:
            row.status = "none"
            row.geonameid = row.place_name = row.country = row.precision = None
            row.latitude = row.longitude = row.matched_text = row.in_headline = None
        else:
            place = match.place
            row.status = "located"
            row.geonameid, row.place_name, row.country, row.precision = place.geonameid, place.name, place.country, place.precision
            row.latitude, row.longitude = place.lat, place.lon
            row.matched_text = match.matched_text[:255]
            row.in_headline = match.in_headline
            result.located += 1
            result.by_precision[place.precision] = result.by_precision.get(place.precision, 0) + 1
        db.add(row)
        result.checked += 1
    db.commit()
    return result


def print_report(result: LocateResult) -> None:
    print(
        f"Locate: {result.checked} items checked, {result.located} located "
        f"({', '.join(f'{p} {n}' for p, n in sorted(result.by_precision.items())) or 'none'}), "
        f"{result.not_located} with no place name matched"
    )


def main() -> None:
    if "--once" not in sys.argv:
        print("Usage: python -m app.geo.locate --once", file=sys.stderr)
        raise SystemExit(1)
    from app.database import SessionLocal, init_db

    init_db()
    with SessionLocal() as db:
        print_report(locate_pending(db))


if __name__ == "__main__":
    main()
