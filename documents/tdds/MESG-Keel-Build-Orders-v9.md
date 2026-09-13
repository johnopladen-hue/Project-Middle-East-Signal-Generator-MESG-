# MESG — Keel Build Orders

**Doc ID:** ORD-001
**From:** Planner
**To:** Builder (Code)
**Keel version:** v9
**Date:** 2026-09-13
**Status:** ISSUED — execute in order
**Related:** `MESG-TDD-v0.1.md`, `Languages_and_Religions.md`, KEEL v9 doctrine set

---

## 0. Read this first

You are laying the **Keel** for MESG — version control, tests, automated deploy, and the five reasoning documents — **before any feature work**. Nothing feature-related begins until **O-15** passes and every PROOF below has happened.

- **This document is authoritative.** It consolidates and **supersedes all prior verbal orders** from the planning session. Where memory and this document disagree, this document wins.
- **Do not execute feature work from the TDD.** `MESG-TDD-v0.1` is a design artifact. Its `⟐ DECISION` items are either resolved into the decision ledger in §2 or remain explicitly open for the feature phase.
- **Roles.** You (Code) work as the Owner, in the trenches — you write code, run tests, ship. The Owner performs rulings, credentials, destructive operations, and branch protection (steps marked **[OWNER]**). The Planner does not touch the repo.
- **Ground before you act (Standing Order 1).** Verify state against the live repo; do not trust this document's description of the current tree.

---

## 1. Standing orders (apply to every order)

1. Before any feature work, confirm the foundation exists. You are laying it now — nothing else starts until O-15.
2. Tests are self-contained: no network, no live services, no secrets.
3. Every result you report names the artefact behind it (a command's output, a file, a run link) **and** its count. No summary stands in for evidence.
4. Cite decisions by number **and** name — "D-002 (adopt Keel v9)", never a bare `D-002`.
5. Never assert something is absent from a copy. Verify against the live repo, or phrase it as a question.
6. Before anything destructive (there should be nothing yet), stop and say the three backup sentences out loud first: a completed backup exists; how old it is, as exposure; what it does not cover.

---

## 2. Decision ledger to create

Write these into `decisions.md` with the seven-field template (decision · context · options rejected · evidence · supersedes · assumptions relied on · amended by). The wording below is canonical; the order that commits each is noted in brackets.

- **D-001 — Documentation & decision-log structure.** [O-3] Five named files in `docs/` (`architecture.md`, `decisions.md`, `findings.md`, `testplan.md`, `assumptions.md`); decisions numbered `D-NNN`; cited by number + name. *Rejected:* a single README with sections. *Evidence:* KEEL v9 Principle 7 and its blood line — decisions buried in `docs/README.md`, undiscoverable to anyone who didn't invent the convention.
- **D-002 — Adopt Keel v9.** [O-3] *Supersedes:* the v5 the TDD cites. Re-stamp the TDD to v9. *Rejected:* staying on v5. *Evidence:* v9 supersedes v5/v7/v8, adds Principle 11, the five-document model, and the destructive-ops rule; v9's own blood line names this project's orphaned assumption numbers.
- **D-003 — MMP as UX reference only.** [O-3] Replicate mappingmilitants.org's maps/profiles/networks **shape** for an actor/relationship layer, in our own React/Vite stack. *Rejected:* adopting their Backdrop CMS; making MESG "exactly" MMP (would lose the brief/alert spine that is the objective). *Evidence:* fetched 2026-09-13 — Rice-hosted beta, three-view shape; TDD objective is signal/divergence, not a relationship catalog.
- **D-004 — MMP data not scraped.** [O-3] Do not ingest MMP content; if ever used, cited enrichment only, decided in the feature phase. *Rejected:* scraping profiles to seed our DB. *Evidence:* MMP profiles are copyrighted, DOI/citation-bound academic work; TDD §14 source-legality risk and §4.1 collection-method decision; MMP is slow, curated, and global — a poor fit for real-time in-region signals.
- **D-005 — Keel-proof stack = Python + FastAPI + pytest; CI on GitHub Actions.** [O-8] *Rejected:* other stacks for the proof vehicle. *Evidence:* matches the TDD's proposed backend and the existing Python `.gitignore`. Ratifies the *keel-proof* stack only; the React/Vite frontend and full backend remain feature-phase decisions.
- **D-006 — Hosting platform = Fly.io.** [O-9] *Rejected:* Render, Railway. *Evidence:* Owner ruling. The Fly deploy shape (Dockerfile + `fly.toml` + `flyctl deploy --remote-only`, secret `FLY_API_TOKEN`) is to be **verified against current Fly docs at the go-remote swap, not now.**
- **D-007 — Deploy target for now = localhost, via automated merge-triggered local deploy.** [O-9] Merge-on-green and "hand-deploy dies" hold and are **proven now** — a deploy is a deploy regardless of where the running version lives. The local deploy *mechanism* is throwaway; the Fly path replaces it at the go-remote tripwire (first real credential / first real user data / first remote deploy), which also flips the repo **private** (Principle 10). *Rejected:* treating localhost as "not really deployed" and carrying the deploy leg as debt — conflates hosting with deploy. *Evidence:* Owner ruling; Principle 3. *Assumptions relied on:* A-001.
- **D-008 — Local deploy mechanism = a local pull-restart agent, NOT a self-hosted GitHub Actions runner.** [O-9] *Rejected:* a self-hosted runner. *Evidence:* the repo is public (Principle 10); a self-hosted runner on a public repo permits forked-PR arbitrary code execution on the Owner's machine — a documented GitHub risk. CI (pytest + gitleaks) stays on GitHub's cloud runners, which need no local access. *Assumptions relied on:* A-001.

---

## 3. Assumptions to register

- **A-001 — The localhost deploy proves the deploy *pattern*, not the Fly *path*.** [registered via D-007/D-008 in O-9] *The test:* when Fly comes online, does a green merge auto-deploy to Fly on the first attempt with no hand-step? *What breaks if false:* we trust a deploy path that was never exercised. *Guard:* `testplan.md` carries the Fly path as owed-and-unproven; re-prove at the go-remote tripwire. *Relied on by:* D-007, D-008. *Status:* ASSUMED.

**Numbering hygiene — do not skip.** Register exactly the one assumption above as **A-001**. Do **not** create any entry for "localhost is not a proven system"; that draft carried a false premise (deploy ≠ remote hosting) and was withdrawn before commit. It gets no number. If O-1 finds any pre-existing orphaned `A-` citations in the repo, reconcile them in `assumptions.md` rather than leaving them to resolve to nothing.

---

## 4. The mechanism that shapes the build — the local deploy agent (D-008)

How a green merge reaches localhost, built right:

- **CI stays in the cloud.** pytest + gitleaks run on GitHub's runners on every PR and push. They need no access to the Owner's machine.
- **A local agent is the hands, not the gate.** Branch protection (O-12) guarantees nothing lands on `main` unless the checks passed — so "`main` moved" already means "`main` is green," and the agent may trust any new `main` HEAD without re-checking.
- **Agent loop:** detect a new `main` HEAD → `git pull` → rebuild → start the new version → **confirm it answers `/health`** → only then cut over. If the new version fails to start, keep the old process alive and surface the failure loudly. **Never leave localhost dark on a green merge** — a deploy that leaves you worse off, silently, is the scar.
- **OS:** you run as the Owner — inspect the machine directly, do not assume. Install the agent as a persistent background service via the platform's native manager: `launchd` (macOS), a `systemd` user service (Linux), or Task Scheduler / a service wrapper (Windows).
- **Trigger:** poll `git fetch` on `main` every 30–60s. Do not use a webhook — a webhook to localhost needs a tunnel and reintroduces the exact remote exposure D-008 avoids.
- **Disposable by design.** Delete the agent the day `flyctl` takes over.

---

## 5. PHASE 1 — the documentation half

Branch protection does not exist yet, so these commits go **direct to `main`** (expected bootstrap). Everything is PR-only from O-12 on.

**O-1 — Ground against live.** List the repo tree, report HEAD, confirm README + `.gitignore` present and no `docs/` yet. Grep the whole repo for existing `D-\d` / `A-\d` citations and any `MESG-close-out-*.md`. **PROOF:** you report the tree, HEAD, and whether a close-out or orphaned D-/A- citations exist.

**O-2 — Create the five documents.** `docs/` + `architecture.md`, `decisions.md`, `findings.md`, `testplan.md`, `assumptions.md` — headings only. Decisions do **not** go in a README. **PROOF:** five files exist, each with its heading.

**O-3 — Seed the decision log.** Put the seven-field template at the top of `decisions.md`, then write **D-001, D-002, D-003, D-004** (§2 wording), each with real rejected options and evidence. **PROOF:** open any one — it names what was rejected and why.

**O-4 — Seed findings.** Write the rule at the top of `findings.md` (every claim names its artefact + n). Record one real entry: the fetched state of mappingmilitants.org (Rice-hosted, beta, maps/profiles/networks shape), artefact = the fetch, dated 2026-09-13. **PROOF:** rule + one artefact-backed entry present.

**O-5 — Set up the assumption register.** Put the `A-NNN` template + the two bars in `assumptions.md` (no falsifying test → not an entry; nothing breaks if false → a detail). Reconcile any orphans found in O-1, or record that there were none. It may be empty at this point — an empty `assumptions.md` is legible; that is fine. (A-001 is registered in Phase 2 as a by-product of D-007/D-008.) **PROOF:** template + two bars present; orphans reconciled or explicitly none.

**O-6 — First architecture paragraph.** Write the real opening of `architecture.md` from the TDD (the components, what is deliberately absent in v1). It will be wrong within a week; updating it is the job. **PROOF:** a real opening paragraph, not a placeholder.

**O-7 — Confirm secrets are locked out.** Verify `.gitignore` covers `.env`. No secrets exist yet; the scanner is wired in O-9. **PROOF:** `.env` confirmed ignored.

---

## 6. PHASE 2 — the enforcement half

**O-8 — Stand up the keel-proof app.** One FastAPI endpoint `GET /health → {"status":"ok"}`, pytest, and one trivial self-contained test. Log **D-005**. **PROOF:** pytest passes in seconds with internet **off**.

**O-9 — Build the gate and the local deploy.** GitHub Actions workflow: on PR and push, run **pytest** and **gitleaks** (or equivalent secret scanner) as **required** checks on cloud runners. Build the local deploy agent per §4 and install it as a background service for the detected OS. Log **D-006, D-007, D-008** and register **A-001**. **PROOF:** a PR shows both checks running; the agent is installed and running.

**O-10 — [OWNER] Nothing to do now — and note why.** No `FLY_API_TOKEN` (Fly deferred, D-007), no runner registration (D-008 uses none), and reading a public repo needs no token. This step re-activates only at the go-remote swap. **PROOF:** confirmed no credential is required to run the keel today.

**O-11 — Prove the gate (all three clauses).** Push a branch that breaks the `/health` test with a value no correct version could produce (e.g. assert it returns `"DOWN"`). Confirm a **failure-red**, not an import/error-red — the assertion actually ran — and that the deploy does **not** happen. Then fix, merge, and watch the agent redeploy localhost with no command from you; confirm `/health` reflects the new code. Record all three in `testplan.md`: gate blocks bad; assertion truly executed; good merge deploys itself. Add the **Fly path as not-yet-proven (A-001)**. **PROOF:** the Owner has watched a bad build blocked and a good one deploy itself to localhost; `testplan.md` says so.

**O-12 — [OWNER] Make the check binding.** Branch protection on `main`: require a PR, require the pytest + gitleaks checks, **no bypass — including the owner**. Push straight to `main` and watch it refused. **PROOF:** direct push refused to the owner; a failing PR reads **BLOCKED**, not merely a red X.

**O-13 — Hand-deploy dies today.** Merging is the only way the running version updates. You never restart the local service by hand again; manual restart is break-glass only. **PROOF:** a merged change reaches local `/health` with no hand-command.

**O-14 — Write the test plan.** `testplan.md` gets its two standing headings: **Covered** and **Deliberately not covered, and why**. Record the O-11 gate proof. Record, as deliberately-not-covered-yet: the DB-safety guard (suite must hard-error against a non-expendable database — no DB exists yet) and the Fly deploy path (A-001). **PROOF:** both headings + the gate-proof entry + the two deferrals present.

**O-15 — Close out and report.** Write the session close-out to `docs/` (done · open · next); answer "which of the five documents changed today?"; commit via PR. Report back to the Planner for next session: HEAD, highest `D-` number, highest `A-` number, the open-items list, and the local `/health` URL. **PROOF:** close-out committed; grounding block reported.

---

## 7. Deliberately deferred — owed debt, tracked (do not silently drop)

- **Fly deploy path** — re-prove at the go-remote tripwire (A-001).
- **Go-private flip** — at the first real credential / real user data / remote deploy (Principle 10).
- **DB-safety guard** — when the database lands (testplan.md holds the placeholder).
- **All feature work** — nothing starts before O-15 passes.

---

## 8. Definition of done — the Keel is laid when all of these are true

- All five documents exist in `docs/`, and at least `decisions.md`, `findings.md`, and `testplan.md` have real content.
- `D-001`–`D-008` are logged; `A-001` is registered; numbering is clean with no orphans.
- pytest runs self-contained and passes with the internet off.
- The gate has been seen to **block a bad build** (failure-red, assertion proven to run) and **deploy a good one to localhost by itself**.
- Branch protection refuses a direct push to `main`, to the owner.
- No hand-command ships or restarts anything.
- The close-out is committed and the grounding block reported.

Only then does the first feature get planned.
