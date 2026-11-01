"""The triage translation job (D-016, U-2).

`translate_pending` works through `records.pending_items` newest first,
writes `RawItem.working_text` plus one TranslationRecord per attempt, and
commits per batch. `python -m app.translation.run --once` runs it alone
over the whole backlog; `python -m app.ingest --once` runs it after
collection.
"""

from __future__ import annotations

import sys
import time
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.interfaces import Translator
from app.models import RawItem, TranslationRecord, TranslationStatus
from app.translation.nllb import MAX_TRIAGE_TOKENS, triage_excerpt
from app.translation.records import pending_items


@dataclass
class TranslateRunResult:
    by_status: Counter = field(default_factory=Counter)
    by_language_status: Counter = field(default_factory=Counter)  # (lang, status) -> n
    elapsed_s: float = 0.0

    @property
    def attempted(self) -> int:
        return sum(self.by_status.values())


def _record(db: Session, result: TranslateRunResult, translator: Translator, item: RawItem, src_code: str,
            status: TranslationStatus, error: str | None = None) -> None:
    db.add(TranslationRecord(raw_item_id=item.id, engine=translator.engine, model_sha256=translator.model_sha256,
                             src_code=src_code, status=status.value, error=error))
    result.by_status[status.value] += 1
    result.by_language_status[(item.original_lang, status.value)] += 1


def _translate_group(db: Session, translator: Translator, items: list[RawItem], lang: str,
                     result: TranslateRunResult, max_tokens: int) -> None:
    try:
        src_code = translator.language_code(lang)
    except Exception as exc:
        for item in items:
            _record(db, result, translator, item, lang, TranslationStatus.FAILED, f"{type(exc).__name__}: {exc}")
        return

    excerpts = [triage_excerpt(item.original_text, translator.count_tokens, max_tokens) for item in items]
    try:
        outputs: list[str | Exception] = list(translator.translate_batch([text for text, _ in excerpts], lang))
    except Exception:
        # Isolate the failure: one bad item must not fail its whole batch.
        outputs = []
        for text, _ in excerpts:
            try:
                outputs.append(translator.translate(text, lang))
            except Exception as exc:
                outputs.append(exc)

    for item, (_, truncated), output in zip(items, excerpts, outputs):
        if isinstance(output, Exception):
            _record(db, result, translator, item, src_code, TranslationStatus.FAILED,
                    f"{type(output).__name__}: {output}")
        elif not output.strip():
            _record(db, result, translator, item, src_code, TranslationStatus.FAILED, "empty translation output")
        else:
            item.working_text = output
            status = TranslationStatus.OK_TRUNCATED if truncated else TranslationStatus.OK
            _record(db, result, translator, item, src_code, status)


def translate_pending(db: Session, translator: Translator, batch_size: int = 32, limit: int | None = None,
                      *, max_tokens: int = MAX_TRIAGE_TOKENS) -> TranslateRunResult:
    """Each pending item is attempted at most once per run: the pending set
    is fixed at the start, so a failure is retried by the *next* run, up to
    records.MAX_ATTEMPTS in total."""
    start = time.monotonic()
    result = TranslateRunResult()

    query = pending_items(db).with_entities(RawItem.id)
    if limit is not None:
        query = query.limit(limit)
    item_ids = [item_id for (item_id,) in query]

    for offset in range(0, len(item_ids), batch_size):
        chunk = item_ids[offset : offset + batch_size]
        by_id = {item.id: item for item in db.query(RawItem).filter(RawItem.id.in_(chunk))}
        ordered = [by_id[item_id] for item_id in chunk]

        groups: dict[str, list[RawItem]] = {}
        for item in ordered:
            groups.setdefault(item.original_lang, []).append(item)
        for lang, items in groups.items():
            _translate_group(db, translator, items, lang, result, max_tokens)
        db.commit()

    result.elapsed_s = time.monotonic() - start
    return result


def print_report(result: TranslateRunResult) -> None:
    rate = result.attempted / result.elapsed_s if result.elapsed_s else 0.0
    print(f"Translation (NLLB triage): {result.attempted} items, {result.elapsed_s:.1f}s wall-clock, {rate:.2f} items/s")
    print("  " + " ".join(f"{status}={result.by_status.get(status, 0)}" for status in ("ok", "ok_truncated", "failed")))
    for (lang, status), count in sorted(result.by_language_status.items()):
        print(f"  {lang:4s} {status:14s} {count}")


def main() -> None:
    if "--once" not in sys.argv:
        print("Usage: python -m app.translation.run --once [--limit N]", file=sys.stderr)
        raise SystemExit(1)
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None

    from app.database import SessionLocal, init_db
    from app.translation.nllb import NllbModelMissing, NllbTranslator

    init_db()
    try:
        translator = NllbTranslator()
    except NllbModelMissing as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    with SessionLocal() as db:
        result = translate_pending(db, translator, limit=limit)
    print_report(result)


if __name__ == "__main__":
    main()
