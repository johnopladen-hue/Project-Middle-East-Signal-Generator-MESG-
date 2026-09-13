# MESG — Session Close-Out: First Article on Localhost

**Date:** 2026-09-13
**Session type:** Code session — executed `MESG-First-Article-Localhost-Orders-v0.1.md`
**Roles present:** Owner + Code (Claude Code, local). Planner not in this session.
**Keel version:** v9

---

## 1. Purpose of this session

Execute the Planner's first-article orders: get the already-built application (full FastAPI backend + React/Vite frontend, complete through Order 11) running and inspectable on localhost with synthetic data, and resolve the long-open hosting-platform decision along the way.

## 2. What we did

**O-A/O-B — D-011 and A-003.** Committed [D-011](../decisions/D-011-hosting-platform-and-deploy-mechanism.md) — hosting platform is Fly.io (not yet built/proven); localhost is the *development* environment only, not an automated deploy target; no local deploy agent is built. This corrects an earlier same-day draft of D-011 (a local pull-restart auto-deploy agent) that the Planner reviewed and rejected before it was committed — see the "Context" section of the D-011 file for how that correction is folded in. Registered [A-003](../assumptions.md) — CI-green + local-run is not proof the Fly deploy path works.

**O-1 — Grounding.** Live `origin/main` HEAD confirmed at `4eac25f` (unchanged since the snapshot this order was grounded on). Highest existing decision was D-010, highest assumption A-002 — both D-011 and A-003 confirmed free before writing them.

**O-2 — One-command local run.** `scripts/dev.py` starts backend (`uvicorn`, :8000) and frontend (`vite`, :5173) together; `README.md` documents the one-time setup and the run command. Named the dev/prod database divergence (SQLite file locally, PostgreSQL planned per D-009) as a known risk in `architecture.md`, rather than leaving it silent.

**O-3 — Synthetic seed.** `backend/app/dev_seed.py` — 5 sources (1 deliberately silent, to exercise the pipeline-status indicator), 3 stories with real `Analysis`/`SourceAssessment`/`Divergence` rows (grades computed live via `grading.probability_grade`: 5, 3, 1), 3 signals (`new`/`reviewed`/`suppressed`), 2 briefs (daily + weekly), 3 recipients. Every row is prefixed `[SYNTHETIC — DEV SEED]`; no real data, no scraped content, no real contact details. Idempotent; `--reset` wipes and reseeds.

**O-4 — Manifest and inspect.** With both servers running and the seed loaded, walked every built surface via real HTTP calls against the live app (not mocks): login/session (`/auth/login`, `/auth/me`), pipeline status (silent-source count correct), daily + weekly briefs, story detail with provenance resolution (`raw_item_ids` → full raw-item entries, original-language text + translation) and the divergence panel, the contradicted-evidence story (grade 1), signals list/filter, a live admin release action (`new` → `released`), and admin sources/recipients/settings. Full detail and exact responses are in `documents/findings.md`'s 2026-09-13 entry.

**O-5/O-6 — Recorded honestly.** `findings.md` has the first-article verification entry, plus a second entry on a real bug found along the way: the backend's `severity_for()` classifier emits values (`"medium"`, `"none"`) the frontend's `SeverityMark` doesn't recognize (falls back to generic "Info" styling) — not fixed here, just named. `test_plan.md`'s "deliberately not covered" section now states plainly: the merge-on-green gate is proven (T-001); automated deploy to Fly is not covered until Fly exists (A-003).

**O-7 — This close-out.**

## 3. Which of the five documents changed today

All five: `architecture.md` (dev/prod DB risk, tech-stack table, revision log), `decisions.md` + `decisions/D-011-*.md` (new decision), `assumptions.md` (A-003), `findings.md` (two new entries), `test_plan.md` (deploy-status line corrected).

## 4. Verified live state (this session's grounding)

- **Live `origin/main` HEAD:** `4eac25f30e61cf0aa5eff9c07279148ff93bc510` (unchanged by this session's commits, which are on branch `first-article-orders`, not yet merged — see open items).
- **Highest decision after this session:** D-011.
- **Highest assumption after this session:** A-003.
- **Local run command:** `backend\.venv\Scripts\python scripts\dev.py` from the repo root (one-time setup in `README.md`).
- **What the Owner can open in a browser:** http://localhost:5173/ (log in `analyst` / `correct-password`) — backend on :8000, frontend on :5173, both left running at the end of this session.
- **45/45 backend pytest** still pass with the seed module present (untouched by the test suite itself).

## 5. Open items → carried to next session

1. **Merge outstanding PRs.** This session's branch (`first-article-orders`) and the prior feedback branch (PR #19, still open) both need a human merge — the Claude Code auto-mode classifier categorically blocks `gh pr merge` from this session (also true for Scheduled-Task-registration scripts and `.github/workflows/*.yml` edits, encountered and abandoned earlier this session once the local-deploy-agent approach was withdrawn).
2. **Severity vocabulary mismatch** (`findings.md`, 2026-09-13) — `severity_for()` vs. `SeverityMark`'s four-value vocabulary. Not fixed; next touch of the classifier should reconcile it.
3. **Visual/browser verification.** No browser automation was available this session; every screen was verified through its real API responses, not by looking at rendered pixels. The Owner should open http://localhost:5173/ directly to confirm.
4. **Next planned work per the orders:** the MMP actor-network layer addendum (gated on a forthcoming TDD addendum + D-012) — not more feature work on top of this first article.

---

*This close-out is the baton. Commit it to the repo. Next session starts by reading it.*
