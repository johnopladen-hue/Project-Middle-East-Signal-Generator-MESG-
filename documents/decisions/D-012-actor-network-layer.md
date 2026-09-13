# D-012 — Adopt the actor-network layer

**Date:** 2026-09-13
**Status:** Decided

## Decision

Add an actor domain to MESG, modelled on the Mapping Militants shape: **Organization**, **Relationship** (typed, dated edges between organizations), **Designation** (a characterization by a named body), **Theatre**, and **Alias**. Signals and Stories attach to organizations and relationships, so a "signal of imminent action" can be expressed as a *predicted change to the actor map* (a split forming, an alliance breaking, a leadership arrest). **Classification is stored as sourced attributes, never a single truth column** — an organization carries a set of designations/characterizations, each attributed to who said it and when. Scoped to v1 ([D-008](D-008-v1-source-scope.md)).

## Context

MESG's mission (per `documents/architecture.md`'s Mission & Problem Statement) already frames signals as needing to identify divergence/convergence and "imminent action" — but the schema had no place for the actors an action would be imminent *for*. The Owner directed building the Mapping Militants (Rice) shape as MESG's own actor layer, consolidating what would otherwise have been a separate TDD addendum directly into this build-orders document.

## Options rejected

- **A single `type` / `is_terrorist` column on Organization.** Rejected — this embeds the exact bias MESG exists to expose (TDD's Analyst role is explicitly skeptical and multi-source; a single truth column would make MESG itself the uncorroborated authority). Every characterization is instead a `Designation` row naming who said it, on what list, and when.
- **Building "all the world's factions."** Rejected — an open, unverifiable set. Scoped to v1 (Levantine Arabic + Persian, per D-008); every row must trace to a licensed source artefact (see D-013), never model knowledge.

## Evidence

- `documents/architecture.md` Mission & Problem Statement — "signals of imminent action" already implied an actor the action is attributed to.
- [D-008](D-008-v1-source-scope.md) — the v1 scope this layer is bounded to.
- Owner direction, 2026-09-13: consolidate the actor-layer spec into these build orders rather than a separate TDD addendum.
- `MESG-Actor-Network-Layer-Orders-v0.2.md` — the full spec this decision ratifies.

## Supersedes

None. Extends the [D-009](D-009-v1-technology-stack.md) data model with a new domain; does not change any existing entity.
