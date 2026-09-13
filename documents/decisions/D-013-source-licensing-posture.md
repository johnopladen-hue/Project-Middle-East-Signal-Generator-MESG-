# D-013 — Source & licensing posture for the actor register

**Date:** 2026-09-13
**Status:** Decided

## Decision

Per-source disposition and license, recorded before any real harvest — substance is Owner-ruled (2026-09-13: honor every source's license; do not ingest anything a license forbids):

- **UCDP Actor Dataset — approved for harvest.** **Corrected at the O-4 re-confirmation, 2026-09-13** (see `findings.md`): ingest via the **plain public CSV download** (`https://ucdp.uu.se/downloads/actor/ucdp-actor-261-csv.zip`), not the JSON API — the API has no dedicated Actor endpoint and requires a registered access token (a credential), while the Actor Dataset itself is a no-auth public file. License is CC BY 4.0 as originally stated. Attribution obligation: cite the dataset's specified publications wherever its data is surfaced ("Shawn Davies, Therese Pettersson, Magnus Oberg, Organized violence 1989-2025, and violent political protests, Journal of Peace Research, 2026"), and indicate that the data was modified (MESG normalizes it) — carried as `Organization.citation` on every record. Provides the relationship spine (actor IDs, name history, splits, alliances) via `ActorIdPrev`/`ActorIdAlliance`/`ActorIdGroup`. Known scope limit: covers only actors involved in organized violence (see [A-004](../assumptions.md)).
- **Public terrorism-designation lists** (US State FTO, OFAC SDGT/SDN, UN Consolidated Sanctions, EU, UK proscribed orgs) — **approved** as the source for `Designation` records. Government/IGO public data; each list's terms and URL are recorded when harvested (O-7). This is where the contested "terrorist" label lives — as *"designated by body X, list Y, date Z,"* never as a truth.
- **Mapping Militants Project (Rice)** — **cited reference / corroboration only**, not bulk ingest. DOI-cited academic work; attribution required per its citation policy.
- **ACLED — excluded from automated ingest.** Its terms prohibit using its content to train/develop AI/LLM systems or to create a substitute for ACLED (verified 2026-09-13); MESG is that use case. Reference-only at most; revisit only under a negotiated license.
- **GTD (START/Maryland) — out.** Event data through 2020; access now closed/registration-gated; not an actor registry.

## Context

Resolves the long-open "legal/ethics position on source collection" item in `documents/decisions.md` — previously unscoped since the 2026-08-02 close-out, blocking real ingestion. The Owner's ruling is a general principle (honor every license) applied here to the five sources actually considered for the actor register.

## Options rejected

- **Ingesting ACLED.** Rejected — its EULA explicitly prohibits the AI/LLM-training use case MESG is.
- **Scraping UCDP where an official API exists.** Rejected — scraping when a licensed API is offered is unnecessary risk with no benefit; D-012/D-013's "harvest, never generate, never scrape past what's offered" posture applies.
- **LLM-generating the register.** Rejected — no provenance; directly violates "harvest, never generate" (D-012).

## Evidence

- Owner ruling, 2026-09-13: honor every source's license; do not ingest anything a license forbids.
- UCDP's stated terms (CC BY 4.0, official API), verified 2026-09-13 per `MESG-Actor-Network-Layer-Orders-v0.2.md` — re-confirmed independently before the first fetch, per O-4.
- ACLED's terms (AI/LLM-training and substitute-product prohibition), verified 2026-09-13.
- GTD's current access status (closed/registration-gated, data through 2020 only), verified 2026-09-13.

## Supersedes

Resolves the open "legal/ethics position on source collection" item in `documents/decisions.md`.
