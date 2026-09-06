"""Signal / alert engine — event taxonomy, TDD §4.5.

`classify_event_type` is a keyword-based placeholder standing in for the
Analyst-driven classification the real pipeline will use once the
analysis/LLM provider decision (documents/decisions.md open list) is made.
It exists so the taxonomy and severity rules are defined and testable now,
independent of that decision — swap the matching logic, keep the contract.
"""

from __future__ import annotations

EVENT_TAXONOMY = (
    "military_event",
    "natural_disaster",
    "incident",
    "outbreak",
    "assassination",
    "arrest_political_figure",
    "arrest_cultural_figure",
    "source_disappearance",
    "uprising",
    "coup",
)

_HIGH_SEVERITY = {"assassination", "coup", "military_event", "uprising"}

_KEYWORDS: dict[str, tuple[str, ...]] = {
    "coup": ("coup", "military takeover", "seized power"),
    "assassination": ("assassinat",),
    "military_event": ("airstrike", "shelling", "troop movement", "mobiliz"),
    "natural_disaster": ("earthquake", "flood", "wildfire"),
    "outbreak": ("outbreak", "epidemic", "cholera"),
    "arrest_political_figure": ("minister arrested", "president arrested", "arrested the leader"),
    "arrest_cultural_figure": ("arrested the singer", "arrested the actor", "arrested the writer"),
    "source_disappearance": ("went offline", "site taken down", "no longer publishing"),
    "uprising": ("uprising", "mass protest", "unrest spreading"),
}


def classify_event_type(text: str) -> str | None:
    """Return the matching taxonomy label, or None if no keyword hits."""
    lowered = text.lower()
    for event_type, keywords in _KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return event_type
    return None


def severity_for(event_type: str | None) -> str:
    if event_type in _HIGH_SEVERITY:
        return "high"
    if event_type is None:
        return "none"
    return "medium"
