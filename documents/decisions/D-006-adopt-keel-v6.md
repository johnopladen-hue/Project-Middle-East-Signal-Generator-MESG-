# D-006 — Adopt Keel v6 as the governing discipline

**Date:** 2026-08-02
**Status:** Decided

## Decision

Author Keel v6, extending v5 with two new principles/steps — a standing **findings log** (`findings.md`, dated context/finding/implication entries) and a standing, tabular **test plan** (`test_plan.md`) — both elevated to the same non-negotiable status as the decision log. Keel v5's original three documents are kept unmodified in `documents/keel-v5/` as historical record; v6 lives alongside in `documents/keel-v6/` and is now the version this project follows. Copies of all three v6 documents were also placed in the Owner's Downloads folder.

## Context

MESG's own documentation structure already had `findings.md` and `test_plan.md` as standing root documents (see [D-003](./D-003-documentation-directory-structure.md)), but Keel v5's text only formally prescribed this treatment for decisions (Principle 7 / Step 8). The Owner directed extending Keel itself to v6, generalizing the pattern MESG already used for decisions to findings and the test plan, and asked for the result to be available both in the repo and in Downloads.

## Options rejected

- **Edit the v5 files in place and rename to v6**, discarding v5. Rejected because Keel's own philosophy (Principle 7: decisions have a recoverable trail; nothing that mattered gets silently overwritten) argues against destroying the prior version of a governing document. Keeping v5 alongside v6 costs nothing and preserves exactly what changed and why.
- **Insert the new findings/test-plan steps without renumbering** (e.g., "Step 8a," "Step 8b"), to minimize diff noise against v5. Rejected in favor of a clean renumber (new Steps 9–10, old Steps 9–15 shifted to 11–17) because the Day-One Checklist and Quick Reference Card are meant to be followed top-to-bottom in strict step order — sub-lettered steps would break that linearity. The renumbering is called out explicitly at the top of both v6 documents so nothing is silently shifted.
- **Only update MESG's local usage**, without touching the Keel source documents themselves. Rejected — the Owner's instruction was explicit: modify the Keel documents and produce a new version, not just note the gap.

## Evidence

- Owner instruction, this session, 2026-08-02: "Modify the Keel 5 documents and update to version 6 with the new separate findings, decisions, and test plan documents. Make those available in downloads as well as in documents directory."
- `documents/decisions/D-003-documentation-directory-structure.md` — MESG already treated findings and test plan as standing root documents before this decision, which is what v6 generalizes.
- `documents/keel-v6/KEEL-1-The-Build-First-Pattern-V6.md`, `KEEL-2-The-Day-One-Checklist-V6.md`, `KEEL-3-Quick-Reference-Card-V6.md` — the authored v6 text.
- Files present at `C:\Users\johno\Downloads\KEEL-{1,2,3}-*-V6.md` as of 2026-08-02.

## Supersedes

Governing-version status only: MESG now follows Keel v6, not v5. The v5 text itself is not overturned or deleted — it remains in `documents/keel-v5/` as the prior version v6 was built from.
