# Decisions Log — Project MESG (Index)

> Per [D-001](decisions/D-001-decision-log-structure.md), this file is an **index**, not the log itself. Every material decision gets its own numbered file in `documents/decisions/` — `D-NNN-slug.md` — with five fields: decision, context, options rejected, evidence, supersedes. Add a row here when you add a D-file; keep rows in numeric order.

## Decision index

| # | Title | Date | Status | Supersedes |
|---|---|---|---|---|
| [D-001](decisions/D-001-decision-log-structure.md) | Decision-log structure | 2026-08-02 | Decided | — |
| [D-002](decisions/D-002-repository-initialization.md) | Repository initialization | 2026-08-02 | Decided | — |
| [D-003](decisions/D-003-documentation-directory-structure.md) | Documentation directory structure | 2026-08-02 | Decided (refined by D-001) | — |
| [D-004](decisions/D-004-planner-builder-working-model.md) | Planner/Builder working model | 2026-08-02 | Decided | — |
| [D-005](decisions/D-005-v1-security-model.md) | v1 security model | 2026-08-02 | Decided | — |
| [D-006](decisions/D-006-adopt-keel-v6.md) | Adopt Keel v6 as the governing discipline | 2026-08-02 | Decided | — |
| [D-007](decisions/D-007-adopt-keel-v9.md) | Adopt Keel v9 as the governing discipline | 2026-09-06 | Decided | D-006 (version only) |
| [D-008](decisions/D-008-v1-source-scope.md) | v1 source scope: Levantine Arabic + Persian | 2026-09-06 | Decided | — |
| [D-009](decisions/D-009-v1-technology-stack.md) | v1 technology stack (backend, DB, frontend, auth) | 2026-09-06 | Decided | — |

## Open Decisions / Pending (not yet a D-file)

- [ ] Full definition of **CORE** framework — CORE brief (Context/Objective/Role/Example) captured in `documents/sessions/MESG-close-out-2026-08-02.md` §6 and in `architecture.md`; confirm no separate CORE methodology doc is still owed beyond that.
- [ ] Hosting platform — drives Keel Part B (CI/CD, secrets, deploy gate) per `documents/sessions/MESG-pre-work-next-session.md`. Explicitly deferred by the Owner, 2026-09-06; backend work proceeds against the placeholder deploy step in the meantime.
- [ ] Translation provider (LLM-based vs. dedicated MT service) — TDD §4.2.
- [ ] Analysis/LLM provider — TDD §4.4.
- [ ] SMS/email delivery provider(s) — TDD §4.7.
- [ ] Scheduler mechanism — TDD §5.
- [ ] Legal/ethics position on source collection (scraping, elicitation, ToS) — flagged as a risk in the 2026-08-02 close-out, unscoped. Needed before real ingestion (not before backend scaffolding).
- [ ] Initial whitelist recipients for testing delivery — `documents/sessions/MESG-pre-work-next-session.md`.

_When one of the above is resolved, give it the next D-number, write the full five-field file in `documents/decisions/`, and move it into the index table above._
