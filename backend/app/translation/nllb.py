"""NLLB-200 triage translator (D-016 translation & analysis providers, U-2).

Free, local, CPU-only machine translation of headline + lede, good enough
to decide what deserves a deep read (A-008 - open until the O-3 bake-off).
Runs `facebook/nllb-200-distilled-600M` converted to CTranslate2 int8; the
weights are CC-BY-NC 4.0 and live in the gitignored `backend/models/`.

`ctranslate2` and `sentencepiece` are imported inside `NllbTranslator`
only (requirements-nllb.txt), so the rest of the app and the whole test
suite run without them or the model files (Keel P5).
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Callable
from pathlib import Path

from app.interfaces import Translator

ENGINE = "nllb-200-distilled-600M-ct2-int8"

# One map, recorded per translation. Levantine Arabic deliberately goes
# through Modern Standard Arabic (arb_Arab) today; whether NLLB's Levantine
# codes (apc_Arab / ajp_Arab) do better is a question for the O-3 bake-off.
LANGUAGE_CODES = {"ar": "arb_Arab", "fa": "pes_Arab", "he": "heb_Hebr"}
TARGET_CODE = "eng_Latn"

DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[2] / "models" / ENGINE
MODEL_FILES = ("model.bin", "sentencepiece.bpe.model")

# Triage, not full translation (D-016): roughly the first 400 sentencepiece
# tokens, cut on a sentence or line boundary.
MAX_TRIAGE_TOKENS = 400

_SENTENCE_END_RE = re.compile(r"(?<=[.!?؟])\s+")


class NllbModelMissing(RuntimeError):
    """The model files are absent - a hard error, never a silent skip (Keel P6)."""


def source_tokens(sp, text: str, src_code: str) -> list[str]:
    """The documented CTranslate2 NLLB input: language code, pieces, end marker."""
    return [src_code] + sp.encode(text, out_type=str) + ["</s>"]


def strip_target_prefix(tokens: list[str], target_code: str = TARGET_CODE) -> list[str]:
    """NLLB output starts with the forced target-language token; drop it."""
    return tokens[1:] if tokens and tokens[0] == target_code else tokens


def triage_excerpt(text: str, count_tokens: Callable[[str], int], max_tokens: int = MAX_TRIAGE_TOKENS) -> tuple[str, bool]:
    """The leading part of `text` that fits in `max_tokens`, cut on sentence
    or line boundaries. Returns (excerpt, truncated). Line breaks are kept,
    so a Telegram post's headline line stays its own line."""
    units: list[tuple[str, bool]] = []  # (sentence, ends its line)
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        sentences = [s for s in _SENTENCE_END_RE.split(line) if s]
        units.extend((sentence, i == len(sentences) - 1) for i, sentence in enumerate(sentences))

    kept: list[tuple[str, bool]] = []
    used = 0
    for sentence, ends_line in units:
        size = count_tokens(sentence)
        if used + size > max_tokens:
            if not kept:
                # A single over-long first sentence: keep its leading words.
                words = sentence.split()
                while len(words) > 1 and count_tokens(" ".join(words)) > max_tokens:
                    words = words[: max(1, len(words) * 4 // 5)]
                kept.append((" ".join(words), True))
            return _render(kept), True
        kept.append((sentence, ends_line))
        used += size
    return _render(kept), False


def _render(units: list[tuple[str, bool]]) -> str:
    lines: list[str] = []
    current: list[str] = []
    for sentence, ends_line in units:
        current.append(sentence)
        if ends_line:
            lines.append(" ".join(current))
            current = []
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


class NllbTranslator(Translator):
    engine = ENGINE

    def __init__(self, model_dir: str | Path | None = None, *, compute_type: str = "int8"):
        model_dir = Path(model_dir or os.environ.get("MESG_NLLB_MODEL_DIR") or DEFAULT_MODEL_DIR)
        missing = [name for name in MODEL_FILES if not (model_dir / name).is_file()]
        if missing:
            raise NllbModelMissing(
                f"NLLB model not found at {model_dir} (missing: {', '.join(missing)}); "
                "see U-2 of MESG-Orders-Usable-Today-v0.1.md for how to convert it."
            )

        import ctranslate2  # lazy: requirements-nllb.txt only
        import sentencepiece

        self.model_dir = model_dir
        self._sp = sentencepiece.SentencePieceProcessor(model_file=str(model_dir / "sentencepiece.bpe.model"))
        self._translator = ctranslate2.Translator(str(model_dir), device="cpu", compute_type=compute_type)
        self.model_sha256 = _sha256_file(model_dir / "model.bin")

    def language_code(self, source_lang: str) -> str:
        try:
            return LANGUAGE_CODES[source_lang]
        except KeyError:
            raise ValueError(f"no NLLB language code mapped for {source_lang!r}") from None

    def count_tokens(self, text: str) -> int:
        return len(self._sp.encode(text, out_type=str))

    def translate(self, text: str, source_lang: str, target_lang: str = "en") -> str:
        return self.translate_batch([text], source_lang, target_lang)[0]

    def translate_batch(self, texts: list[str], source_lang: str, target_lang: str = "en") -> list[str]:
        if target_lang != "en":
            raise ValueError(f"triage translates into English only, not {target_lang!r}")
        src_code = self.language_code(source_lang)

        # Line by line: NLLB is trained on sentence-level pairs, and a short
        # headline line translated alone stays a headline.
        segments: list[str] = []
        owners: list[int] = []
        for index, text in enumerate(texts):
            for line in text.splitlines():
                if line.strip():
                    segments.append(line.strip())
                    owners.append(index)

        outputs: list[list[str]] = [[] for _ in texts]
        if segments:
            results = self._translator.translate_batch(
                [source_tokens(self._sp, segment, src_code) for segment in segments],
                target_prefix=[[TARGET_CODE]] * len(segments),
                max_batch_size=32,
                beam_size=2,
                max_decoding_length=256,
            )
            for owner, result in zip(owners, results):
                outputs[owner].append(self._sp.decode(strip_target_prefix(result.hypotheses[0])))
        return ["\n".join(parts) for parts in outputs]
