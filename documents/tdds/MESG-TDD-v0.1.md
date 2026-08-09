# Technical Design Document — MESG v0.1

**Doc ID:** TDD-001
**Title:** Middle East Signal Generator — System Architecture
**Status:** DRAFT (Planner output, for Code analysis and Owner review)
**Author:** Planner
**Date:** 2026-08-02
**Keel version:** v5
**Related:** `MESG-close-out-2026-08-02.md`, `Languages_and_Religions.md`, CORE brief

> **KEEL sequencing note.** This is a design artifact. Per KEEL, **execution does not begin until Keel Part B is laid and every PROOF is witnessed** (tests, the gate, prove-the-gate, branch protection, hand-deploy killed). Every *proposed* technology choice below (marked **⟐ DECISION**) must be resolved and written to the decision log before Code executes against it. This document is the "constructive" TDD; the open **⟐ DECISION** items are the surviving questions from the exploratory phase that still need resolving.

---

## 1. Purpose and scope

MESG collects information in the languages of the Middle East, analyzes it with an intelligence-analyst's skepticism, and separates **what people in-region are saying** from **what English-language media reports** — surfacing the points of divergence and convergence. It delivers a **daily brief**, **event bulletins/alerts**, and **early signals of imminent action** to a whitelisted audience via **web application, email, and SMS**.

This TDD covers the whole-system architecture at v0.1. It defines components, data model, the analytic methodology, the web app (React), security, testing, and a phased build. It deliberately proposes a **lean v1** and defers breadth.

## 2. Design principles

1. **Provenance-first.** Every analytic claim in the system links to the raw item(s) it came from. This is CORE Role 2 and KEEL Principle 8 built into the schema: a claim with no artefact is not stored as a finding. A grade cannot exceed "unconfirmed" without a corroborating artefact on record.
2. **Skeptical by default.** The pipeline assumes a claim is unproven until access + corroboration justify otherwise. Summaries never overwrite raw evidence; the raw item is always reachable in one hop.
3. **Self-contained testability.** No component's unit tests touch the network or a live service (KEEL Principle 5). The LLM, translation, email, and SMS providers all sit behind interfaces that are mocked in tests.
4. **Start simple.** Username/password auth, one hosting platform, a narrow source set for v1. Complexity is added only after the pipeline is proven end-to-end.
5. **Human-in-the-loop before it goes loud (v1).** Bulletins and alerts are *reviewed and released*, not auto-blasted, until the grading earns trust. A false "coup" alert by SMS is expensive; the safety net is a release gate.

## 3. System overview

```
                 ┌─────────────────────────────────────────────────────┐
                 │                   SCHEDULER / JOBS                    │
                 └───────┬───────────────┬───────────────┬──────────────┘
                         │               │               │
   SOURCES          ┌───▼────┐      ┌────▼─────┐    ┌────▼──────┐
   (native-lang  →  │ INGEST │  →   │TRANSLATE │ →  │  ANALYZE  │
   news, feeds,     │        │      │(preserve │    │  ENGINE   │
   discussion,      │ dedupe │      │ original)│    │           │
   English media)   └───┬────┘      └────┬─────┘    └────┬──────┘
                        │                │               │
                     ┌──▼────────────────▼───────────────▼──┐
                     │             DATA STORE               │
                     │ raw items · stories · analyses ·     │
                     │ divergence · signals · briefs ·      │
                     │ users · recipients · delivery logs   │
                     └──┬───────────────┬──────────────┬────┘
                        │               │              │
                  ┌─────▼─────┐   ┌─────▼─────┐   ┌────▼────────┐
                  │  SIGNAL / │   │   BRIEF   │   │  DELIVERY   │
                  │  ALERT    │   │ GENERATOR │   │ email · SMS │
                  │  ENGINE   │   │ daily +   │   │ (whitelist) │
                  └─────┬─────┘   │ weekly    │   └────┬────────┘
                        │         └─────┬─────┘        │
                        └───────────────┼──────────────┘
                                        │
                            ┌───────────▼───────────┐
                            │   API BACKEND (REST)   │
                            └───────────┬───────────┘
                                        │
                            ┌───────────▼───────────┐
                            │   WEB APP  (React)     │
                            │ login · dashboard ·    │
                            │ story detail · alerts ·│
                            │ weekly · admin         │
                            └───────────────────────┘
```

**Data flow (one cycle):** scheduler fires → ingest pulls new items and dedupes → translate to a working language while preserving the original → analyze (cluster into stories, assess access + veracity, corroborate, compare in-region vs. English media, grade 1–5) → detect bulletin-worthy signals → generate the brief → queue delivery → a human reviews and releases → email/SMS go out to the whitelist; the web app reads everything from the store.

## 4. Component specifications

### 4.1 Ingestion

- Pulls from configured **Sources** on a schedule. Source types: RSS/Atom feeds, site scrapers, public APIs, and (later) discussion-platform collectors.
- **Deduplication** by content hash + near-duplicate detection.
- **Source-liveness tracking.** Each source's last-seen timestamp is recorded. A source that goes unexpectedly silent is itself a signal ("sudden disappearance of a news source" from the bulletin taxonomy).
- Records the fetch artefact for every item: source, URL, fetch time, original language, raw text/hash. Nothing is analyzed that has no fetch record.
- **⟐ DECISION:** per-source collection method and rate/politeness limits; respect for ToS/robots (see Risks §14).

### 4.2 Translation

- Translates in-region content into the **working language** (English) for analysis while **preserving the original verbatim**. Both are stored; the original is the artefact of record.
- Interface-based (`Translator`) so the provider is swappable and mockable.
- **⟐ DECISION:** translation provider (LLM-based translation vs. dedicated MT service).

### 4.3 Data store

- Relational store holding raw items, stories, analyses, divergence records, signals, briefs, users, recipients, and delivery logs (schema in §6).
- **⟐ DECISION:** PostgreSQL proposed (relational integrity for users/whitelist/delivery + JSON columns for flexible analytic payloads; a vector extension can be added later for semantic clustering).

### 4.4 Analysis engine (the core)

For each cluster of related items ("story"), the engine produces a structured analysis (methodology in §9):

1. **Facts** — what is claimed, stripped of framing, each fact tied to its source item(s).
2. **Source access + reliability** — for each contributing source, an assessment of whether it has *direct access* to the event and its *track record* (§9.1).
3. **Corroboration** — cross-source and, where possible, **orthogonal/indirect** corroboration (the "verify units shipped via the packaging supplier" pattern): official gazettes, market moves, transport trackers, imagery, physical proxies. v1 does LLM-assisted corroboration against a checklist; richer proxy integrations are Phase 3.
4. **In-region vs. English-media comparison** — two summaries (native-language voices; English-language outlets) plus an explicit list of **divergence** and **convergence** points. This is the product's reason to exist.
5. **Probability-of-truth grade (1–5)** — graded against contrary evidence (§9.2), **capped at 3 when corroboration is absent**.
- Interface-based (`Analyst`/LLM client) so it is mockable; deterministic fixtures drive tests.

### 4.5 Signal / alert engine

- Classifies stories against the **bulletin event taxonomy** and assigns severity:
  - military event · natural disaster · incident · outbreak · assassination · arrest of a political figure · arrest of a major cultural influencer · sudden disappearance of a news source · uprising · coup.
- Emits **early signals of imminent action** when leading indicators cluster (e.g., mobilization chatter, unusual official silence, market/logistics anomalies) even before a confirmed event.
- Each signal carries its grade and its artefacts, and enters the **review-and-release** queue (v1).

### 4.6 Brief generator

- **Daily brief** — bulleted; per item: *facts → analysis → probability grade (1–5) with the contrary evidence weighed*. Matches the CORE Example format exactly.
- **Friday "What mattered this week"** — weekly synthesis generated Friday afternoon: the stories that moved, what converged/diverged, what to watch.
- Output stored as a `Brief` record; rendered in the web app and formatted for email/SMS.

### 4.7 Delivery

- Channels: **email** and **SMS**, plus the **web app** (always the system of record).
- **Whitelist-enforced**: delivery only ever goes to active, opted-in recipients the Owner has approved. Enforcement happens at the delivery layer, not the caller.
- Interface-based (`EmailProvider`, `SmsProvider`); both mocked in tests. Every send writes a `DeliveryLog` (recipient, channel, item, status, timestamp).
- **⟐ DECISION:** email provider; SMS provider.

### 4.8 Web application

- **React** single-page app (per Owner) talking to the REST API. Pages in §8.
- Auth: username/password to start (§10).

## 5. Scheduling and cadence

| Job | Cadence | Output |
|---|---|---|
| Ingest + translate + analyze | Recurring through the day (e.g., hourly) | Updated stories, analyses |
| Signal/alert scan | Each cycle | New signals → review queue |
| Daily brief | Once daily (morning) | Daily brief → review → email + web |
| Bulletins/alerts | Event-triggered, throughout the day | Alert → review → email + SMS |
| Weekly summary | Friday afternoon | "What mattered this week" → email + web |
| Source-liveness check | Each cycle | Silence flags |

**⟐ DECISION:** scheduler mechanism (platform cron vs. in-app scheduler vs. task queue). Start with the simplest that the chosen platform supports.

## 6. Data model (core entities)

| Entity | Key fields | Notes |
|---|---|---|
| `User` | id, username, password_hash, role, active | App login accounts. |
| `Recipient` | id, name, email, phone, channels[], active, approved_by | The whitelist. May reference a `User` or stand alone. **PII** — see §10. |
| `Source` | id, name, url, language, dialect, type, region, credibility_prior, last_seen_at, active | Seeded from `Languages_and_Religions.md`. |
| `RawItem` | id, source_id, fetched_at, original_lang, original_text, working_text, url, content_hash | The artefact of record. `working_text` = translation. |
| `Story` | id, title, event_type, status, first_seen_at, last_updated_at | A cluster of related items. |
| `StoryItem` | story_id, raw_item_id | Many-to-many link. |
| `Analysis` | id, story_id, facts_json, analysis_text, probability_grade (1–5), contrary_evidence, generated_at, reviewed_by | `facts_json` items each carry source `raw_item_id`s. |
| `SourceAssessment` | id, analysis_id, source_id, access_level, reliability, rationale | Per-source access + track-record judgment. |
| `Divergence` | id, story_id, in_region_summary, english_media_summary, divergence_points[], convergence_points[] | The core comparison. |
| `Signal` | id, story_id, type, severity, is_imminent, created_at, status | status ∈ {new, reviewed, released, suppressed}. |
| `Brief` | id, type (daily/weekly), for_date, content_json, generated_at, released_at, released_by | |
| `DeliveryLog` | id, recipient_id, channel, ref_type, ref_id, status, sent_at, error | Provenance for every send. |

## 7. API surface (representative)

```
POST /auth/login          POST /auth/logout        GET  /auth/me
GET  /briefs?type=daily|weekly                     GET  /briefs/{id}
GET  /stories             GET  /stories/{id}        (facts, analysis, grade, divergence)
GET  /signals             GET  /signals/{id}
POST /signals/{id}/release   POST /signals/{id}/suppress   (review gate)
GET  /admin/sources       POST /admin/sources       PATCH /admin/sources/{id}
GET  /admin/recipients    POST /admin/recipients    PATCH /admin/recipients/{id}
GET  /admin/settings      PATCH /admin/settings     (thresholds, cadence)
```

Scheduled pipeline triggers are internal, not public endpoints.

## 8. Frontend (React) design

- **Stack (proposed):** React + Vite. **⟐ DECISION:** TypeScript vs. plain JS — Planner recommends TypeScript for maintainability of the analytic data shapes; Owner said "React.JS," so this is a flagged sub-decision. Routing via React Router; server state via a data-fetching layer (e.g., React Query); minimal global state.
- **Pages:**
  - **Login** — username/password.
  - **Dashboard** — today's daily brief, bulleted, each item expandable to facts → analysis → grade.
  - **Story detail** — full analysis: facts (with source links), per-source access/reliability, the in-region vs. English-media split, divergence/convergence, grade + contrary evidence.
  - **Alerts** — active bulletins/signals; review-and-release controls for authorized users.
  - **Weekly** — the Friday "What mattered this week."
  - **Admin** — sources, recipients (whitelist), thresholds/cadence.
- **Provenance in the UI:** every claim shows a path back to its raw item(s). This is not decoration — it is the product promise made visible.
- Protected routes; auth token handling per §10.

## 9. Analytic methodology (the intelligence-analyst core)

### 9.1 Source access + reliability

Adapted from established intelligence source-grading practice. Two axes, judged separately:

- **Access** — proximity to the event: *direct* (on-ground/eyewitness/participant) → *one-step* (local outlet relaying local sources) → *aggregator* (repackaging others) → *commentary* (opinion, no access).
- **Reliability** — the source's track record for accuracy over time.

A high-access source with a poor track record and a low-access source with a great track record are *different* problems; the schema records both so a later reviewer can see the reasoning.

### 9.2 Probability-of-truth scale (1–5)

| Grade | Meaning | Typical basis |
|---|---|---|
| 5 | Confirmed | Multiple independent, high-access sources; no credible contradiction. |
| 4 | Probably true | Two+ sources or one high-access source; minor gaps; no strong contradiction. |
| 3 | Unconfirmed / possible | Single credible source, plausible, **not yet corroborated**. *(Ceiling without corroboration.)* |
| 2 | Doubtful | Low-access source, thin corroboration, or partial contradiction. |
| 1 | Improbable / likely false | Contradicted by better evidence, or single low-credibility source against contrary indicators. |

**Guardrail (KEEL Principle 8 applied):** the grade is a judgment *against contrary evidence*, not a vote count. The engine must prefer the disqualifying question — ask what is *available*, not just what is *reported*; ask for the breakdown, not the headline total — and must record the artefact behind each fact. **No corroborating artefact ⇒ grade capped at 3.** This is what stops a confident summary from hiding the detail that would have reversed it.

### 9.3 Divergence / convergence

For every story the engine produces two independent summaries — in-region voices vs. English-language media — and enumerates where they agree and where they part. Divergence is frequently the signal: what the region is saying that English media is not (or vice versa) is often the most decision-relevant output MESG produces.

## 10. Security and privacy

- **Auth:** username/password to start. Passwords hashed (argon2 or bcrypt). **⟐ DECISION:** session cookies vs. JWT — Planner leans httpOnly session cookies for simplicity and safer defaults in a small trusted-user app.
- **Secrets:** every key/token lives in the **hosting platform's** secret store, referenced by name, never in a file or the repo (KEEL Principle 4 / Step 10). A secret-scanner sits in the gate.
- **Transport:** HTTPS only.
- **Whitelist:** delivery restricted to approved, active recipients; enforced at the delivery layer.
- **Rate limiting + input validation** on the API.
- **PII + the Private tripwire:** recipient emails and phone numbers are real user data. Per KEEL Principle 10, **the moment real recipient data (or the first real credential, or the first live deploy) lands, the repo flips to Private** and the Planner reverts to hand-fed snapshots. Plan the flip; don't be surprised by it.

## 11. Testing strategy

Feeds `test plan.md` (tabular). All unit tests are **self-contained — no network, no live services** (KEEL Principle 5):

- **Mocks/fakes** for `Translator`, `Analyst` (LLM), `EmailProvider`, `SmsProvider`, and source fetchers.
- **Fixtures** — canned raw items (multi-language) drive deterministic clustering, grading, and divergence tests.
- **Grading rubric tests** — assert the corroboration cap (no artefact ⇒ ≤3) and contrary-evidence handling.
- **Whitelist tests** — assert delivery never reaches a non-approved recipient.
- **API tests** — auth, protected routes, review-and-release transitions.
- **Frontend tests** — component/interaction tests (e.g., Vitest + React Testing Library).
- **Integration/e2e** (real providers) run **separately** from the unit suite, never in the gate's fast path.

## 12. Deployment and environments

- Platform-agnostic PaaS. **CI runs the self-contained suite → gate blocks on failure → deploy happens by merging** (KEEL Steps 12–15). Secrets in the platform; DB migrations on deploy.
- **⟐ DECISION:** hosting platform (drives CI/CD, secrets, and deploy mechanics — pick this early; much downstream depends on it).

## 13. Technology stack (proposed — each a decision to log)

| Layer | Proposed | Status |
|---|---|---|
| Frontend | React + Vite (+ TypeScript, recommended) | **⟐ DECISION** (TS vs JS) |
| Backend/API | Python + FastAPI | **⟐ DECISION** |
| Database | PostgreSQL | **⟐ DECISION** |
| Translation | LLM or MT service (interface-based) | **⟐ DECISION** |
| Analysis | LLM client (interface-based) | **⟐ DECISION** |
| Email | transactional email API | **⟐ DECISION** |
| SMS | programmable SMS API | **⟐ DECISION** |
| Scheduler | platform cron / task queue | **⟐ DECISION** |
| Hosting/CI | PaaS with CI gate | **⟐ DECISION** |
| Auth | username/password, hashed; session cookies | **⟐ DECISION** |

The `.gitignore` already present is Python-oriented, consistent with the FastAPI proposal.

## 14. Phasing / roadmap

- **Phase 0 — Keel proven (prerequisite).** No feature work until Part B PROOFs are witnessed.
- **Phase 1 — MVP.** Narrow source scope (one or two language communities from `Languages_and_Religions.md`); ingest → translate → cluster → analyze → **daily brief**; web app (login, dashboard, story detail, admin for sources + recipients); **email** delivery; basic auth; **review-and-release** gate.
- **Phase 2.** SMS bulletins + full bulletin-event detection + **Friday weekly summary** + source-liveness alerts.
- **Phase 3.** Broaden sources; richer indirect-corroboration proxies; semantic clustering (vector search); grading refinement; consider selective auto-release once grades are trusted.

## 15. Open decisions → D-entries needed

Log each before Code executes against it (the decision-log structure itself is **D-001**, still pending from the close-out):

1. Decision-log structure (D-001, carried over).
2. Hosting platform.
3. Backend framework (FastAPI proposed).
4. Database (PostgreSQL proposed).
5. Frontend language (React JS vs TS).
6. Translation provider.
7. Analysis/LLM provider.
8. Email provider.
9. SMS provider.
10. Scheduler mechanism.
11. Auth mechanism (session vs JWT).
12. v1 source scope (which languages/outlets first).

## 16. Risks

- **Source legality / ToS / blocking.** Collection may breach terms or trigger rate-limiting/bans. Needs an explicit position before ingestion is built; prefer feeds/APIs and permitted sources first.
- **Analytic hallucination.** An LLM analyst can invent corroboration. Mitigations: provenance-first schema, the "no artefact ⇒ ≤3" cap, and the human review gate before anything goes out in v1.
- **False bulletins.** A wrong "coup/assassination" alert by SMS is costly and erodes trust. Mitigation: review-and-release in v1; earn auto-release later.
- **PII handling.** Recipient contact data triggers the Private flip and carries a duty of care.
- **Cost/scale.** Continuous translation + analysis across many sources is expensive. Mitigation: narrow v1, cache aggressively, cluster before analyzing.
- **Scope creep.** The domain is vast. Mitigation: prove one pipeline end-to-end before breadth.

---

*Planner draft for Code to analyze. Code: please return feedback on feasibility, the proposed stack, the data model, and anything that fights the Keel. Owner will relay, then issue the execute order — after the Keel is proven.*
