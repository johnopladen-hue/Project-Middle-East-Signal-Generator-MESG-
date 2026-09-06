# MESG — Web UI Specification & Orders for Claude Code

**Doc ID:** UI-SPEC-001
**Title:** Middle East Signal Generator — Frontend (React / Node·JS) Specification and Build Orders
**Status:** DRAFT — Planner output, for Owner review and (once gated) Builder execution
**Author:** Planner
**For:** Claude Code (the Builder)
**Related:** `MESG-TDD-v0.1.md` (TDD-001), `Languages_and_Religions.md`, CORE brief, KEEL doctrine set
**Stack ruling captured here:** React + Vite, **JavaScript (JSX), not TypeScript** — per Owner ("React.JS")

---

## 0. Read this before you touch anything

> **KEEL sequencing gate.** This document is a *design artifact*. It is Planner work and it may be written now. It may **not** be executed until **Keel Part B is laid and every PROOF is witnessed** — self-contained tests, the gate, prove-the-gate, branch protection, hand-deploy killed (TDD §12, §14; Checklist Steps 11–16). Frontend work is **Phase 1** (TDD §14). **Phase 0 is a prerequisite.** Order 0 below is the hard gate; do not start Order 1 until Order 0 passes.

> **Doctrine version note.** The Owner's standing instruction is **Keel v5**. The repository also now contains a **v9** doctrine set (five named documents in `docs/`, additional principles). This spec is written to sit correctly under either: where it refers to "the decision log," read that as `docs/decisions/D-###.md` under v5, or `docs/decisions.md` under v9 — whichever the Owner has ruled governs. Do not resolve that ambiguity yourself; ask the Owner if it blocks you.

> **What you are and are not.** You are the Builder. You act on what you are handed, fast, and your mistakes ship before anyone reads them (KEEL, "three players"). So: every order ends with a **PROOF** you must witness, and every test you write must be **self-contained — no network, no live services** (KEEL Principle 5). If a proof does not happen, **stop on that order and fix it** before moving on.

---

## 1. Scope

Build the **web application** described in TDD §4.8 and §8 — the system of record and the human surface for MESG. In v1 it must let a small, trusted, whitelisted set of users:

1. Log in (username / password).
2. Read **today's daily brief**, each item expandable from headline → facts → analysis → probability grade (1–5) with the contrary evidence weighed.
3. Open a **story** in full: facts with source links, per-source access + reliability, the **in-region vs. English-media** split, divergence/convergence, grade + contrary evidence.
4. See **alerts / signals**, and — if authorized — **review and release or suppress** them (this is what sends email/SMS, so it is a deliberate, confirmed action).
5. Read the **Friday "What mattered this week"** summary.
6. Administer **sources**, **recipients (the whitelist)**, and **thresholds/cadence** (admin role only).

Everything the UI shows that is an analytic claim must carry a path back to the raw item(s) it came from. **Provenance is not a feature of this UI; it is the point of it** (TDD §2, §8 "Provenance in the UI"; KEEL Principle 8).

Out of scope for v1 UI: dark theme (defer), internationalized UI chrome (the *content* is multilingual; the *chrome* is English v1), auto-release of alerts (human-in-the-loop first, TDD §2.5).

---

## 2. Frontend decisions to log before execution (⟐ → D-entries)

These come out of TDD §13/§15. Each must have a decision-log entry before you build against it. Rulings the Owner has already made are marked **RULED**; the rest are **OPEN** and block the orders they touch.

| # | Decision | Proposal / Ruling | Blocks |
|---|---|---|---|
| F-1 | Frontend language | **RULED: JavaScript (JSX), not TypeScript.** Mitigation for lost type-safety on the analytic data shapes: JSDoc `@typedef`s + runtime **PropTypes** on every component (see §8). Log this ruling *and* its mitigation as one D-entry. | Order 1 |
| F-2 | Data-fetching / server-state layer | **Propose: TanStack Query (React Query).** Rationale: caching, loading/error states, refetch on focus — all of which this read-heavy app needs and which you would otherwise hand-roll badly. | Order 3 |
| F-3 | Auth transport | **Propose: httpOnly session cookie** (TDD §10 leans this). Frontend impact: API client sends `credentials: 'include'`; no token in JS-readable storage. If Owner rules JWT instead, auth handling in §7-Login and §5-Auth changes. | Order 3 |
| F-4 | Styling system | **Propose: Tailwind CSS with a semantic token layer** mapped to the palette in §3, so tokens (not raw hex) are used in markup. Fallback if Owner prefers no build-time CSS dep: CSS variables + CSS Modules using the same tokens. | Order 2 |
| F-5 | Icon set | **Propose: `lucide-react`** — restrained, consistent, tree-shakeable. | Order 2 |
| F-6 | Routing | **Propose: React Router v6.** | Order 1 |
| F-7 | Roles in v1 | **Propose two roles:** `admin` (everything, incl. Admin section + release/suppress) and `viewer` (read briefs/stories/weekly; no release, no admin). `User.role` already exists in the data model (TDD §6). A third "reviewer" role is deferred. | Orders 4, 8, 10 |

**Do not silently adopt a proposal by building against it.** Adopting it *is* the D-entry. If you find yourself relying on something not in this table, that is an assumption — name it (v9: `assumptions.md`; v5: note it in the decision entry that relies on it).

---

## 3. Design system

The design is grounded in the subject: **an intelligence analyst's reading and triage tool.** Its job is sustained reading, fast triage, and — above all — making *provenance* and *divergence* legible at a glance. The visual identity is **"the reading room": calm, high-legibility, instrument-like**, not a spy-movie set and not a generic SaaS dashboard.

Boldness is spent in exactly one place: **the divergence view** (in-region voices vs. English-language media) and its companion, **the grade block**. Everything else stays quiet so those two carry the meaning.

### 3.1 Palette (semantic; define as tokens, never raw hex in markup)

| Token | Hex | Use |
|---|---|---|
| `surface` | `#F7F8FA` | App background (cool near-white — deliberately *not* cream) |
| `surface-raised` | `#FFFFFF` | Cards, panels, modals |
| `ink` | `#1A1D24` | Primary text (a real slate, chosen for readability) |
| `ink-muted` | `#5B626E` | Secondary text, metadata |
| `rule` | `#DDE1E6` | Hairlines, borders, dividers (structure carries hierarchy — prefer rules over soft grey shadows) |
| `accent` | `#0E6E77` | Interactive: links, primary buttons, focus ring (petrol — the "instrument panel" color) |
| `accent-weak` | `#E3F0F1` | Accent backgrounds, selected states |

Shadows are used sparingly and only to lift a truly floating surface (modal, dropdown). Cards use **rules and spacing**, not the identical soft-grey drop-shadow that reads as generated.

### 3.2 Grade scale (1–5) — the analytic heart

The **numeral is the primary signal.** Color and label *reinforce* it and are never the only carrier (accessibility + KEEL "never rely on color alone"). The grade block always shows **numeral + word + the corroboration state**, and grade 3 is visibly the **ceiling without corroboration** (TDD §9.2).

| Grade | Word | Token | Hex |
|---|---|---|---|
| 5 | Confirmed | `grade-5` | `#1B7F5B` |
| 4 | Probably true | `grade-4` | `#6BA368` |
| 3 | Unconfirmed | `grade-3` | `#C8912A` (ochre — the ceiling) |
| 2 | Doubtful | `grade-2` | `#C56A2E` |
| 1 | Likely false | `grade-1` | `#B23A34` |

The grade block also surfaces, in one line, *why*: e.g. "3 · Unconfirmed — single credible source, not yet corroborated (ceiling without corroboration)." A grade ≥4 must show its corroborating artefacts on click.

### 3.3 Severity system — kept visually distinct from grade

Signals carry a **severity** and an **event type**, which must never be confused with the truth grade. Severity is shown as a **left border rule + a small labeled icon**, not a color fill:

- `Critical` (coup, assassination, uprising, military event) — heaviest rule
- `High` (arrest of a political/cultural figure, outbreak, incident)
- `Elevated` (sudden disappearance of a news source, anomaly clusters)
- `Info`

`is_imminent` (early signal of imminent action, TDD §4.5) gets its own distinct marker — a small "imminent" pill — separate from severity, because a low-severity *imminent* signal and a high-severity *confirmed* one are different objects.

### 3.4 Typography

Two roles, one deliberate family — **IBM Plex** (open-source; humane but technical; reads "instrument," not "startup"):

- **IBM Plex Sans** — all UI, headings, brief and analysis body. Reading measure capped at ~72 characters. Comfortable line-height for the long analysis body.
- **IBM Plex Mono** — used **narrowly and only for genuine machine identifiers**: content hashes, item/story IDs, ISO timestamps in logs, source URLs. This is data alignment, not decoration — mono is justified here because these are tabular identifiers a person scans and compares, which is exactly where it earns its place.

Type scale: a clear modular scale (e.g. 12 / 14 / 16 / 20 / 26 / 34). Weights: 400 body, 500 UI labels, 600 headings. **Avoid** all-caps eyebrow labels, single-word accenting, and unnecessary label rows above content — set hierarchy with size, weight, and space.

### 3.5 Layout

- **Slim left rail** for primary nav on desktop (instrument feel, space-efficient); collapses to a top bar + drawer under `md`.
- **Single reading column** for the daily brief — a stack of brief items with real hierarchy — **not** a grid of identical cards.
- **Reading measure** (~72ch) enforced on all long-form analysis text.

Dashboard wireframe (desktop):

```
┌────┬───────────────────────────────────────────────┐
│    │  Daily brief — Tue 2 Sep 2026     [◀ date ▶]   │
│ ▦  │  Last pipeline run: 09:12 · 3 sources silent ⚠ │
│ ⌂  ├───────────────────────────────────────────────┤
│ ⚑  │ ▎5 Confirmed   Mobilization near <place>       │
│ ⧉  │    facts → analysis → grade         [4 sources]│
│ ⚙  │ ────────────────────────────────────────────  │
│    │ ▎3 Unconfirmed  Reported arrest of <figure>    │
│ ── │    (ceiling: no corroboration)      [1 source] │
│ ⏻  │ ────────────────────────────────────────────  │
└────┴───────────────────────────────────────────────┘
```

Divergence panel wireframe (the one place boldness is spent — Story detail):

```
┌── In-region voices ──────┐ ╎ ┌── English-language media ─┐
│ summary of what the      │ ╎ │ summary of what EN outlets │
│ region is saying …       │ ╎ │ are reporting …            │
└──────────────────────────┘ ╎ └────────────────────────────┘
        ╎  DIVERGES ON:  point · point · point   ╎
        ╎  CONVERGES ON: point · point           ╎
      (the central seam is the product's reason to exist)
```

### 3.6 Copy voice

Plain, active, sentence case. Buttons say what happens: **"Release to recipients"**, not "Submit"; the toast then says **"Released."** Empty states direct action ("No brief yet today — the morning run posts around 09:00."). Errors state what happened and the next step, in the interface's voice, and never apologize or go vague.

---

## 4. Information architecture & navigation

Routes (React Router; all except `/login` are protected):

| Path | Page | Role |
|---|---|---|
| `/login` | Login | public |
| `/` | Dashboard (today's daily brief) | any |
| `/briefs/:id` | A specific daily brief (by date/id) | any |
| `/stories/:id` | Story detail | any |
| `/alerts` | Alerts / signals list | any (release/suppress: admin) |
| `/alerts/:id` | Signal detail | any |
| `/weekly` | Weekly summaries list + latest | any |
| `/weekly/:id` | A specific weekly | any |
| `/admin/sources` | Sources admin | admin |
| `/admin/recipients` | Recipients (whitelist) admin | admin |
| `/admin/settings` | Thresholds / cadence | admin |

Nav items in the left rail: Dashboard, Alerts, Weekly, Admin (admin only), account/logout. A visible **pipeline-status strip** (last run time; count of silent sources) lives in the header — source liveness is itself a signal (TDD §4.1).

---

## 5. Global patterns (build these once, use everywhere)

1. **Every data view has four states:** loading (skeleton, not a spinner-only), empty (directive copy), error (what happened + retry), loaded. No screen may render only the happy path.
2. **Provenance is mandatory** on any rendered claim, fact, grade, or divergence point. The reusable path: claim → `SourceTrail` → raw item(s) → original text **and** translation side by side, with source name, access level, reliability. If a datum has no artefact, it must not render as a finding — render it as "unverified" with that stated, never as a bare confident number.
3. **Review-and-release is a deliberate action.** Releasing a signal sends email/SMS to real people. The confirmation modal must state, in words, **the blast radius**: "This sends to N active recipients (E email, S SMS). This cannot be recalled." (This mirrors KEEL v9 Principle 1 — before a consequential action, say what it costs, at the moment of the action.) Suppress is reversible and needs only a light confirm.
4. **Auth & roles:** protected routes redirect to `/login` when unauthenticated. Role-gated UI (`admin`) is hidden *and* the underlying action is refused client-side as defense-in-depth — but the server remains the real gate (never trust the client).
5. **Accessibility floor (non-negotiable):** WCAG AA contrast, full keyboard operability, visible focus (accent ring), correct roles/labels, `prefers-reduced-motion` respected. Grade and severity always pair color with text/numeral.
6. **Responsive floor:** usable down to a phone. Alerts and the daily brief in particular must be readable on mobile, because that is where an alert gets read.
7. **Motion:** only in response to a user action (expanding a brief item, opening the confirm modal). No section-load fade-ins.

---

## 6. Component inventory

Primitives: `Button`, `IconButton`, `Card`, `Badge`, `Tag`, `Modal`, `Drawer`, `Tabs`, `Skeleton`, `EmptyState`, `ErrorState`, `Toast`, `FormField` (label, input, error), `Table`.

Domain components:
- `GradeBlock` — numeral + word + corroboration-state line; expands to corroborating artefacts.
- `SeverityMark` — left-rule + icon + label; separate `ImminentPill`.
- `ProvenanceChip` — a single source reference (name · access · reliability); click → `RawItemView`.
- `SourceTrail` — the ordered set of `ProvenanceChip`s behind a claim.
- `RawItemView` — original text + translation side by side, with fetch artefact (source, URL, fetch time, original lang, hash).
- `BriefItemCard` — collapsed headline row (grade, event type, source count) → expands to facts → analysis → grade.
- `DivergencePanel` — the two-stream + seam layout of §3.5.
- `SourceAssessmentTable` — per-source access + reliability + rationale (TDD §9.1).
- `SignalRow` / `SignalDetail` — with `ReviewReleaseControls` (admin).
- `ReleaseConfirmModal` — states blast radius (§5.3).
- `PipelineStatusStrip` — last run, silent-source count.

Every domain component ships with **PropTypes** matching the view-models in §8.

---

## 7. Page specifications

**Login (`/login`).** Username + password, one primary action "Sign in." No public sign-up. States: idle, submitting (button busy, inputs locked), invalid credentials (inline, generic — never reveal which field), rate-limited ("Too many attempts — try again in Xs"). On success, redirect to the route the user was going to, else `/`.

**App shell.** Left rail (§4), header with `PipelineStatusStrip` and account menu (logout). Renders the routed page. Admin nav hidden for `viewer`.

**Dashboard (`/`).** Today's daily brief as a stack of `BriefItemCard`s (TDD §4.6 format: facts → analysis → grade with contrary evidence). Header shows the brief date with prev/next controls (loads past briefs via `/briefs?type=daily`). Each card: `SeverityMark` (if it's a signal), `GradeBlock`, event-type `Tag`, source count; expand reveals facts (each with `SourceTrail`), analysis, grade with contrary evidence, and a link to the full story. Empty state when no brief has posted yet today.

**Story detail (`/stories/:id`).** The full analytic record (TDD §8): title, event type, status; **facts** each with `SourceTrail`; `SourceAssessmentTable`; the `DivergencePanel` (in-region vs English-media summaries + divergence/convergence lists) — the visual centerpiece; `GradeBlock` with contrary evidence; a timeline of related raw items. Every claim reaches its raw item in one hop.

**Alerts (`/alerts`, `/alerts/:id`).** Filterable list (event type, severity, status ∈ new/reviewed/released/suppressed, imminent). Each `SignalRow`: severity, event type, `ImminentPill` if set, grade, created time, status. Detail shows the signal's grade and artefacts and, for `admin`, `ReviewReleaseControls`: **Release to recipients** (opens `ReleaseConfirmModal` stating blast radius) and **Suppress** (light confirm). Status transitions reflect immediately and are read from the server after the call, not assumed.

**Weekly (`/weekly`, `/weekly/:id`).** The Friday "What mattered this week" (TDD §4.6): latest by default, list of past weeklies, long-form read view at reading measure.

**Admin (`/admin/*`, admin only).**
- *Sources*: table (name, language/dialect, type, region, `credibility_prior`, `last_seen_at` with a silence flag, active). Add/edit; seedable from `Languages_and_Religions.md`.
- *Recipients (whitelist)*: table (name, email, phone, channels, active, approved_by). Add/edit/approve. **This is PII** — surface a standing note that recipient data is real user data and its arrival is a **Private-repo tripwire** (TDD §10; KEEL Principle 10). Mask phone/email by default with reveal-on-intent.
- *Settings*: thresholds and cadence (TDD §5), plainly labeled by what they do.

---

## 8. Data contracts (JS mitigation for no-TypeScript)

Because F-1 rules out TypeScript, the analytic shapes are protected two ways, and this is not optional:

1. **JSDoc `@typedef`s** in a `src/types/` module for every entity the UI consumes — `Brief`, `Story`, `Analysis`, `Fact`, `SourceAssessment`, `Divergence`, `Signal`, `RawItem`, `Recipient`, `Source`, `User` — mirroring TDD §6 field-for-field.
2. **PropTypes** on every component, matching those typedefs.

The API client normalizes responses to these view-models at the boundary, so no component reads a raw API shape directly. A fact with no `raw_item_id`(s) is normalized to an explicit `unverified: true` — it must never arrive at `GradeBlock` looking like a corroborated finding.

Endpoints consumed (TDD §7): `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `GET /briefs?type=`, `GET /briefs/{id}`, `GET /stories`, `GET /stories/{id}`, `GET /signals`, `GET /signals/{id}`, `POST /signals/{id}/release`, `POST /signals/{id}/suppress`, `GET|POST|PATCH /admin/sources`, `GET|POST|PATCH /admin/recipients`, `GET|PATCH /admin/settings`.

---

## 9. Testing requirements (KEEL Principle 5 — self-contained)

**No frontend test may touch the network or a live service.** All API interaction in tests goes through **Mock Service Worker (MSW)** (or an injected mock client), driven by canned fixtures. Required coverage:

- Every page renders all four states (loading / empty / error / loaded) from fixtures.
- **Provenance:** a fact with no artefact renders as unverified, never as a graded finding.
- **Grade ceiling:** an uncorroborated story never displays grade > 3.
- **Role gating:** a `viewer` never sees Admin nav and cannot invoke release/suppress.
- **Release blast radius:** the confirm modal displays the correct recipient counts from the fixture before any call is made, and no send occurs until confirm.
- **Auth:** protected route redirects when unauthenticated; login error and rate-limit states render.
- **`testplan.md` (v9) / test plan:** record, for each guard above, *how it was proven able to fail* — break the thing it watches, confirm red (KEEL Principle 6, three-clause proof rule).

PROOF for the suite: **it passes in seconds with the network turned off.**

---

## 10. THE ORDERS — for Claude Code, in sequence

Do these **in order.** Each ends with a **PROOF** you must witness. If a proof does not happen, **stop and fix that order.** After each order, run the Closing Ritual: write a session close-out and record which doctrine documents changed.

### Order 0 — Gate (do not skip; this is Phase 0)
- Confirm Keel Part B is laid and every PROOF witnessed: self-contained tests run offline; the deploy gate blocks a failing build and ships a passing one; branch protection refuses a direct push to `main` (incl. for the owner); hand-deploy is dead (TDD §12, Checklist 11–16).
- Confirm the decision log exists and holds entries for **F-1 (JS ruling + JSDoc/PropTypes mitigation), F-2, F-3, F-4, F-5, F-6, F-7** — or that the Owner has explicitly deferred each. Do not proceed on an OPEN decision that a later order needs.
- **PROOF:** you can point at the witnessed Keel proofs and at each required D-entry (or a written deferral). Only then continue.

### Order 1 — Scaffold
- Create the Vite + React (**JavaScript/JSX**) app inside the repo. Add React Router v6, ESLint, Prettier, Vitest, React Testing Library, MSW, `prop-types`, `lucide-react`. Establish folders: `src/{app,routes,components,domain,api,types,test}`.
- Add one trivial component + its test.
- **PROOF:** `dev` server runs and renders a placeholder; the one test passes **with the network off**.

### Order 2 — Design tokens & primitives
- Implement the §3 token layer (per F-4) — palette, grade scale, severity, type scale — as named tokens, not raw hex. Load IBM Plex Sans + Mono. Build the primitives from §6 (Button, Card, Badge, Tag, Modal, Drawer, Tabs, Skeleton, EmptyState, ErrorState, Toast, FormField, Table).
- Provide a dev-only `/_gallery` route rendering each primitive in each state for eyeball review.
- **PROOF:** the gallery shows every primitive; keyboard focus is visible on all interactive ones; grade/severity render with numeral+label, not color alone. Tests for primitive states pass offline.

### Order 3 — API client, query layer, auth, protected routes
- Build the boundary API client (F-3: `credentials: 'include'`; normalize to §8 view-models). Wire TanStack Query (F-2). Implement auth context, `/login`, `GET /auth/me` bootstrap, logout, and `ProtectedRoute`.
- All backed by MSW fixtures.
- **PROOF:** against mocks — login succeeds and redirects; bad credentials and rate-limit states render; an unauthenticated visit to `/` redirects to `/login`. Tests pass offline.

### Order 4 — App shell, nav, role gating
- Build the shell: left rail (§4), header with `PipelineStatusStrip` + account menu, routed outlet. Hide Admin nav for `viewer` (F-7).
- **PROOF:** `admin` sees Admin nav; `viewer` does not; `PipelineStatusStrip` shows last-run + silent-source count from fixture. Tests pass offline.

### Order 5 — Provenance components
- Build `ProvenanceChip`, `SourceTrail`, `RawItemView` (original + translation side by side, with fetch artefact), and `GradeBlock` (numeral + word + corroboration-state line; expands to artefacts). Normalize artefact-less facts to `unverified`.
- **PROOF:** a fixture fact with no artefact renders as unverified; an uncorroborated story's `GradeBlock` never exceeds 3; a graded claim reaches its raw item (original + translation) in one hop. Tests assert all three, offline.

### Order 6 — Dashboard / daily brief
- Build `BriefItemCard` and the Dashboard: today's brief as a reading-column stack, date prev/next loading past briefs, all four states.
- **PROOF:** today's brief renders from fixture; a card expands headline → facts (with `SourceTrail`) → analysis → grade w/ contrary evidence; empty/loading/error all render. Tests pass offline.

### Order 7 — Story detail
- Build Story detail: facts with `SourceTrail`, `SourceAssessmentTable`, the `DivergencePanel` (the design centerpiece), `GradeBlock` with contrary evidence, related-items timeline.
- **PROOF:** the divergence panel shows both summaries plus divergence and convergence lists; every fact reaches its raw item; grade shows contrary evidence. Tests pass offline.

### Order 8 — Alerts + review-and-release
- Build the Alerts list (filters), `SignalDetail`, and (admin) `ReviewReleaseControls` with `ReleaseConfirmModal` stating blast radius (§5.3). Read status back from the server after the call.
- **PROOF:** a `viewer` cannot see or invoke release/suppress; the confirm modal shows correct recipient counts *before* any call; no send fires until confirm; suppress needs only a light confirm. Tests assert each, offline.

### Order 9 — Weekly
- Build Weekly: latest by default, past list, long-form read at reading measure.
- **PROOF:** latest weekly renders; a past weekly loads by id; empty/error render. Tests pass offline.

### Order 10 — Admin
- Build Sources, Recipients, Settings (admin only). Mask recipient PII with reveal-on-intent; surface the **Private-repo tripwire** note on the Recipients page (TDD §10).
- **PROOF:** admin can list/add/edit each; `last_seen_at` silence flag shows; PII is masked by default; the tripwire note is present; `viewer` is refused. Tests pass offline.

### Order 11 — Accessibility & responsive pass, and close the test plan
- Full keyboard/contrast/reduced-motion pass; verify the phone layout for Dashboard and Alerts. Fill the test plan: what is covered, what is deliberately not and why, and for each guard how it was proven able to fail (KEEL Principle 6).
- **PROOF:** keyboard-only walk of a full flow (login → read brief → open story → release an alert) works; contrast checks pass; the test plan names at least one deliberately-uncovered area with its reason. Suite passes offline in seconds.

---

## 11. Definition of done

- Every Order's PROOF witnessed and, where relevant, recorded in the test plan.
- The full suite passes **with the network off**, in seconds.
- No analytic claim renders anywhere without a reachable artefact; no uncorroborated story shows a grade above 3.
- Release/suppress is admin-only, states its blast radius, and sends nothing until confirmed.
- Each frontend decision (F-1…F-7) has a decision-log entry or a written deferral.
- Recipient PII handling and the Private-repo tripwire are visible in the UI, ready for the flip when real recipient data lands.

*Planner draft. Owner: review §2 (especially the OPEN decisions) and the §3 direction, then issue the execute order — after the Keel is proven.*
