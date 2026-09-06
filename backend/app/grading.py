"""Probability-of-truth grading — TDD §9.1/§9.2.

Deterministic by design: the LLM Analyst produces facts and evidence: this
module turns that evidence into the 1-5 grade. Keeping the arithmetic out of
the LLM's hands is what makes the corroboration cap enforceable and testable
— an LLM asked to "grade against contrary evidence" can be argued out of a
cap; a Python `min()` cannot.
"""

from __future__ import annotations

from app.models import SourceAccessLevel

_ACCESS_RANK = {
    SourceAccessLevel.DIRECT: 3,
    SourceAccessLevel.ONE_STEP: 2,
    SourceAccessLevel.AGGREGATOR: 1,
    SourceAccessLevel.COMMENTARY: 0,
}


def probability_grade(
    *,
    num_independent_sources: int,
    max_access_level: SourceAccessLevel,
    has_corroborating_artefact: bool,
    contradicted_by_better_evidence: bool = False,
    partial_contradiction: bool = False,
) -> int:
    """Return the 1-5 probability-of-truth grade for a story (TDD §9.2 table).

    `has_corroborating_artefact=False` caps the result at 3 regardless of
    source count or access, no matter how strong the other inputs look —
    this is the guardrail the TDD calls out by name, not a heuristic.
    """
    if contradicted_by_better_evidence:
        return 1

    access_rank = _ACCESS_RANK[max_access_level]

    if num_independent_sources >= 2 and access_rank >= _ACCESS_RANK[SourceAccessLevel.DIRECT]:
        grade = 5
    elif num_independent_sources >= 2 or access_rank >= _ACCESS_RANK[SourceAccessLevel.DIRECT]:
        grade = 4
    elif num_independent_sources == 1 and access_rank >= _ACCESS_RANK[SourceAccessLevel.ONE_STEP]:
        grade = 3
    else:
        grade = 2

    if partial_contradiction:
        grade = min(grade, 2)

    if not has_corroborating_artefact:
        grade = min(grade, 3)

    return grade
