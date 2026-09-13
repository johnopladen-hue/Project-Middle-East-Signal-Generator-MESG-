# MESG — Pre-Work for Next Session

**Prepared:** 2026-09-13 by Code (Claude Code, local)
**For:** the next session — either Planner (fresh chat) or Code (fresh Claude Code session)
**Keel version:** v9
**Supersedes:** the 2026-08-02 version of this file (Keel v5 era — everything in it is resolved; kept no further)

---

## Opening ritual — do this first

1. **Start fresh.** Do not reopen a previous chat/session. Continuity lives in the repo, not in a chat log.
2. **Ground on live, not a snapshot.** Clone/pull `johnopladen-hue/Project-Middle-East-Signal-Generator-MESG-`; do not trust any document's description of repo state, including this one — Standing Order 1.
3. **Read, in order:** this pre-work doc → the latest close-outs in `documents/sessions/` (`MESG-close-out-2026-09-13-session-wrap.md`, then `-map-interface.md`, `-actor-network.md`, `-first-article.md`, in that order, newest first) → `documents/decisions.md` (through D-015) → `documents/findings.md` → `documents/assumptions.md` (through A-007) → `documents/architecture.md` → `documents/test_plan.md`.
4. **State current state + today's agenda back to the Owner** before any work.

## Where we are — one line

The Keel was laid and proven weeks ago (CI gate, branch protection, D-001–D-010); since then the app has grown a real running backend + frontend (first article), a real actor-network register with genuine harvested UCDP/OFAC data (D-012/D-013), and a real self-hosted map interface with a CENTCOM AOR lens (D-014/D-015) — all with open, honestly-tracked gaps, not silent ones.

## Immediate next step (before anything else)

**Merge PR #24** (`map-render-fixes`, CI green) — two real bugs found by the Owner actually looking at the running app: the basemap rendered as plain grey (Vite/MapLibre Web Worker pre-bundling conflict, fixed), and place-name labels didn't render (fixed by self-hosting a Noto Sans glyph range). **The label fix was not re-verified live before the prior session ended** — after merging, open http://localhost:5173/map, hard-refresh, and confirm both the basemap (land/water/roads/boundaries) and English place-name labels actually render.

## Agenda (priority order)

1. **Verify PR #24's fixes live** (above) — the one loose end from today.
2. **Add frontend component tests** for `MapView.jsx`, `Organizations.jsx`, `OrganizationDetail.jsx` — three sessions running without them now (first-article, actor-network, map-interface all built UI with no `.test.jsx`, unlike every earlier route in this codebase). Worth doing as its own small pass before building more UI on top.
3. **Decide what's next**, most likely one of:
   - The **MMP actor-network addendum** the actor-network-layer orders flagged as the natural next increment (needs a TDD addendum + D-016).
   - **Widening designation-list coverage** past OFAC's SDN (US State FTO's own page and UN/EU/UK lists are still unharvested — `centcom.mil`-style bot-blocking may recur; CRS-style public-domain fallbacks worked twice this project, worth trying first next time a .gov/.mil source is needed).
   - **Non-English map labels** (only basic-Latin glyphs are self-hosted today).
   - Something else the Owner has in mind — this file doesn't presume.
4. **Fix the severity vocabulary mismatch** (`findings.md`, 2026-09-13, first-article session) — small, still open, low-risk to close out.

## Decisions/assumptions already resolved (do not re-litigate)

D-001 through D-015 are all Decided (`documents/decisions.md` is the index). A-001 through A-007 are registered (`documents/assumptions.md`). If a new build order proposes re-deciding any of these under new numbers, that is almost certainly the same stale-snapshot failure mode `findings.md` has now recorded three times this project — re-ground before drafting.

## Open items carried forward (not exhaustive — see each close-out's §5 for full detail)

- PR #24 merge + live verification (above).
- Frontend component test gap (three UI surfaces).
- Five non-CENTCOM AORs, self-hosted geocoder, UN/EU/UK designation lists, rich frame-divergence overlay — all named and deferred, not silently dropped.
- Severity vocabulary mismatch (`severity_for()` vs. `SeverityMark`).
- Fly.io deploy path — still unbuilt/unproven (D-011, A-003); localhost remains dev-only by design until the go-remote tripwire.

## Questions for the Owner

- Which of the agenda items above is the priority for the next session?
- Any real credential, real user data, or real remote deploy on the horizon? That's the go-remote tripwire (D-011/D-014) — it flips the repo Private and retires the localhost-only posture.

## The discipline — reminder

Ground before you act — verify against the live repo, not this document's description of it. Every claim names its source artefact and count. Every decision written down before the work is finished — with the option you rejected and the evidence behind the call. Close out every session, commit it, start fresh.
