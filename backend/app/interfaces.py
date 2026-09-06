"""Provider interfaces — TDD §4.2/§4.4/§4.7, Design Principle 3.

No component's unit tests touch the network or a live service (Keel
Principle 5). Every external dependency MESG has — translation, LLM
analysis, email, SMS — sits behind one of these interfaces. Real
implementations get wired in once the corresponding vendor decision is
made (see documents/decisions.md open list); tests always use the fakes
in app/fakes.py.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Translator(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        """Translate `text` into `target_lang`, preserving the original elsewhere (TDD §4.2)."""


class Analyst(ABC):
    @abstractmethod
    def analyze(self, story_items: list[str]) -> dict:
        """Produce a structured analysis dict for a cluster of related items (TDD §4.4).

        Expected keys: facts (list[dict]), analysis_text (str),
        contrary_evidence (str), has_corroborating_artefact (bool).
        The probability grade itself is computed by app.grading.probability_grade,
        not by the Analyst — grading is a deterministic rule, not an LLM judgment
        call, per the TDD §9.2 guardrail.
        """


class EmailProvider(ABC):
    @abstractmethod
    def send(self, to_address: str, subject: str, body: str) -> bool:
        """Send an email. Returns True on accepted send, False on failure."""


class SmsProvider(ABC):
    @abstractmethod
    def send(self, to_number: str, body: str) -> bool:
        """Send an SMS. Returns True on accepted send, False on failure."""
