"""Fake provider implementations for the self-contained test suite (Keel Principle 5).

These are test doubles, not stubs of a specific real vendor — swapping in a
real Translator/Analyst/EmailProvider/SmsProvider later must not require
changing any test that uses these fakes.
"""

from __future__ import annotations

from app.interfaces import Analyst, EmailProvider, SmsProvider, Translator


class FakeTranslator(Translator):
    def translate(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        return f"[{source_lang}->{target_lang}] {text}"


class FakeAnalyst(Analyst):
    def __init__(self, has_corroborating_artefact: bool = False):
        self.has_corroborating_artefact = has_corroborating_artefact

    def analyze(self, story_items: list[str]) -> dict:
        return {
            "facts": [{"text": item, "raw_item_ref": i} for i, item in enumerate(story_items)],
            "analysis_text": "fake analysis of {} item(s)".format(len(story_items)),
            "contrary_evidence": "",
            "has_corroborating_artefact": self.has_corroborating_artefact,
        }


class FakeEmailProvider(EmailProvider):
    def __init__(self):
        self.sent: list[tuple[str, str, str]] = []

    def send(self, to_address: str, subject: str, body: str) -> bool:
        self.sent.append((to_address, subject, body))
        return True


class FakeSmsProvider(SmsProvider):
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send(self, to_number: str, body: str) -> bool:
        self.sent.append((to_number, body))
        return True
