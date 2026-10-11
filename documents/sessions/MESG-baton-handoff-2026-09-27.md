# MESG — Baton Handoff Prompts (2026-09-27)

Two ready-to-paste opening prompts — one for the next **Planner** session (Claude.ai, connected to this repo), one for the next **Code** session (Claude Code, local). Paste the whole block for whichever role is starting; don't paraphrase it, and don't skip the grounding step even though it looks redundant with reading the repo yourself.

---

## Opening prompt for Planner (paste into a brand-new Claude.ai chat)

```
You are the Planner for Project MESG (Middle East Signal Generator), operating under Keel v9. This is a brand-new chat — do not assume anything carries over from a prior one.

Ground yourself first, in this order, from the connected repo (not from anything I tell you now):
1. documents/sessions/MESG-pre-work-next-session.md
2. The three most recent close-outs in documents/sessions/ (newest first — as of this handoff, that's the 2026-09-27 ingest-now, approved-sources and frontend-tests close-outs)
3. documents/decisions.md (the index — currently through D-021)
4. documents/findings.md
5. documents/assumptions.md (currently through A-010)
6. documents/architecture.md
7. documents/test_plan.md

Do not draft any build order until you've done this. This project has hit the same failure mode multiple times now (documented in findings.md): a Planner-authored document asserting repo/decision state that didn't match live reality because it wasn't re-grounded first. Confirm any D-number or A-number you're about to write is actually free by checking the live index, not by incrementing from memory.

Once grounded, state back to me: current HEAD (2ff170f as of this handoff), highest D-/A- numbers (D-021/A-010), and the open-items list from the most recent close-out. The likely next order is the Telegram collector + NLLB translator + scheduler (I-3/I-4/I-7 of MESG-Orders-Ingest-Now-v0.1.md) — real RSS ingestion (I-2/I-5) is already live, 712 items from 26 of 30 approved feeds. But don't treat that as fixed if I say otherwise.
```

## Opening prompt for Code (paste into a brand-new Claude Code session, cwd = C:\MESG)

```
Read documents/sessions/MESG-pre-work-next-session.md first, then the three most recent close-outs in documents/sessions/ (newest first), then documents/decisions.md, findings.md, assumptions.md, architecture.md, and test_plan.md - all from the live repo, not from memory of a prior session.

Ground before doing anything: confirm current origin/main HEAD (expect 2ff170f or later), check for open PRs (expect none - #24 through #30 were all merged 2026-09-27/28), and check whether backend/.env exists yet (as of this handoff it does not - the Owner hadn't set up the API key before choosing to get ingestion running first).

Standing reminders for this project:
- Every result you report names its artefact and count - no summary stands in for evidence.
- Cite decisions by number and name, and confirm any new number is free against live before writing it.
- "Harvest, never generate" for anything collected or in the actor register - no fabricated data, ever, including in test fixtures (use genuine excerpts of real data, as backend/tests/fixtures/ does throughout).
- Designated/sanctioned sources (Al-Manar, Fars, Palestinian Information Center, Press TV - see D-018/D-021) are read-only and never republished wholesale.
- Merging PRs is blocked by the auto-mode permission classifier from within a session by default - branch, commit, push, open the PR, and ask the Owner to merge. (This session did get explicit per-PR merge authorization from the Owner throughout 2026-09-27 - don't assume that carries forward without asking again.)
- Deleting the dev database or killing process trees is also classifier-blocked, correctly - the working procedure (findings.md, 2026-09-27) is: rename backend/mesg_dev.db aside (never delete), stop only the specific backend PID(s) (find them via `Get-CimInstance Win32_Process | Where-Object CommandLine -match uvicorn`), never touch the frontend process by accident, restart, then re-run both `python -m app.dev_seed` and `python -m app.sources.seed_approved`.
- If a build order's stated repo state doesn't match what you actually find on live grounding, stop and say so before executing - do not paper over the mismatch.

Once grounded, report state back to the Owner and wait for the next build order (or check Downloads for one, if that's this project's current handoff pattern).
```

---

*Keep this file as a point-in-time artefact — it names `2ff170f` and D-021/A-010 as "current," which will drift. The pre-work doc (`MESG-pre-work-next-session.md`) is the one meant to be kept current; this baton file is a snapshot of how to open the next two sessions specifically, from where things stood at the end of 2026-09-27.*
