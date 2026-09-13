# Architecture — Project MESG (Middle East Signal Generator)

> This document is the single source of truth for system architecture. Update it whenever a build order or TDD changes the design. Do not let it drift from what is actually implemented.

## Mission & Problem Statement

**Context:** Coverage of Middle East events is poor because we rely on biased, English-language news media. We lack native-language access and are dependent on agenda-driven outlets, producing a hazy picture of unfolding events.

**Objective:** Separate what people are saying (native-language discourse) from what is being reported in English-language media, and identify where the two converge and diverge. Aggregate, analyze, and distill this into:
- A daily brief
- Alerts on high-signal events
- Potential signals of imminent action

Delivered via web application, SMS text, and email, to start.

**Roles the system (and its analysis) must embody:**
1. **Source-finding expert** — locates discussions, published news, and information exchanges impacting native language-speakers across the Middle East.
2. **Intelligence analyst** — assesses each source's access to the information it claims and the veracity of that information; objective, skeptical, and creative in corroboration (e.g., cross-checking a claimed shipment volume via a packaging supplier rather than trusting the company's own figure).

**Output format (example shape):**
- Bulleted daily summary; for each item: facts → analysis → probability of truth (1–5 scale) against corroborating/contradicting evidence.
- **Bulletins** (email + text) for: military events, natural disasters, incidents, disease outbreaks, assassinations, arrest of a political figure, arrest of a major cultural influencer, sudden disappearance of a news source, uprising, coup.
- **"What Mattered This Week"** summary, delivered Friday afternoon.

## Guiding Principles

- Adheres to **Keel v6** (`documents/keel-v6/`) — extends v5 (`documents/keel-v5/`, kept for history) with standing findings-log and test-plan-document principles. See [D-006](decisions/D-006-adopt-keel-v6.md).
- Leverages **CORE** — Context/Objective/Role/Example brief captured in the Mission & Problem Statement above and in `documents/sessions/MESG-close-out-2026-08-02.md` §6.

## System Components (to be filled in as designed)

| Component | Purpose | Status |
|---|---|---|
| Source ingestion | Collect native-language discourse + English media | Not started |
| Translation / normalization | Convert native-language sources for analysis | Not started |
| Corroboration / veracity engine | Score source access & reliability, cross-check claims | Not started |
| Divergence/convergence analysis | Compare native discourse vs. English media narrative | Not started |
| Daily brief generator | Produce bulleted, scored daily summary | Not started |
| Alerting engine | Detect bulletin-worthy events, trigger email/SMS | Not started |
| Weekly summary generator | "What Mattered This Week," Fridays | Not started |
| Web application | Deliver briefs/alerts, manage subscribers | Not started |
| Auth / access control | Username + password (v1), whitelisted recipients | Not started |
| Notification delivery | Email + SMS to whitelisted individuals | Not started |

## Data Flow (to be diagrammed as design matures)

_TBD — populate once first TDD defining ingestion/analysis pipeline is received._

## Tech Stack

Per [D-009](decisions/D-009-v1-technology-stack.md):

| Layer | Choice |
|---|---|
| Backend/API | Python + FastAPI |
| Database | SQLAlchemy ORM; PostgreSQL (production, per D-009) / SQLite (local dev, a real file at `backend/mesg_dev.db`) / SQLite temp-file (self-contained test suite, `backend/tests/conftest.py`) |
| Frontend | React + Vite, plain JavaScript |
| Auth | Username/password (argon2 hash), httpOnly session cookies |
| Translation, Analysis/LLM, Email, SMS, Scheduler, Hosting | Interface-based, deferred pending vendor decision — see `decisions.md` open list |

**v1 source scope** (per [D-008](decisions/D-008-v1-source-scope.md)): Levantine Arabic and Iranian Persian, from `documents/reference/Languages_and_Religions.md`.

**Known risk — dev/prod database divergence:** local dev runs against a real SQLite file (`backend/mesg_dev.db`), matching [A-001](assumptions.md)'s "CI runner ≈ deploy target" framing but not actual prod (PostgreSQL, per D-009, not yet stood up). SQLite and PostgreSQL differ on concurrency, type coercion, and some SQL semantics; code that only ever ran against SQLite locally could behave differently on Postgres. Named here rather than left silent per the first-article orders (2026-09-13); no mitigation is built yet beyond the ORM boundary D-009 already chose for swappability.

## Security Model

- **v1:** Simple username/password authentication.
- Recipient list (email/SMS) is a **whitelist** curated by the project owner.
- Expected to evolve — track upgrades in `decisions.md`.

## Actor-Network Layer (D-012)

Adds an actor domain, modelled on the Mapping Militants shape: `Organization`, `OrganizationAlias`, `Designation`, `Relationship` (typed, dated edges), `Theatre`. Deliberately carries **no `type`/`is_terrorist` truth column** - a contested characterization is a `Designation` row attributed to a named body and date, and an organization can carry several, even contradictory ones, as parallel sourced characterizations rather than a single resolved verdict.

**The harvester → storage contract (`backend/app/actors/contracts.py`, O-2):** every source-specific harvester (UCDP today; designation lists in Phase 3) must emit its output as this normalized shape - it never writes `Organization`/`Relationship` rows directly:

```python
ActorRecord(source_dataset, source_id, source_url, name, last_verified, aliases=(), theatre=None, grade=None)
RelationshipRecord(source_dataset, source_org_id, target_org_id, kind, source_url, start_date=None, end_date=None)
HarvestResult(actors=(...), relationships=(...))
```

`apply_harvest(session, result)` (`backend/app/actors/apply.py`) is the **only** code path that writes actor rows - resolving `Relationship` endpoints by `(source_dataset, source_id)`, counting (never silently dropping) any edge that resolves to nothing. `reconcile(session)` independently checks both directions: no edge points at a missing organization, and every organization's edges are countable.

**Principle 11 in this schema:** "never harvested" and "harvested but empty" must carry different values, never look the same. `Organization.last_verified is None` means never harvested; a set `last_verified` with zero aliases/designations means it *was* checked and genuinely found none. A `Designation` with no matched `organization_id` is stored with `match_status = unmatched_pending_match`, not dropped and not treated as "this org isn't designated."

## Map Interface (D-014, D-015)

**Self-hosted, not a public tile server.** The basemap is a self-hosted OSM-derived vector tileset (Protomaps/PMTiles, ODbL, `frontend/public/basemap/levant.pmtiles` - a genuine 2.9 MB extract of the live daily planet build, pulled via HTTP range requests, not the full 138 GB file; see `findings.md`, 2026-09-13). MapLibre GL JS (BSD-3) renders it; nothing in the render path calls `tile.openstreetmap.org`, Google, or Mapbox. `© OpenStreetMap contributors` attribution is required and shown on the map (`frontend/src/map/basemapStyle.js`).

**Cartographic stance — contested boundaries are shown as contested, not silently resolved (O-4).** The basemap's `boundaries` vector layer carries OSM's own `disputed` field; MESG's style renders `disputed=true` features distinctly (dashed, amber) rather than as an ordinary international border. This is the data's own honesty, not a position MESG invented — see `basemapStyle.js`'s `boundaries-disputed` layer.

**The map's frame is a lens, not neutral geography.** Regions are the U.S. Unified Command Plan's Areas of Responsibility (`AorMembership`, v1 = CENTCOM, [D-015](decisions/D-015-region-taxonomy-ucp-aors.md)) — stored as a **dated, versioned** fact (source + source_date per row), because AOR boundaries shift (Israel: EUCOM → CENTCOM, 2021-01-15). The UI labels this explicitly as the U.S. command frame, and a `FrameDivergenceNote` lets an analyst record where in-region self-conception diverges from it — the map's honesty about its own frame is a feature, not a footnote.

**Geo endpoint precision (O-7).** `GET /geo/items` returns located items as GeoJSON points with a `precision` field (`point`/`city`/`province`/`country`) and puts everything without a known location in a **separate unlocated set** — never a fake coordinate (Principle 11). Country-level precision (e.g. every harvested `Organization`, via its `Theatre`) comes from an offline centroid lookup (`app/geo/country_centroids.json`, computed from public-domain Natural Earth data) — no live geocoder call, per D-014.

## Revision Log

| Date | Change | Source Doc |
|---|---|---|
| 2026-08-02 | Initial architecture scaffold created from project kickoff conversation | This session |
| 2026-09-13 | Hosting platform decided (D-011); named the dev/prod SQLite-vs-PostgreSQL divergence as a known risk | `MESG-First-Article-Localhost-Orders-v0.1.md` O-2 |
| 2026-09-13 | Actor-network layer added (D-012): Organization/Alias/Designation/Relationship/Theatre schema + the ActorRecord harvester contract | `MESG-Actor-Network-Layer-Orders-v0.2.md` O-2 |
| 2026-09-13 | Map interface added (D-014/D-015): self-hosted MapLibre+PMTiles basemap, contested-boundary stance, CENTCOM AOR as a labeled U.S. lens, geo endpoint precision model | `MESG-Map-Interface-Orders-v0.1.md` O-4/O-6/O-7 |
