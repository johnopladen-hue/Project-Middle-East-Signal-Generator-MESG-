# Decisions Log — Project MESG

> Every material decision made during development goes here, in chronological order (newest at bottom). Include the date, the decision, the reasoning, and alternatives considered/rejected when relevant.

## 2026-08-02 — Repository initialization

- **Decision:** Initialized the project by cloning the existing (empty except README/.gitignore) GitHub remote `johnopladen-hue/Project-Middle-East-Signal-Generator-MESG-` into `C:\projects\Project MESG`, rather than running `git init` fresh.
- **Why:** A remote already existed for the project; cloning keeps local and remote in sync from day one.

## 2026-08-02 — Documentation structure

- **Decision:** Created a `documents/` directory at the repo root to hold all build orders, TDDs, close-out docs, pre-work docs, and the four standing root documents (`architecture.md`, `decisions.md`, `findings.md`, `test_plan.md`).
- **Why:** Establishes a single, version-controlled location for all project knowledge so both Claude Code and the "Planner" (Claude.ai project) workflow have a consistent handoff point.

## 2026-08-02 — Working model with "Planner"

- **Decision:** Build orders and TDDs are authored collaboratively in a Claude.ai project called "Planner," delivered to the user's Downloads folder, and then moved into `documents/` in this repo. Claude Code reads and analyzes each doc, returns feedback (relayed to Planner by the user), and only executes/code once the user issues an explicit execute order.
- **Why:** Keeps design/planning and execution as separate, reviewable steps; avoids Claude Code coding against unreviewed or unstable specs.

## 2026-08-02 — Security model (v1)

- **Decision:** Start with simple username/password authentication; recipient list for email/SMS alerts is a manually curated whitelist.
- **Why:** Minimize early complexity; harden later as the system matures. Revisit before any production/public exposure.

## Open Decisions / Pending

- [ ] Tech stack (backend, frontend, data store, translation/NLP approach) — pending first build order/TDD.
- [ ] Full text of **Keel v5** principles — to be provided and filed for daily grounding.
- [ ] Full definition of **CORE** framework — to be provided and filed for daily grounding.
- [ ] SMS/email delivery provider(s).
- [ ] Source list / language coverage for Middle East discourse ingestion.
