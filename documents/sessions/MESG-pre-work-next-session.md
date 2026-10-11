# MESG — Pre-Work for Next Session

**Prepared:** 2026-10-11 by Code (Claude Code, local), during U-0 of `MESG-Orders-Usable-Today-v0.1.md`
**For:** the next session — either Planner (fresh chat) or Code (fresh Claude Code session)
**Keel version:** v9
**Supersedes:** the 2026-09-13 version of this file (it still said "merge PR #24" and listed decisions only through D-015 — all of that is resolved)

---

## Opening ritual — do this first

1. **Start fresh.** Do not reopen a previous chat/session. Continuity lives in the repo, not in a chat log.
2. **Ground on live, not a snapshot.** Pull `johnopladen-hue/Project-Middle-East-Signal-Generator-MESG-`; do not trust any document's description of repo state, including this one — Standing Order 1.
3. **Read, in order:** this pre-work doc → the latest close-outs in `documents/sessions/`, newest first (as of this writing: `MESG-close-out-2026-09-27-session-wrap.md`, then `-ingest-now.md`, `-approved-sources.md`, `-frontend-tests.md`) → `documents/decisions.md` (through D-021) → `documents/findings.md` → `documents/assumptions.md` (through A-010) → `documents/architecture.md` → `documents/test_plan.md` (through T-036).
4. **State current state + today's agenda back to the Owner** before any work.

## Verified state at U-0 grounding (2026-10-11)

- **`origin/main` HEAD:** `2ff170f` (Merge PR #30, `ingest-now-v0.1`). **Open PRs:** none.
- **Highest decision:** D-021 (v1 approved source set). **Highest assumption:** A-010. **Highest test:** T-036.
- **Suites:** backend 100/100 pytest, frontend 92/92 Vitest (25 files).
- **`backend/.env`:** does not exist — nothing built so far calls Claude.
- **Real data:** 47 approved sources seeded (30 RSS + 17 Telegram); 712 real RSS items from 26 of 30 feeds (4 blocked by CDN/WAF, HTTP 403). Telegram not yet collected; nothing translated yet.

## Where we are — one line

MESG is a real running app with a real actor register, map, and a live RSS feed on `/incoming`; the current order (`MESG-Orders-Usable-Today-v0.1.md`, in the Owner's Downloads, not in the repo) makes it a continuously updating, English-readable feed — Telegram collector (U-1), NLLB triage translation (U-2), in-app scheduler (U-3), daily-use polish (U-4/U-5).

## Agenda (priority order) — the current order, U-0 → U-6, one PR each

1. **U-0** — grounding, commit the 2026-09-27 wrap docs, this rewrite, X/Twitter deferral finding.
2. **U-1** — Telegram web-preview collector (17 channels; D-018 collection posture). Stopping point 1.
3. **U-2** — NLLB-200 triage translator (D-016 translation & analysis providers). Needs the Owner's "go" on a ~2.5 GB model pull before anything is downloaded. Stopping point 2.
4. **U-3** — scheduled continuous ingestion (D-019 scheduler & runtime). Stopping point 3.
5. **U-4** — search, auto-refresh, time-window and kind/language filters on `/incoming`.
6. **U-5** — the state-driven honesty banner. Stopping point 4.
7. **U-6** — close-out.

Whatever is not done of this list carries forward; check `documents/sessions/` for which U-steps have a close-out or merged PR.

## Decisions/assumptions already resolved (do not re-litigate)

D-001 through D-021 are all Decided (`documents/decisions.md` is the index). A-001 through A-010 are registered (`documents/assumptions.md`). D-022 is the next free number — confirm against live before writing it.

## Open items carried forward (not exhaustive — see each close-out's §5)

- **After the current order:** the Owner creates the Claude API key (`MESG-Orders-API-Key-v0.1.md` Part A), then K-1–K-7, then O-3 (the NLLB-vs-Claude bake-off), then Analyst + Daily Brief.
- Delivery provider decision (TDD §4.7) and the test whitelist.
- X/Twitter — deferred by Owner ruling 2026-10-11 (`findings.md`); journalists/OSINT first when revisited.
- The 4 blocked RSS feeds (Al Arabiya ar+en, Enab Baladi, Maariv).
- OFAC multi-program label fix (`findings.md`, 2026-09-27).
- Severity vocabulary mismatch (`findings.md`, 2026-09-13).
- Fly.io deploy path — unbuilt (D-011, A-003); localhost-only until the go-remote tripwire (D-020).

## Questions for the Owner

- Any real credential, real user data, or real remote deploy on the horizon? That's the go-remote tripwire (D-011 as amended by D-020).
- Merge authorization is per-PR and does not carry over between sessions — expect to be asked for each PR.

## The discipline — reminder

Ground before you act — verify against the live repo, not this document's description of it. Every claim names its source artefact and count. Every decision written down before the work is finished — with the option you rejected and the evidence behind the call. Close out every session, commit it, start fresh.
