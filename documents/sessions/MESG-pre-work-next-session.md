# MESG — Pre-Work for Next Session

**Prepared:** 2026-08-02 by Planner
**For:** the next Planner session (a fresh chat)
**Keel version:** v5

---

## Opening ritual — do this first

1. **Start a brand-new chat.** Do not reopen the previous one. Continuity lives in the repo, not in a chat log.
2. **Upload nothing.** The connected repo is your ground truth.
3. **Read, in order:** this pre-work doc → the latest close-out (`MESG-close-out-2026-08-02.md`) → `architecture.md`, `decisions.md`, `findings.md`, `test plan.md` (once they exist) → `Languages_and_Religions.md`.
4. **Re-ground on KEEL v5** — the three pages — before planning anything.
5. **State current state + today's agenda back to the Owner** before any work.

## Where we are — one line

The brief and operating model are set; the Keel is **not yet fully laid or proven**; no architecture decisions are recorded. Feature planning stays on hold until Keel Part B PROOFs pass.

## Agenda (priority order)

1. **Confirm the scaffolding exists.** Ask Code to confirm `documents/` and the four root docs (`architecture.md`, `decisions.md`, `findings.md`, `test plan.md`) are created and committed. If not, that is the first build order.
2. **Resolve D-001 — decision-log structure.** KEEL numbered D-files vs. single `decisions.md`. Decide, then log it as the first entry.
3. **Verify / finish Keel Part B.** Walk Steps 10–15:
   - Choose the **hosting platform** first — it drives CI/CD, secrets, and deploy mechanics.
   - Stand up **self-contained tests** (no network, no live services) — do this one early; it makes the rest cheap.
   - Build **the gate** (tests must pass to ship; ship by merging), then **prove it** by pushing a failing test and watching it get blocked.
   - Turn on **branch protection** (require PR, require the check, no bypass — not even for the Owner).
   - **Kill hand-deploy.** Merging is the only way to ship.
   - Nothing counts until the PROOF is witnessed.
4. **Only then: first architecture pass.** High-level component map for MESG:
   - (a) source ingestion, (b) language / analysis engine, (c) signal + alert logic and 1–5 scoring, (d) storage, (e) delivery (web app, email, SMS), (f) auth + whitelist.
   - Capture as `architecture.md` v0, with the reasoning behind each choice recorded as D-entries.

## Decisions pending — need Owner input

- **Decision-log structure** (D-001 candidate; see close-out §5).
- **Hosting platform** — determines Steps 12–15 mechanics and the secrets model.
- **Language / framework** — `README` and `.gitignore` imply Python; confirm, and pick a web framework.
- **Email provider and SMS provider** — affects secrets and architecture.
- **v1 source scope** — which languages/dialects/outlets from `Languages_and_Religions.md` do we start with? Planner's recommendation: a **narrow v1** (one or two language communities) to prove the pipeline end-to-end before adding breadth.

## Questions for the Owner

- Is the repo currently **Public**? (Required for Planner's direct view. Go Private at the first real credential, first real user data, or first live deploy.)
- Where do we stand on the **legal / ToS / ethics** of collecting and analyzing sources? We need a position before building ingestion.
- Who is the **initial whitelist** (even just you) for testing daily-brief, alert, and Friday-summary delivery?

## Definition of done for next session

- Scaffolding confirmed committed.
- D-001 (decision-log structure) logged.
- Hosting platform chosen and logged as a decision.
- A concrete plan for — or completion of — the remaining Keel Part B steps.
- If the Keel is proven: `architecture.md` v0 drafted, with matching D-entries.

## The discipline — reminder

Lay the Keel before features. Witness every PROOF with your own eyes. Every claim names its source artefact. Every decision written down before the work is finished — with the option you rejected and the evidence behind the call. Close out every session, commit it, start fresh.
