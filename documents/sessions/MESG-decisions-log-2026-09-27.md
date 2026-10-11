# MESG — Decisions Log Snapshot (as of 2026-09-27, `main` @ `2ff170f`)

> **This is a point-in-time export, not the source of truth.** The live, authoritative index is `documents/decisions.md` in the repo (each row links to its full five-field file under `documents/decisions/`). This snapshot exists for quick reference without opening the repo — always re-check the live file before citing a decision or claiming a D-number is free.

**Six decisions landed today:** D-016 through D-021 — the whole ingestion-pipeline decision set (providers, scope, collection posture, scheduler, the go-remote tripwire amendment, and the approved source list). Three assumptions registered: A-008 through A-010. Full detail on each is in its own `documents/decisions/D-0NN-*.md` file; this snapshot only carries the index table.

---

# Decisions Log — Project MESG (Index)

> Per [D-001](decisions/D-001-decision-log-structure.md), this file is an **index**, not the log itself. Every material decision gets its own numbered file in `documents/decisions/` — `D-NNN-slug.md` — with five fields: decision, context, options rejected, evidence, supersedes.

## Decision index

| # | Title | Date | Status | Supersedes |
|---|---|---|---|---|
| D-001 | Decision-log structure | 2026-08-02 | Decided | — |
| D-002 | Repository initialization | 2026-08-02 | Decided | — |
| D-003 | Documentation directory structure | 2026-08-02 | Decided (refined by D-001) | — |
| D-004 | Planner/Builder working model | 2026-08-02 | Decided | — |
| D-005 | v1 security model | 2026-08-02 | Decided | — |
| D-006 | Adopt Keel v6 as the governing discipline | 2026-08-02 | Decided | — |
| D-007 | Adopt Keel v9 as the governing discipline | 2026-09-06 | Decided | D-006 (version only) |
| D-008 | v1 source scope: Levantine Arabic + Persian | 2026-09-06 | Decided (language list amended by D-017) | — |
| D-009 | v1 technology stack (backend, DB, frontend, auth) | 2026-09-06 | Decided | — |
| D-010 | Frontend decisions F-1–F-7 (query layer, auth transport, styling, icons, routing, roles) | 2026-09-06 | Decided | Extends D-009 |
| D-011 | Hosting platform (Fly.io) and localhost dev-for-now | 2026-09-13 | Decided (tripwire amended by D-020) | — |
| D-012 | Adopt the actor-network layer (Organization/Relationship/Designation/Theatre/Alias) | 2026-09-13 | Decided | — |
| D-013 | Source & licensing posture for the actor register (UCDP approved, ACLED excluded, GTD out) | 2026-09-13 | Decided | Resolves the open legal/ethics item below |
| D-014 | Map interface technology + self-hosted basemap (MapLibre GL JS + PMTiles) | 2026-09-13 | Decided | — |
| D-015 | Region taxonomy: UCP AORs as a labeled U.S. operational lens (CENTCOM v1) | 2026-09-13 | Decided | — |
| **D-016** | **Translation & analysis providers: free-first hybrid (NLLB-200 triage, Claude deep pass, $20/month cap)** | 2026-09-27 | Decided (provisional pending O-3 bake-off) | — |
| **D-017** | **v1 scope amended: add Israeli Hebrew** | 2026-09-27 | Decided | D-008 (language list only) |
| **D-018** | **Collection posture: RSS + public Telegram, keyless corroboration feeds; WhatsApp excluded** | 2026-09-27 | Decided | Extends D-013 |
| **D-019** | **Scheduler & runtime: in-app scheduler, localhost first** | 2026-09-27 | Decided (build deferred to next order) | — |
| **D-020** | **Go-remote tripwire amended: a local-only credential does not trip it** | 2026-09-27 | Decided | D-011 (tripwire clause only) |
| **D-021** | **v1 approved source set (47 sources: RSS + Telegram, designated sources flagged)** | 2026-09-27 | Decided | — |

## Open Decisions / Pending (not yet a D-file)

- [ ] Full definition of **CORE** framework — CORE brief (Context/Objective/Role/Example) captured in `documents/sessions/MESG-close-out-2026-08-02.md` §6 and in `architecture.md`; confirm no separate CORE methodology doc is still owed beyond that.
- [ ] SMS/email delivery provider(s) — TDD §4.7.
- [ ] Initial whitelist recipients for testing delivery — `documents/sessions/MESG-pre-work-next-session.md`.

_When one of the above is resolved, give it the next D-number (D-022 is next free, confirm against live first), write the full five-field file in `documents/decisions/`, and move it into the index table above._

---

## Assumptions registered today (for reference — full log in `documents/assumptions.md`)

- **A-008:** NLLB-200 triage translation of headline+lede is good enough to decide which items deserve the deep pass — open until the O-3 bake-off runs.
- **A-009:** Telegram's public web preview stays keyless, available and parseable for the approved channels.
- **A-010:** $20/month of Claude covers the deep pass at v1 volume once triage is free.
