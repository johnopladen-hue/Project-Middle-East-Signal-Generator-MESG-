# D-001 — Decision-log structure

**Date:** 2026-08-02
**Status:** Decided

## Decision

Adopt Keel v5's numbered decision-log structure: one file per decision under `documents/decisions/`, named `D-NNN-slug.md`, each carrying five fields (decision, context, options rejected, evidence, supersedes). `documents/decisions.md` becomes an index/table of contents that lists and links to the D-files, rather than being the log itself.

The project's root documentation folder stays named `documents/` — **not** the literal `docs/` used in the Keel v5 text. Keel's mechanics (numbering, five fields, recoverability) are adopted in full; the folder name is not, because `documents/` is already the committed root referenced throughout this repo (`architecture.md`, `findings.md`, `test_plan.md`, `documents/keel-v5/`, `documents/sessions/`) and in both Planner session docs. Renaming it would break those references for no functional gain — Keel's intent is the log mechanics, not the literal string "docs".

## Context

Keel v5 Principle 7 / Day-One Checklist Step 8 prescribes `docs/decisions/` with numbered D-files, each recording the decision, the context that forced it, the rejected alternatives, the supporting evidence, and what it supersedes — specifically so a later reader can navigate to "the last good decision" instead of re-deriving reasoning from memory.

MESG's day-one build order (issued before Keel v5's text had been provided to Builder) instead specified a single consolidated `decisions.md`. Once Keel v5 was filed into the repo, Planner flagged this as a genuine divergence in `documents/sessions/MESG-close-out-2026-08-02.md` §5, called it "the Owner's call," and recommended adopting Keel's numbered structure while keeping `decisions.md` as an index. The Owner directed, in this session (2026-08-02): "Adopt the Keel structure for D-001 and set up docs/decisions/."

## Options rejected

- **Keep the single consolidated `decisions.md` as-is**, accepting the divergence from Keel. Rejected because the project explicitly runs under Keel v5 discipline, and Keel is emphatic that the numbering, the rejected-options field, and the supersedes field are what make the log *recoverable* — not decoration.
- **Literally rename `documents/` to `docs/`** to match the Keel text verbatim. Rejected because `documents/` is already the committed, cross-referenced root of this repo's documentation (four standing docs, `keel-v5/`, `sessions/`, and both existing Planner session docs all reference it by that name). A rename buys literal textual compliance at the cost of breaking every existing reference, with no improvement to the actual mechanism Keel cares about.

## Evidence

- `documents/sessions/MESG-close-out-2026-08-02.md` §5 — Planner's flag of the divergence and its recommendation.
- `documents/keel-v5/KEEL-1-The-Build-First-Pattern-V5.md` — Principle 7 ("Write the decision down before the work is done").
- `documents/keel-v5/KEEL-2-The-Day-One-Checklist-V5.md` — Step 8 ("A safe place for decisions").
- Owner instruction, this session, 2026-08-02: "Adopt the Keel structure for D-001 and set up docs/decisions/."

## Supersedes

None (first D-file).
