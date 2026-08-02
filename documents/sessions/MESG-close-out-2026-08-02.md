# MESG — Session Close-Out

**Date:** 2026-08-02 (Sunday)
**Session type:** Planner session — project grounding, operating model, repo state
**Roles present:** Planner (Claude.ai, this chat) + Owner. Code (Claude Code) not in this session.
**Keel version:** v5

---

## 1. Purpose of this session

Put the project on solid ground before any feature work: confirm the operating brief (CORE), confirm KEEL v5 as the governing discipline, confirm the Planner / Code division of labor, and ground on the current repo state.

## 2. What we did

- Confirmed the **CORE brief** for MESG (Context / Objective / Role / Example). Recorded verbatim in §6 so it survives outside this chat.
- Adopted **KEEL v5** as the governing discipline. Lay the Keel and witness every PROOF before feature work begins.
- Confirmed the **two-AI operating model**:
  - **Planner** (this chat): thinks, architects, drafts build orders + TDDs with the Owner. Sees only the connected repo plus what it is handed.
  - **Code** (Claude Code, local): executes. Reads and analyzes each build order + TDD, returns feedback, waits for an explicit execute order, then codes.
  - **Handoff path:** Planner + Owner draft → `downloads` → Code files into `documents/` → Code analyzes and feeds back → Owner relays feedback to Planner → Owner issues execute order → Code codes.
- Grounded on repo state as visible to Planner (§3) and assessed KEEL Day-One status honestly (§4).

## 3. Repo state as visible to Planner (ground truth)

Files currently visible via the connected repo:

- `README.md` — placeholder (project title only).
- `.gitignore` — Python-oriented; **`.env` is ignored** (good — the Principle 4 / Step 10 baseline is in place).
- `Languages_and_Religions.md` — domain reference: Middle East languages, dialects, sects, and candidate news sources.

**Not yet visible to Planner (confirm with Code):**

- The `documents/` directory and the four root docs directed in the day-one order — `architecture.md`, `decisions.md`, `findings.md`, `test plan.md`. Planner cannot see these. **First item next session:** confirm they were created and committed, or issue that as the first build order.

## 4. KEEL Day-One status (honest read)

**Part A — Workshop**

- Project + name: assumed done (this Project exists).
- Repo created: yes (`README.md` present).
- Repo PUBLIC + connected to Planner: **appears connected** (Planner can read repo files). Confirm it is set to Public.
- Local workshop at `c:/projects/projectMESG`: reported by Owner.
- Builder (Code) connected: yes, per the operating model.

**Part B — Lay the Keel: NOT yet verified.**

- Docs home + decision log: partial — see §5 divergence flag.
- Secrets out: baseline only (`.env` gitignored). Secret-scanner in the gate not confirmed.
- Self-contained tests: not confirmed.
- The gate (tests must pass before anything ships): not confirmed.
- Prove the gate / branch protection / kill hand-deploy: not done.
- Hosting platform, email provider, SMS provider: not chosen.

**Consequence:** Per KEEL, feature planning does not begin until Part B PROOFs are witnessed. We are not there yet, and that is fine — we are exactly where a day-one project should be.

## 5. Flag for reconciliation — decision-log structure

The day-one order directs a single consolidated `decisions.md`. KEEL v5 (Principle 7 / Step 8) prescribes `docs/decisions/` with **one file per decision, numbered D-001, D-002…**, each carrying five fields: *decision · context · options rejected · evidence · supersedes*. KEEL is emphatic that the numbered, one-file-per-decision structure — with the rejected options and the supersedes field — is what makes the log **recoverable** ("we were sound up to D-023, go straight to it").

This is a genuine divergence, and it is the Owner's call. But it should be resolved deliberately and **logged as our first decision (D-001)** whichever way it goes.

**Planner's recommendation:** adopt the KEEL structure (`docs/decisions/` + numbered D-files) and keep a top-level `decisions.md` only as an index/table-of-contents that points at the D-files. That gives both the single-glance view and KEEL's recoverability.

## 6. CORE brief (recorded so it survives this chat)

**CONTEXT:** Coverage of Middle East events is poor because we depend on biased, agenda-driven, English-language news outlets and cannot read the languages of the region. The result is a hazy picture of events unfolding in real time.

**OBJECTIVE:** Separate what people in-region are actually saying from what English-language media reports, and identify where the two diverge and converge. Aggregate, analyze, and distill into a **daily brief**, **alerts**, and **early signals of imminent action**, delivered via a **web application**, **text messages**, and **email** to a whitelisted group the Owner selects. Security starts simple: username and password.

**ROLE 1 — Collector:** expert at finding discussions, published news, and information exchanges affecting speakers of Middle East languages.

**ROLE 2 — Analyst:** a skeptical, objective intelligence analyst. Assess each source's *access* to what it claims, and the *veracity* of the claim. Corroborate by any means, including unorthodox, indirect methods (the "count the packaging supplier's units to verify the shipping claim" approach).

**EXAMPLE output:** a bulleted daily summary; for each item — the facts, then the analysis, then a probability-of-truth judgment weighed against contrary evidence, graded 1–5. Bulletin-worthy events (military action, natural disaster, incident, outbreak, assassination, arrest of a political figure or major cultural influencer, sudden disappearance of a news source, uprising, coup) go out daily by email and text. A **"What mattered this week"** summary goes out **Friday afternoon**.

## 7. Open items → carried to next session

1. Confirm the `documents/` scaffolding and four root docs exist and are committed.
2. Resolve **D-001** — decision-log structure (see §5).
3. Verify / finish **Keel Part B** (Steps 10–15): pick a hosting platform, stand up self-contained tests, build and *prove* the gate, turn on branch protection, kill hand-deploy.
4. Only after the Keel is proven: first architecture pass for MESG.

## 8. Risks / watch items

- **Legality and ethics of source collection** (scraping, elicitation, ToS) — unscoped. Needs a position before we build ingestion.
- **The analysis engine** — "what people say vs. what English media reports" — is the hard core of the product and is entirely undefined.
- **Delivery stack** (web + email + SMS) and **auth** (username/password to start, whitelist management) — undefined.
- **No hosting / CI/CD chosen** → Keel Part B cannot be verified until it is.

---

*This close-out is the baton. Commit it to the repo. Next session starts by reading it — not by reopening this chat.*
