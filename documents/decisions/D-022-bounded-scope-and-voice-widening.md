# D-022 — Bounded scope: public in-region voices vs English media; widen Telegram; Reddit by research application

**Date:** 2026-11-01
**Status:** Decided (Owner ruling, 2026-11-01)

## Decision

1. **MESG's objective, stated honestly.** MESG separates what **public in-region channels, outlets and named voices** say in their own languages from what **English-language media** report, and shows where the two converge and diverge. It does **not** measure population opinion and does not read private conversation. The product says so wherever it reports. The honesty banner (U-5) carries a standing scope line, and `architecture.md`'s mission statement records the bound.
2. **Widen Telegram within [D-018](D-018-collection-posture.md) (collection posture).** Add public **channels** that bring voices MESG lacks:
   - named journalists, commentators and public figures;
   - local and city news, especially channels carrying residents' reports;
   - citizen-reporting and human-rights documentation;
   - a few OSINT/security-watch channels.

   These are balanced across the political spectrum in each language community. Candidates are researched, verified from the Owner's PC through the keyless web preview, and approved by the Owner before seeding, the same gate as [D-021](D-021-v1-approved-source-set.md) (v1 approved source set).
3. **Reddit: apply, don't build.** The Owner files a researcher access request under Reddit's Responsible Builder Policy. No Reddit collector is built meanwhile, and no keyless workaround is attempted. If access is granted, a new decision covers the build and its terms.
4. **X/Twitter: not pursued now.** It stays deferred (findings, 2026-10-11).
5. **Open option, not taken: Telegram public groups and channel comment threads.** That is where ordinary people talk to each other, but it needs a phone-linked account (a real credential; [D-020](D-020-go-remote-tripwire-amendment.md) tripwire) and a change to D-018's "channels, not people" rule. It stays open for a future Owner ruling.

## Context

On 2026-11-01 the Owner asked for one more attempt at Reddit and, on the result, an honest conversation about whether the project's objective is achievable. Collection so far (47 sources; first Telegram run 1,650 items from 17 channels, findings 2026-10-11) leans on outlets and institutions. Only a few of the 17 Telegram channels are individual voices (e.g. Vahid Online, Amit Segal, Mannie's War Room). So the "what people are saying" half of the original objective is met only in part. Region-wide conversation happens on Telegram groups, Instagram, X, Facebook, TikTok and WhatsApp. Except for public Telegram, all of these are closed to keyless, terms-compliant collection. The divergence half (in-region vs English media) is achievable and largely built. Its remaining blockers are analysis (the Claude API key) and translation quality on names and places (findings, 2026-10-11 U-2 spot-check), not collection.

The Owner ruled on the Planner/Code options: Telegram widening (1), Reddit research application (3) and bounded scope (4). Paid X (2) was not taken.

## Options rejected

- **Keyless Reddit collection now** (public `.rss`/`.json`). Not attempted further. Reddit closed self-service API access on 2025-11-11, and building on unauthenticated endpoints while an access request is pending invites a block that could prejudice the request. D-018's no-evasion line applies either way.
- **X pay-per-use on curated accounts** (~$0.005 per post read, ~$150/month at 1,000 posts/day). The Owner declined for now. The cost is well past D-016's $20/month posture.
- **Keep the original "what people are saying" wording.** That would claim a capability MESG cannot deliver within D-018, which is a Keel P8 failure (a claim without the artefact behind it).
- **Abandon the people-side entirely.** Rejected. Named voices, local channels and citizen reporting are real, reachable in-region speech.
- **Telegram groups/comments now.** Not rejected on merit. It needs an account and a D-018 change, so it is held open (item 5).

## Evidence

- Reddit admins, r/redditdev, 2025-11-11, "Introducing the Responsible Builder Policy": self-service access to Reddit's public data API is closed; new access, including new OAuth tokens, requires a request; researchers file a ticket.
- 2026-11-01 probes from Code's cloud workspace: `https://www.reddit.com/r/iran/new/.rss` and three similar URLs got no route (proxy 403, 0 bytes), and the web-fetch tool refused reddit.com as not allowlisted. **This says nothing about reachability from the Owner's PC.** A probe script (`probe_reddit.py`, keyless `.rss`, 15 candidate subreddits) was given to the Owner and had not been run when this decision was made.
- X pricing evidence: `findings.md`, 2026-10-11 (X/Twitter deferral).
- Collection composition: `backend/app/sources/approved_sources_v1.yaml` (17 Telegram channels) and `findings.md`, 2026-10-11 (U-1 real run).

## Supersedes

None. **Extends [D-018](D-018-collection-posture.md)**: it resolves D-018's "Reddit: deferred" line into a route (research application) and names the groups/comments option. **Narrows the mission statement** in `architecture.md` (the original kickoff Objective) to what this decision states. D-021's approval gate is unchanged and applies to every new channel.
