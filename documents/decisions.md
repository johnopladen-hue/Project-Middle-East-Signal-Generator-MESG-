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

- [ ] **D-001 candidate — decision-log structure.** Keel v5 (Principle 7 / Step 8) prescribes `docs/decisions/` with one numbered file per decision (D-001, D-002…; five fields: decision, context, options rejected, evidence, supersedes). This project currently uses a single consolidated `decisions.md` instead. Flagged by Planner in `documents/sessions/MESG-close-out-2026-08-02.md` §5 as a genuine divergence requiring an explicit Owner decision — Planner's recommendation is to adopt the Keel numbered-file structure under `documents/decisions/` and keep this file as an index pointing at them. **Not yet resolved.**
- [ ] Tech stack (backend, frontend, data store, translation/NLP approach) — pending first build order/TDD.
- [x] Full text of **Keel v5** principles — provided 2026-08-02, filed in `documents/keel-v5/`.
- [ ] Full definition of **CORE** framework — CORE brief (Context/Objective/Role/Example) captured in `documents/sessions/MESG-close-out-2026-08-02.md` §6 and in `architecture.md`; confirm no separate CORE methodology doc is still owed beyond that.
- [ ] Hosting platform — drives Keel Part B (CI/CD, secrets, deploy gate) per `documents/sessions/MESG-pre-work-next-session.md`.
- [ ] SMS/email delivery provider(s).
- [ ] Source list / language coverage for Middle East discourse ingestion — see `documents/sessions/MESG-pre-work-next-session.md` re: narrow v1 scope recommendation.
- [ ] Legal/ethics position on source collection (scraping, elicitation, ToS) — flagged as a risk in the 2026-08-02 close-out, unscoped.
