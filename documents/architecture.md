# Architecture — Project MESG (Middle East Signal Generator)

> This document is the single source of truth for system architecture. Update it whenever a build order or TDD changes the design. Do not let it drift from what is actually implemented.

## Mission & Problem Statement

**Context:** Coverage of Middle East events is poor because we rely on biased, English-language news media. We lack native-language access and are dependent on agenda-driven outlets, producing a hazy picture of unfolding events.

**Objective:** Separate what people are saying (native-language discourse) from what is being reported in English-language media, and identify where the two converge and diverge. Aggregate, analyze, and distill this into:
- A daily brief
- Alerts on high-signal events
- Potential signals of imminent action

Delivered via web application, SMS text, and email, to start.

**Roles the system (and its analysis) must embody:**
1. **Source-finding expert** — locates discussions, published news, and information exchanges impacting native language-speakers across the Middle East.
2. **Intelligence analyst** — assesses each source's access to the information it claims and the veracity of that information; objective, skeptical, and creative in corroboration (e.g., cross-checking a claimed shipment volume via a packaging supplier rather than trusting the company's own figure).

**Output format (example shape):**
- Bulleted daily summary; for each item: facts → analysis → probability of truth (1–5 scale) against corroborating/contradicting evidence.
- **Bulletins** (email + text) for: military events, natural disasters, incidents, disease outbreaks, assassinations, arrest of a political figure, arrest of a major cultural influencer, sudden disappearance of a news source, uprising, coup.
- **"What Mattered This Week"** summary, delivered Friday afternoon.

## Guiding Principles

- Adheres to **Keel v5** principles (see project grounding — full principles to be pasted/filed).
- Leverages **CORE** (definition pending — full framework to be pasted/filed).

## System Components (to be filled in as designed)

| Component | Purpose | Status |
|---|---|---|
| Source ingestion | Collect native-language discourse + English media | Not started |
| Translation / normalization | Convert native-language sources for analysis | Not started |
| Corroboration / veracity engine | Score source access & reliability, cross-check claims | Not started |
| Divergence/convergence analysis | Compare native discourse vs. English media narrative | Not started |
| Daily brief generator | Produce bulleted, scored daily summary | Not started |
| Alerting engine | Detect bulletin-worthy events, trigger email/SMS | Not started |
| Weekly summary generator | "What Mattered This Week," Fridays | Not started |
| Web application | Deliver briefs/alerts, manage subscribers | Not started |
| Auth / access control | Username + password (v1), whitelisted recipients | Not started |
| Notification delivery | Email + SMS to whitelisted individuals | Not started |

## Data Flow (to be diagrammed as design matures)

_TBD — populate once first TDD defining ingestion/analysis pipeline is received._

## Tech Stack

_TBD — repo currently ships a Python `.gitignore`; confirm stack in first build order/TDD._

## Security Model

- **v1:** Simple username/password authentication.
- Recipient list (email/SMS) is a **whitelist** curated by the project owner.
- Expected to evolve — track upgrades in `decisions.md`.

## Revision Log

| Date | Change | Source Doc |
|---|---|---|
| 2026-08-02 | Initial architecture scaffold created from project kickoff conversation | This session |
