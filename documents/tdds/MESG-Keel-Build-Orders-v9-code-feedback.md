# Code's feedback on MESG — Keel Build Orders (Doc ID ORD-001, Keel v9)

**Date:** 2026-09-13
**From:** Code (Claude Code, local)
**To:** Owner, to relay to Planner
**Status:** Orders NOT executed. Filed alongside the source document for the record.

---

## 1. Grounding performed before any action (Standing Order 1)

Per the orders document's own §0 ("Ground before you act... do not trust this document's description of the current tree"), the live repo was cloned fresh to `C:\MESG` and checked directly — not assumed from the document's description. Artefacts:

- `git log --oneline -5` at clone time: HEAD `4eac25f`, "Merge pull request #18 from johnopladen-hue/order11-accessibility-pass".
- `find . -not -path './.git/*' -type f` — 129 tracked files: a full `backend/app/` (FastAPI, 6 routers, models, database, delivery, grading, signals, auth) with 13 test files under `backend/tests/`, and a full `frontend/src/` (React/Vite, routes, domain components, primitives, API client) with test files alongside each component; `documents/` with the five-document set plus `decisions/`, `keel-v5/`, `keel-v6/`, `keel-v9/`, `sessions/`, `tdds/`, `reference/`.
- `documents/decisions.md` — 10 rows, D-001 through D-010, all status "Decided."
- `documents/assumptions.md` — A-001, A-002 registered, each with a falsifying test.
- `documents/findings.md` — 5 dated entries, 2026-08-02 through 2026-09-06.
- `gh pr list --state all` — 18 PRs, all MERGED, through #18 "Order 11: accessibility and responsive pass."
- `gh api repos/.../rulesets` — one active ruleset (id `21864750`) on `main`, created 2026-08-30, updated 2026-09-06.
- `gh api repos/.../branches/main/protection` — 404 "Branch not protected" (the repo uses the newer rulesets API instead of classic branch protection; the ruleset above is what's actually enforcing).
- `.github/workflows/ci.yml` — `test-backend` (pytest), `test-frontend` (npm lint + test), `deploy` (placeholder, gated on both tests passing on push to `main`).
- `documents/findings.md`, 2026-09-06 entry — records the Principle 6/9 gate proof witnessed for real on PR #4: a broken test produced `mergeable_state: "blocked"`, a plain `gh pr merge` was refused by base-branch policy even for the repo owner, an attempted `gh pr merge --admin` override was independently blocked by the Claude Code auto-mode permission classifier, then the fix went green and merged.

## 2. Finding: the orders document does not match the ground it names as authoritative

`MESG-Keel-Build-Orders-v9.md` (dated 2026-09-13, same day) directs laying the Keel from an empty repo — no `docs/`, no decisions, no CI, no branch protection, no tests — across O-1 through O-15, with feature work explicitly held until O-15 passes (§0, §7, §8). None of that matches what §1 above shows. Specifically:

- **O-1** asks to confirm "no `docs/` yet" and grep for orphaned `D-`/`A-` citations. There is no `docs/` (the project uses `documents/`, per D-001/D-003), and grepping the live repo returns 10 clean, non-orphaned decisions and 2 assumptions, not an empty log.
- **O-2/O-3** direct creating `docs/architecture.md`, `decisions.md`, `findings.md`, `testplan.md`, `assumptions.md` and seeding **D-001 through D-004** with new content (docs structure, adopt-Keel-v9, MMP-as-UX-reference, MMP-not-scraped). `documents/decisions/D-001-decision-log-structure.md` through `D-010-frontend-decisions.md` already exist with unrelated, already-ratified content. Writing the new D-001–D-004 content over these numbers would not "seed" a log — it would overwrite ten resolved decisions with different ones under the same numbers, breaking the exact recoverability property (D-001's own text: "we were sound up to D-023") the numbering exists to protect.
- **O-8/O-9** direct standing up a one-endpoint keel-proof FastAPI app and a first-time CI gate, logging **D-005 through D-008**. The live `backend/app/main.py` already serves a real application (auth, briefs, pipeline, recipients, signals, stories, admin), CI already runs pytest + frontend lint/test, and D-005–D-008 are already taken (v1 security model, Keel v6 adoption, v1 source scope, v1 technology stack — see `documents/decisions.md` rows 5–8).
- **O-11/O-12** direct proving the gate for the first time and turning on branch protection for the first time. Both are already done and already recorded: the 2026-09-06 `findings.md` entry above is that exact proof, and the active ruleset (id `21864750`) is that exact protection.
- **§7/§8 ("all feature work — nothing starts before O-15 passes")** — feature work is not pending; it is complete through Order 11 of the *actual* build orders (`documents/tdds/MESG-UI-Spec-and-Claude-Code-Orders-v0.1.md`), merged as PRs #7 through #18.

## 3. This is the same failure mode `findings.md` already names twice

- 2026-08-02 entry: Planner asserted a file was visible in the connected repo when it was not.
- 2026-08-09 entry: a TDD carried forward a decision (D-001) and a Keel version as still-open when both had already been resolved earlier the same session.
- **This document is a third instance, more consequential than the first two**: it doesn't just carry forward one stale fact, it re-derives an entire day-one bootstrap sequence — decisions, doc structure, CI, branch protection — against a repo that finished that sequence a week earlier. The 2026-08-09 entry's own proposed fix ("Planner should explicitly re-read `documents/decisions.md` before drafting a new build order") would have caught this.

## 4. Disposition

Per Owner direction (2026-09-13): **do not execute.** No files were created or modified in `documents/`, `backend/`, or `frontend/`; no branches, decisions, or CI/branch-protection changes were made beyond filing this feedback and the source document itself. This feedback and the source orders document are committed together so the Planner can ground on both directly from the connected repo, per the working model in [D-004](../decisions/D-004-planner-builder-working-model.md).

## 5. Recommendation to relay to Planner

Re-read `documents/decisions.md` (currently D-001–D-010), `documents/findings.md`, and `documents/assumptions.md` (currently A-001–A-002) before drafting the next build order. If any idea in the v9 orders doc is still live and genuinely undecided today — the clearest candidate is **hosting platform** (the CI `deploy` job is still a placeholder; no D-entry commits to Fly.io or any other host) — reframe it as a new decision proposal appended after **D-010**, not a re-issue of D-001–D-008.
