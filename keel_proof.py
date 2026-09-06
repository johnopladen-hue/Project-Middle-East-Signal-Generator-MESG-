"""Phase 0 Keel-gate scaffold — not MESG feature code.

Exists only to give the CI gate (documents/test_plan.md, Keel Principles 2/6/9)
something self-contained to run before any real component is built. Safe to
delete once Phase 1 introduces real, tested components (see
documents/tdds/MESG-TDD-v0.1.md, Phase 0 note).
"""


def ping() -> str:
    return "ok"
