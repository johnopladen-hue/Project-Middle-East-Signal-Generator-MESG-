# D-015 — Region taxonomy: UCP AORs as a labeled U.S. operational lens

**Date:** 2026-09-13
**Status:** Decided

## Decision

Adopt the U.S. Unified Command Plan's geographic Areas of Responsibility as MESG's **region registry** — the six terrestrial regional AORs (NORTHCOM, SOUTHCOM, EUCOM, AFRICOM, CENTCOM, INDOPACOM), **v1 = CENTCOM**. Adopt it **explicitly as a labeled U.S. operational lens, not neutral geography**: the map states the frame is U.S. command's, and MESG surfaces where in-region self-conception diverges from it (frame-divergence as an on-mission feature, [D-014](D-014-map-interface-technology.md)/O-9). AOR membership is stored as a **dated, versioned** fact (which source, which date) because boundaries shift; AOR polygons are derived as the **union of member-country borders**. Region (AOR) is a separate axis from source scope ([D-008](D-008-v1-source-scope.md)) — the map filters by AOR; ingestion filters by language scope; they are not merged.

**CENTCOM v1 membership** (22 entries — 21 sovereign states + West Bank & Gaza — per Congressional Research Service, "United States Central Command," IF11428, Version 3, Updated March 30, 2022, the most recent CRS treatment on record; re-confirmed live 2026-09-13 after the official `centcom.mil` AOR page returned HTTP 403 to both `WebFetch` and `curl` — see `findings.md`):

Afghanistan, Bahrain, Egypt, Iran, Iraq, Israel, Jordan, Kazakhstan, Kuwait, Kyrgyzstan, Lebanon, Oman, Pakistan, Qatar, Saudi Arabia, Syria, Tajikistan, Turkmenistan, United Arab Emirates, Uzbekistan, Yemen, West Bank & Gaza.

Notably: Israel moved to CENTCOM from EUCOM on January 15, 2021 (per DOD's 2020 UCP review) — cited in-source as the most recent AOR reassignment CRS documents, which is exactly the kind of change [A-006](../assumptions.md) exists to guard against going stale silently.

## Context

The actor-network layer ([D-012](D-012-actor-network-layer.md)) needed a concrete `Theatre` taxonomy; the map interface orders (`MESG-Map-Interface-Orders-v0.1.md`) specify UCP AORs for this rather than an ad-hoc region list.

## Options rejected

- **UCP as a plain neutral taxonomy.** Rejected — re-imposes the Western/U.S. frame MESG exists to see past, and discards the divergence feature that is the actual point of naming the frame explicitly.
- **An ad-hoc "Middle East" region.** Rejected — undefined, unstable, no authoritative membership list or versioning.
- **A purely in-region regionalization.** Rejected — no single authoritative, stable source exists for one; the consumer (the Analyst role) is oriented around the U.S. command frame as the thing to compare against, not replace.

## Evidence

- `MESG-Map-Interface-Orders-v0.1.md` §2 O-B — the drafted decision content this ratifies.
- CRS, "United States Central Command," IF11428 v3, Updated March 30, 2022 — the CENTCOM membership list above, downloaded and read directly (`congress.gov/crs_external_products/IF/PDF/IF11428/IF11428.3.pdf`) after `centcom.mil`'s own AOR page returned HTTP 403 (bot-blocked) to both `WebFetch` and `curl` — see `findings.md`, 2026-09-13.
- CRS reports are U.S. Government works, not subject to copyright, per the document's own disclaimer — safe to cite and quote.

## Supersedes

None; extends [D-012](D-012-actor-network-layer.md)'s `Theatre` entity with a concrete, sourced taxonomy.
