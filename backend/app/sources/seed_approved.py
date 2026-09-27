"""Seeder for MESG's v1 approved source set (D-021, Approved-Sources orders S-3).

These are real rows - no [SYNTHETIC - DEV SEED] tag (app.dev_seed's tag is
reserved for throwaway demo data, D-021's set is the Owner-approved real
collection list). Idempotent: upserts on Source.seed_key, so re-running the
seeder against unchanged data changes nothing - `active` and
`credibility_prior` are only set on first insert, never overwritten on
update, so a manual admin edit (deactivating a source, adjusting its prior)
survives a reseed.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from app.database import SessionLocal
from app.models import Source

DATA_FILE = Path(__file__).parent / "approved_sources_v1.yaml"

ALLOWED_KINDS = {"rss", "telegram", "corroboration"}
ALLOWED_CLASSES = {"native", "pre_translated", "english_comparison", "corroboration"}

# Source.type predates ingestion (O-4) and stays free-form; the seeder maps
# each approved row's `kind` onto it so the legacy column isn't left blank.
LEGACY_TYPE_BY_KIND = {"rss": "rss", "telegram": "discussion", "corroboration": "api"}


class SourceValidationError(ValueError):
    pass


def load_sources(data_file: Path = DATA_FILE) -> list[dict]:
    with data_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    sources = data["sources"]
    validate(sources)
    return sources


def validate(sources: list[dict]) -> None:
    """Fail loudly (Keel P6): a bad row must never seed quietly."""
    errors: list[str] = []
    seen_keys: set[str] = set()
    seen_urls: set[str] = set()
    pairs: dict[str, list[dict]] = {}

    for row in sources:
        key = row["key"]
        if key in seen_keys:
            errors.append(f"duplicate key: {key}")
        seen_keys.add(key)

        url = row["url"]
        if url in seen_urls:
            errors.append(f"duplicate url: {url}")
        seen_urls.add(url)

        if row["kind"] not in ALLOWED_KINDS:
            errors.append(f"{key}: kind {row['kind']!r} not in {sorted(ALLOWED_KINDS)}")
        if row["source_class"] not in ALLOWED_CLASSES:
            errors.append(f"{key}: source_class {row['source_class']!r} not in {sorted(ALLOWED_CLASSES)}")
        if row["source_class"] == "pre_translated" and not row.get("translator_selector"):
            errors.append(f"{key}: source_class=pre_translated requires translator_selector")

        pair_id = row.get("pair_id")
        if pair_id:
            pairs.setdefault(pair_id, []).append(row)

    for pair_id, members in pairs.items():
        non_english = [m for m in members if m["language"] != "en"]
        english = [m for m in members if m["language"] == "en"]
        if len(non_english) != 1:
            errors.append(f"pair_id {pair_id!r}: expected exactly 1 non-English member, found {len(non_english)}")
        if not english:
            errors.append(f"pair_id {pair_id!r}: expected at least 1 English member, found 0")

    if errors:
        raise SourceValidationError("; ".join(errors))


def _tally(sources: list[dict], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in sources:
        counts[row[field]] = counts.get(row[field], 0) + 1
    return counts


def seed_approved(db=None, data_file: Path = DATA_FILE) -> dict:
    """Upsert the approved set. Returns counts: total, by kind, by
    source_class, by language."""
    sources = load_sources(data_file)
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        for row in sources:
            existing = db.query(Source).filter_by(seed_key=row["key"]).first()
            synced_fields = dict(
                name=row["name"],
                url=row["url"],
                language=row["language"],
                dialect=row.get("dialect"),
                type=LEGACY_TYPE_BY_KIND[row["kind"]],
                region=row.get("region"),
                kind=row["kind"],
                source_class=row["source_class"],
                translator_selector=row.get("translator_selector"),
                pair_id=row.get("pair_id"),
                designation_note=row.get("designation_note"),
                verification_note=row.get("verification_note"),
            )
            if existing:
                for field, value in synced_fields.items():
                    setattr(existing, field, value)
            else:
                db.add(Source(seed_key=row["key"], active=True, **synced_fields))
        db.commit()

        return {
            "total": len(sources),
            "by_kind": _tally(sources, "kind"),
            "by_source_class": _tally(sources, "source_class"),
            "by_language": _tally(sources, "language"),
        }
    finally:
        if own_session:
            db.close()


if __name__ == "__main__":
    from app.database import init_db

    init_db()
    result = seed_approved()
    print(f"Seeded {result['total']} approved sources.")
    print(f"  by kind: {result['by_kind']}")
    print(f"  by source_class: {result['by_source_class']}")
    print(f"  by language: {result['by_language']}")
