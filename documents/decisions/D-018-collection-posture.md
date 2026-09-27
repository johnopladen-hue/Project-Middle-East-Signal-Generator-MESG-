# D-018 — Collection posture: RSS + public Telegram, keyless corroboration feeds; WhatsApp excluded

**Date:** 2026-09-27
**Status:** Decided

## Decision

v1 collects **only**:
1. **RSS/Atom feeds** from Owner-approved outlets.
2. **Public Telegram channels via the no-login web preview** (`https://t.me/s/<handle>`), with **no Telegram account** in v1.
3. **Keyless public data feeds** for corroboration: IODA internet outages, the Tzeva Adom rocket-alert mirror, USGS earthquakes and GDACS disaster alerts (the build comes in a later order).

**Collection rules:**
- **Public broadcast content only.** No private groups, no joining anything, no accounts in v1.
- **Channels, not people.** Store content per channel/outlet. Store no personal data about individual commenters or posters beyond what a public channel post itself contains.
- **Designated and sanctioned sources** (e.g. Al-Manar, US SDGT; Fars and Tasnim, OFAC SDN) are **read as sources, flagged in the data model and UI, and never republished wholesale**. Quote only as needed for analysis.
- **Politeness:** per-host rate limits and a descriptive User-Agent. Read `t.me/robots.txt` and each outlet's robots.txt at grounding and record the posture in `findings.md`.
- **Collected content never leaves the Owner's machine.** The database stays gitignored (already verified: `backend/*.db`, `backend/data/`).
- **Pre-translated material is its own source class** with a required `translator_selector` field (who chose what to translate and who rendered it). It never substitutes for the original-language voice. Outlets' own English editions are paired with their native-language editions (`pair_id`).

## Context

Owner rulings, 2026-09-27 (Telegram and "other message services you deem valuable"; the Planner advised against WhatsApp and the Owner accepted). `test_plan.md` has listed "legal/ethics position on collection" as the blocker for ingestion since 2026-08-02; this decision is that position.

## Options rejected

- **WhatsApp.** No public or readable layer; groups are end-to-end encrypted. Harvesting would mean joining private groups under a real account, against WhatsApp's terms and with real ethical and legal exposure. WhatsApp Channels have no read API.
- **Reddit.** Deferred, not rejected. Useful for diaspora sentiment but mostly English, and access runs through a data API whose terms need a careful read first.
- **X/Twitter.** Paid API access is far beyond the $20 posture.
- **Telegram via an account (the MTProto API, e.g. Telethon).** Deferred. It needs a phone-linked account, i.e. a real credential, and the keyless web preview suffices to prove the idea.
- **Eitaa and Rubika** (Iranian domestic platforms). Deferred; access not yet investigated.

## Evidence

- Owner rulings, 2026-09-27.
- The candidate source list: 23 Telegram channels verified live through the web preview.
- **Iran-hosted government RSS (Tasnim, Fars, IRNA, Mehr, ISNA) was unreachable from outside Iran.** Their voice is reachable only through Telegram, which makes Telegram load-bearing, not optional.
- `test_plan.md` has listed "legal/ethics position on collection" as the blocker for ingestion since 2026-08-02.
- The Owner is not relying on this as legal advice. If MESG ever becomes more than personal use, the designated-source handling gets a professional review.

## Supersedes

None. Resolves the ingestion blocker in `test_plan.md` and TDD §4.1's "per-source collection method" decision; extends [D-013](D-013-source-licensing-posture.md) (licensing posture) from the actor register to collection.
