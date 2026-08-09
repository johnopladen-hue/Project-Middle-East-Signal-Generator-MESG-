# Code's feedback on TDD-001 (MESG v0.1)

**Date:** 2026-08-09
**Reviewer:** Code (Claude Code / Builder)
**Subject:** `documents/tdds/MESG-TDD-v0.1.md`
**Status:** Feedback for Owner to relay to Planner. No implementation has started — see the "Execution status" note at the end.

## Overall

This is a strong v0.1. It translates the CORE brief faithfully — provenance-first schema, the corroboration-capped grading scale, the in-region-vs-English-media divergence/convergence split, and the review-and-release gate are all direct, correctly-reasoned implementations of the brief and of Keel Principle 8 ("a summary is not knowing"). The design is internally consistent and the phasing (Phase 0 Keel-proven prerequisite → narrow MVP → SMS/weekly → breadth) is sound and appropriately conservative.

## Feasibility

No red flags. The architecture (scheduler → ingest → translate → analyze → store → signal/brief → delivery, with a REST API and a React frontend) is a standard, well-understood shape for this kind of pipeline. Interface-based `Translator`/`Analyst`/`EmailProvider`/`SmsProvider` boundaries are exactly right for Keel Principle 5 (self-contained tests) — every one of them is naturally mockable. Nothing in v0.1 requires unproven technology or an unusual architecture.

## Stack

The proposed stack (React + Vite [+TypeScript], Python + FastAPI, PostgreSQL, LLM-based translation/analysis behind interfaces, transactional email + programmable SMS APIs, PaaS hosting with a CI gate) is a conventional, well-supported choice and matches the Python-oriented `.gitignore` already in the repo. No objection to any of it; all still correctly marked **⟐ DECISION** pending Owner sign-off and a D-file, per Keel.

One vote, since it's asked for directly: **TypeScript over plain JS** for the frontend. The analytic data shapes (`Analysis`, `Divergence`, `Signal`, grade + contrary-evidence structures) are exactly the kind of nested, evolving payloads that benefit most from a type checker — a shape mismatch here is a wrong-analysis bug, not a cosmetic one. The Owner said "React.JS" — worth a direct check on whether that meant "the React framework" (compatible with TS) or "JavaScript specifically, not TypeScript."

## Data model

Coherent and traceable — every analytic artifact chains back to a `RawItem`, which is the right backbone for the provenance-first principle. Three things worth resolving before Code builds against this schema:

1. **`Analysis.facts_json` as a JSON blob.** Pragmatic for v1, but it means "which facts cite a given contested `raw_item_id`" isn't queryable without parsing JSON in application code. Fine for MVP; flag as a candidate for normalization (a `Fact` table) once query patterns are known — don't normalize prematurely.
2. **`Recipient` vs. `User` relationship is underspecified.** The TDD says a `Recipient` "may reference a `User` or stand alone," but doesn't say whether web-app login access and bulletin/email/SMS delivery are meant to be independent axes (e.g., can someone receive alerts without ever logging into the app, and vice versa?). Worth one sentence in the next TDD revision.
3. **`Story.event_type` vs. `Signal.type`.** Both appear to carry the bulletin taxonomy (military event, coup, etc.). Clarify whether `Story.event_type` is the analyst's classification and `Signal.type` is derived from it (in which case say so), or whether they're independently assigned (in which case say how they reconcile when they disagree).

None of these block moving forward — they're clarifications for TDD v0.2, not defects.

## Fit with Keel

Good alignment overall — the TDD explicitly cites Keel Principles 4, 5, 8, and 10 and applies them correctly (secrets in the platform, self-contained tests, the corroboration-capped grade, the Private-flip tripwire on real recipient PII). Two corrections:

1. **§15, item 1** says decision-log structure "(D-001, carried over)" is still pending. It isn't — **D-001 was resolved earlier in this session** (Keel's numbered `documents/decisions/D-NNN-slug.md` structure was adopted; see `documents/decisions/D-001-decision-log-structure.md`). This TDD was drafted from a close-out that predates that resolution, so the staleness is expected, not a Planner error — but the next Planner session should re-ground on the current `documents/decisions.md` index before drafting TDD v0.2, so this kind of stale carry-forward doesn't propagate into decision numbering.
2. **This project is on Keel v6, not v5** (`documents/keel-v6/`; see `documents/decisions/D-006-adopt-keel-v6.md`). The TDD header says "Keel version: v5" and doesn't yet reflect v6's two new principles (standing findings log, standing tabular test plan). Nothing in the TDD conflicts with v6 — §11 already points at a tabular `test_plan.md` — but the header should be updated, and TDD v0.2 should explicitly plan its build order against v6's step numbering (old Steps 9–15 are now 11–17) rather than v5's.

## Open ⟐ DECISION items (§15)

Confirmed count: 11 outstanding (hosting platform, backend framework, database, frontend language, translation provider, analysis/LLM provider, email provider, SMS provider, scheduler mechanism, auth mechanism, v1 source scope) — decision-log structure itself (the TDD's item 1) is already resolved, so it's 11, not 12, remaining. Per Keel and per the TDD's own sequencing note, each needs a D-file before Code builds against it. **Hosting platform first** — it gates Keel Part B (Steps 13–17: tests, the gate, prove-the-gate, branch protection, kill hand-deploy), and nothing in Part B can be witnessed until it's chosen.

## Execution status

The TDD's own sequencing note is explicit: **execution does not begin until Keel Part B is laid and every PROOF is witnessed**, and the document closes by asking Code to return feedback for the Owner to relay to Planner, with the execute order to follow *after* the Keel is proven. As of this session, Keel Part B is not yet laid (no hosting platform chosen, no tests, no gate, no branch protection) and none of the 11 open ⟐ DECISION items have been logged. Per the working model this project already established ([D-004](../decisions/D-004-planner-builder-working-model.md)), this feedback is what goes back to Planner — implementation starts on an explicit Owner execute order after that loop closes, not automatically on receipt of the TDD.
