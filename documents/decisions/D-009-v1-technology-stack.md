# D-009 — v1 technology stack

**Date:** 2026-09-06
**Status:** Decided

## Decision

Resolve the TDD's ⟐ DECISION stack items that do not require a new vendor/account choice:

| Layer | Decision |
|---|---|
| Backend/API | Python + FastAPI (as proposed, TDD §13) |
| Database | SQLAlchemy ORM over PostgreSQL in production; SQLite in-memory for the self-contained unit test suite (Keel Principle 5 — no network/live service in tests). The ORM boundary makes this swappable without touching model/business logic. |
| Frontend | React + Vite, **plain JavaScript** (not TypeScript) — per the Owner's explicit direction recorded in the TDD itself ("Owner said 'React.JS'," TDD §8). The Planner's TypeScript recommendation is noted but not adopted; revisit if the analytic data shapes prove hard to maintain without static types. |
| Auth | Username/password, hashed with argon2; **httpOnly session cookies** (not JWT), per the Planner's leaning in TDD §10 and no conflicting Owner instruction. |

Left **open**, deferred until the Owner supplies the vendor/account or a decision session addresses them (TDD §15, items 2, 6–10): hosting platform, translation provider, analysis/LLM provider, email provider, SMS provider, scheduler mechanism. Backend code is written against the `Translator`, `Analyst`, `EmailProvider`, `SmsProvider` interfaces (TDD §4.2/§4.4/§4.7) with fake/mock implementations backing the test suite, so none of these five deferrals block writing or testing the rest of the system — they only block wiring in a real provider and a real deploy.

## Context

TDD §15 requires every ⟐ DECISION be logged before Code executes against it. The Owner asked Code to begin developing the application per the TDD; several stack choices can be resolved immediately from what the TDD and prior sessions already establish, while others name real external services or infrastructure the Owner has not chosen and Code should not pick unilaterally (cost, account ownership, and Keel Principle 4's secrets-handling implications all sit with the Owner).

## Options rejected

- **TypeScript for the frontend**, despite the Planner's recommendation — rejected because the Owner already gave explicit direction ("React.JS") recorded in the TDD; overriding a stated Owner preference with an AI's stylistic recommendation is exactly the kind of unilateral call Keel reserves for the Owner (v9, "The third player is you — rulings on judgement calls").
- **JWT auth** instead of session cookies — rejected in favor of the Planner's own stated leaning ("httpOnly session cookies for simplicity and safer defaults in a small trusted-user app," TDD §10), since no Owner instruction contradicts it.
- **Guessing a hosting platform / LLM / email / SMS provider** to avoid leaving anything open — rejected. These carry real cost and account-creation implications; picking one without the Owner would risk building against infrastructure the Owner doesn't want to pay for or hold credentials in.

## Evidence

- `documents/tdds/MESG-TDD-v0.1.md` §8, §10, §13, §15 — the proposed stack, the flagged JS/TS sub-decision, and the auth leaning.
- Owner instruction, this session, 2026-09-06: "I want you to develop the application according to the tdds found in the tdd file," followed by explicit deferral of the hosting-platform question ("Not decided yet — defer").

## Supersedes

None.
