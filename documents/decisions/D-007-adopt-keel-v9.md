# D-007 — Adopt Keel v9 as the governing discipline

**Date:** 2026-09-06
**Status:** Decided

## Decision

Adopt Keel v9 (`documents/keel-v9/KEEL-Build-First-Pattern-V9.md`, transcribed from the Owner-supplied `KEEL-Build-First-Pattern-Deck-V9.pptx`, both filed under `documents/keel-v9/`) as the version this project follows, superseding v6. Keel v5 and v6 remain in `documents/keel-v5/` and `documents/keel-v6/` as historical record; this project has no v7 or v8 artifacts — v9 is the next version actually supplied.

v9 restates the eleven principles in deck form rather than the three-document (Build-First Pattern / Day-One Checklist / Quick Reference) structure v5 and v6 used, and adds explicit content not present in v6: the Planner/Builder distinction (three-players model), the public-while-building / private-when-real tripwire (Principle 10), and Principle 11 ("when it outgrows your eyes" — five moves for verification at scale). The five standing documents (architecture/decisions/findings/testplan/assumptions) and the numbered principle structure v6 established are carried forward unchanged.

## Context

The Owner asked Code to ground itself in Keel v9 before conducting the "merge on green" gate proof (Principle 6 / Principle 9 / the deck's "one demo that matters," Slide 16). The v9 deck existed only as an untracked `.pptx` file sitting in the local working directory (`C:\Projects\Project MESG`), never committed. Per Principle 7 (a record nobody can find is a record that doesn't exist) and Principle 1 (one canonical copy), it needed to be in version control and in a form searchable/readable the way v5 and v6 already are, before being relied on as the governing text.

## Options rejected

- **Leave the deck as an untracked local file** and just read it once for this session. Rejected — it would remain invisible to the Planner (which only reads what's committed and connected) and to any future session, violating Principle 7 exactly the way the deck itself warns against.
- **Commit only the `.pptx`, no markdown transcript.** Rejected — a binary slide deck is not greppable or diffable, and v5/v6 both set the precedent of plain-markdown governing text. The transcript is the primary reference; the `.pptx` is kept alongside as the source artifact.
- **Renumber/restructure v9 to match v6's three-document format.** Rejected as unnecessary rewriting of the Owner-supplied source text; the deck's own structure (eleven principles, "the one demo that matters," daily rituals, Part C) is preserved as authored.

## Evidence

- `documents/keel-v9/KEEL-Build-First-Pattern-Deck-V9.pptx` — the Owner-supplied source deck (28 slides), present in the working directory as of 2026-09-06.
- `documents/keel-v9/KEEL-Build-First-Pattern-V9.md` — full markdown transcript produced this session.
- Owner instruction, this session, 2026-09-06: "First thing I want you to do is ground yourself in Keel v9 principles, conduct the test for merging on green."
- `documents/decisions/D-006-adopt-keel-v6.md` — the precedent this decision follows for filing a new Keel version alongside prior versions rather than overwriting them.

## Supersedes

Governing-version status only: MESG now follows Keel v9, not v6. The v5 and v6 text are not overturned or deleted; they remain in `documents/keel-v5/` and `documents/keel-v6/` as prior versions.
