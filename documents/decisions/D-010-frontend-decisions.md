# D-010 — Frontend decisions (F-1 through F-7)

**Date:** 2026-09-06
**Status:** Decided

## Decision

Resolves the seven frontend decisions (F-1–F-7) that `documents/tdds/MESG-UI-Spec-and-Claude-Code-Orders-v0.1.md` §2 requires be logged before Order 1 (and later orders) execute:

| # | Decision | Ruling |
|---|---|---|
| F-1 | Frontend language | **JavaScript (JSX), not TypeScript** (Owner-ruled, carried from [D-009](D-009-v1-technology-stack.md)). Mitigation: JSDoc `@typedef`s in `src/types/` for every entity the UI consumes, plus `PropTypes` on every component, both mirroring TDD §6 field-for-field. This mitigation is adopted as specified, not optional. |
| F-2 | Data-fetching / server-state layer | **TanStack Query (React Query)**, as proposed — caching, loading/error states, and refetch-on-focus are exactly what a read-heavy briefs/stories/signals UI needs, and hand-rolling them badly is the realistic alternative. |
| F-3 | Auth transport | **httpOnly session cookie** (`credentials: 'include'`; no token in JS-readable storage), consistent with the auth mechanism already decided in D-009. |
| F-4 | Styling system | **Tailwind CSS with a semantic token layer** mapping to the §3 palette — tokens in markup, never raw hex. |
| F-5 | Icon set | **`lucide-react`.** |
| F-6 | Routing | **React Router v6.** |
| F-7 | Roles in v1 | **Two roles: `admin`** (everything, incl. Admin section + release/suppress) **and `viewer`** (read-only: briefs/stories/weekly, no release, no admin). A third "reviewer" role is explicitly deferred. `User.role` (TDD §6) already accommodates this without a schema change. |

## Context

The UI-spec/orders document marks F-1 as **RULED** (Owner already said "React.JS") and F-2 through F-7 as **OPEN proposals**, and its Order 0 explicitly blocks later orders on these being logged or explicitly deferred: *"Do not silently adopt a proposal by building against it. Adopting it is the D-entry."* None of F-2–F-7 name a paid vendor, external account, or ongoing cost (unlike the hosting/translation/LLM/email/SMS decisions still open in `documents/decisions.md`) — they are open-source library and architecture choices with rationale already supplied by the Planner, so Code is resolving them here rather than blocking Order 1 on an Owner round-trip for tooling that carries no account/cost implication.

## Options rejected

- **TypeScript**, per the Planner's original recommendation — rejected in D-009 already, on the Owner's explicit "React.JS" instruction; reaffirmed here since F-1 is what the JSDoc/PropTypes mitigation exists to compensate for.
- **JWT auth** instead of session cookies (F-3's stated alternative) — rejected for consistency with D-009's auth decision; no Owner instruction favors JWT.
- **Hand-rolled fetch/caching** instead of TanStack Query (F-2) — rejected; the spec's own rationale (this is a read-heavy app that needs caching, loading/error states, and refetch-on-focus) is sound and uncontested.
- **CSS Modules + CSS variables** instead of Tailwind (F-4's stated fallback, "if Owner prefers no build-time CSS dep") — not chosen; no Owner objection to a build-time CSS dependency has been raised, so the primary proposal stands.
- **A third "reviewer" role in v1** (F-7) — rejected per the spec's own explicit deferral; adding it now would be scope creep against the "start simple" design principle (TDD §2.4).

## Evidence

- `documents/tdds/MESG-UI-Spec-and-Claude-Code-Orders-v0.1.md` §2 (the F-1–F-7 table), §10 Order 0 (the gate requiring this D-entry or explicit deferral before Order 1).
- `documents/decisions/D-009-v1-technology-stack.md` — the prior JS-over-TS and session-cookie rulings this decision is consistent with.
- Owner instruction, this session, 2026-09-06: "Find orders from planner, read, analyze and execute please" — authorizing Code to proceed through the orders, which includes resolving the decisions Order 0 requires.

## Supersedes

None. Extends D-009 with frontend-specific detail; does not change any of D-009's rulings.
