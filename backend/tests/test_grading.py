from app.grading import probability_grade
from app.models import SourceAccessLevel


def test_confirmed_grade_requires_multiple_direct_sources_and_corroboration():
    grade = probability_grade(
        num_independent_sources=2,
        max_access_level=SourceAccessLevel.DIRECT,
        has_corroborating_artefact=True,
    )
    assert grade == 5


def test_corroboration_cap_applies_even_to_otherwise_perfect_evidence():
    """TDD §9.2 guardrail: no corroborating artefact => grade capped at 3,
    no matter how many high-access sources agree."""
    grade = probability_grade(
        num_independent_sources=5,
        max_access_level=SourceAccessLevel.DIRECT,
        has_corroborating_artefact=False,
    )
    assert grade == 3


def test_single_uncorroborated_source_is_unconfirmed():
    grade = probability_grade(
        num_independent_sources=1,
        max_access_level=SourceAccessLevel.ONE_STEP,
        has_corroborating_artefact=False,
    )
    assert grade == 3


def test_single_commentary_only_source_is_doubtful():
    grade = probability_grade(
        num_independent_sources=1,
        max_access_level=SourceAccessLevel.COMMENTARY,
        has_corroborating_artefact=False,
    )
    assert grade == 2


def test_contradicted_by_better_evidence_is_improbable_regardless_of_sources():
    grade = probability_grade(
        num_independent_sources=3,
        max_access_level=SourceAccessLevel.DIRECT,
        has_corroborating_artefact=True,
        contradicted_by_better_evidence=True,
    )
    assert grade == 1


def test_partial_contradiction_caps_at_doubtful():
    grade = probability_grade(
        num_independent_sources=2,
        max_access_level=SourceAccessLevel.DIRECT,
        has_corroborating_artefact=True,
        partial_contradiction=True,
    )
    assert grade == 2
