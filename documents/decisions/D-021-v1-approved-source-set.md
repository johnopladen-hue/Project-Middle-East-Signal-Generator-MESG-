# D-021 — v1 approved source set

**Date:** 2026-09-27
**Status:** Decided

## Decision

Adopt the 47 sources in `backend/app/sources/approved_sources_v1.yaml` as MESG's v1 collection set:

- **16 native RSS**: 8 Levantine Arabic, 3 Persian, 5 Hebrew.
- **14 English comparison**: 6 baseline outlets + 8 outlets' own English editions.
- **17 Telegram**: 5 Arabic, 6 Persian, 6 Israeli perspectives.

**Designated and sanctioned sources are included, flagged, read-only, never republished** ([D-018](D-018-collection-posture.md)): Al-Manar (ar+en, US SDGT 2006), Fars (OFAC SDN 2023, Iran human-rights program), Palestinian Information Center (Hamas-affiliated, not designated), Press TV (Iranian state/IRIB; sanction status reported but **unconfirmed**).

`WAFAgency` and `alhadath` are included **despite unconfirmed authenticity** — each carries an `verification_note` = "AUTHENTICITY UNCONFIRMED" until checked against the outlets' own websites.

Two more Israeli-perspective Telegram channels added by Owner/Planner pick: **Mannie's War Room** (`@manniefabian`, Emanuel Fabian, Times of Israel military correspondent, English; Planner-verified live, post #59200 dated 20 Sep 2026) and the **IDF's official English channel** (`@idfofficial`, official checkmark, ~160K subscribers; latest-post date not yet confirmed — to verify in O-6).

**Expected volume:** ~2,500–3,000 items/day, dominated by Fars, Akhbar-e Fori, IRNA, Al Mayadeen, Palinfo and HaMoked. This is free NLLB triage load on the Owner's PC, not Claude cost ([D-016](D-016-translation-analysis-providers.md)). If the PC can't keep up, throttle the highest-volume channels first — never drop a source silently.

## Context

Resolves the source-approval gate this session flagged in PR #28 (`ingestion-orders-v0.1-foundations`): the prior candidate list (`MESG-candidate-sources-2026-09-27.md`) was explicitly marked "CANDIDATE — for owner approval, nothing here is final" and named designated/sanctioned entities, so Code would not pick from it unilaterally. The Owner reviewed it with the Planner and ruled the set above.

## Options rejected

- **The lean ~20-source set.** Thinner coverage than the Owner wanted for a first real look.
- **All ~65 verified sources.** Adds low-trust Hebrew aggregators and redundant Arabic broadcasters.
- **Excluding designated sources.** Rejected — loses Hezbollah's and much of the Iranian regime's own voice, which is exactly the in-language voice MESG exists to hear first-hand ([D-018](D-018-collection-posture.md)).
- **Holding the unconfirmed handles (WAFAgency, alhadath) until verified.** The Owner chose to include them now, flagged, rather than wait.

## Evidence

- `MESG-candidate-sources-2026-09-27.md` — the verification work behind the set.
- `backend/app/sources/approved_sources_v1.yaml` — the approved set as data, with per-source verification notes.
- Owner ruling, 2026-09-27, and the Planner's live verification of `@manniefabian` and `@idfofficial`.

## Supersedes

None. Resolves the source-list-approval blocker named in `documents/findings.md` and PR #28.
