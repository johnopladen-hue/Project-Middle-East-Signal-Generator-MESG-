"""Approved-source seeder tests (D-021, Approved-Sources orders S-3).
Self-contained, isolated temp SQLite (Keel Principle 5)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from app.database import SessionLocal, init_db
from app.models import Source
from app.sources.seed_approved import SourceValidationError, load_sources, seed_approved, validate

init_db()


def _write_yaml(tmp_path: Path, sources: list[dict]) -> Path:
    path = tmp_path / "sources.yaml"
    path.write_text(yaml.safe_dump({"sources": sources}), encoding="utf-8")
    return path


_VALID_ROW = dict(
    key="test_native",
    name="Test Native Outlet",
    kind="rss",
    source_class="native",
    language="ar",
    url="https://example.test/native/feed",
)


def test_the_real_approved_set_loads_and_validates_with_the_expected_counts():
    result = seed_approved()
    assert result["total"] == 47
    assert result["by_kind"] == {"rss": 30, "telegram": 17}
    assert result["by_source_class"] == {"native": 33, "english_comparison": 14}
    assert sum(result["by_language"].values()) == 47


def test_reseeding_the_real_set_is_idempotent():
    seed_approved()
    with SessionLocal() as session:
        before = {
            s.seed_key: (s.name, s.url, s.active, s.credibility_prior)
            for s in session.query(Source).filter(Source.seed_key.isnot(None))
        }

    seed_approved()
    with SessionLocal() as session:
        after = {
            s.seed_key: (s.name, s.url, s.active, s.credibility_prior)
            for s in session.query(Source).filter(Source.seed_key.isnot(None))
        }

    assert before == after
    assert len(after) == 47


def test_a_manually_deactivated_source_survives_a_reseed():
    seed_approved()
    with SessionLocal() as session:
        source = session.query(Source).filter_by(seed_key="lbci_ar").first()
        source.active = False
        source.credibility_prior = 0.2
        session.commit()

    seed_approved()
    with SessionLocal() as session:
        source = session.query(Source).filter_by(seed_key="lbci_ar").first()
        assert source.active is False
        assert source.credibility_prior == 0.2


def test_duplicate_key_trips_validation(tmp_path):
    """Keel Principle 6: prove a bad row is rejected, not silently seeded."""
    rows = [dict(_VALID_ROW), dict(_VALID_ROW, url="https://example.test/native/other-feed")]
    path = _write_yaml(tmp_path, rows)
    with pytest.raises(SourceValidationError, match="duplicate key"):
        load_sources(path)


def test_duplicate_url_trips_validation(tmp_path):
    rows = [dict(_VALID_ROW), dict(_VALID_ROW, key="test_native_2")]
    path = _write_yaml(tmp_path, rows)
    with pytest.raises(SourceValidationError, match="duplicate url"):
        load_sources(path)


def test_unknown_kind_trips_validation():
    with pytest.raises(SourceValidationError, match="kind"):
        validate([dict(_VALID_ROW, kind="scraper")])


def test_unknown_source_class_trips_validation():
    with pytest.raises(SourceValidationError, match="source_class"):
        validate([dict(_VALID_ROW, source_class="unvetted")])


def test_pre_translated_without_translator_selector_trips_validation():
    with pytest.raises(SourceValidationError, match="translator_selector"):
        validate([dict(_VALID_ROW, source_class="pre_translated")])


def test_pair_missing_an_english_member_trips_validation():
    native_only = dict(_VALID_ROW, pair_id="test_pair")
    with pytest.raises(SourceValidationError, match="test_pair"):
        validate([native_only])


def test_pair_with_two_non_english_members_trips_validation():
    a = dict(_VALID_ROW, key="a", url="https://example.test/a", pair_id="test_pair")
    b = dict(_VALID_ROW, key="b", url="https://example.test/b", pair_id="test_pair")
    with pytest.raises(SourceValidationError, match="test_pair"):
        validate([a, b])


def test_a_valid_pair_passes_validation():
    native = dict(_VALID_ROW, key="a", url="https://example.test/a", pair_id="test_pair")
    english = dict(_VALID_ROW, key="b", url="https://example.test/b", pair_id="test_pair", language="en")
    validate([native, english])  # does not raise
