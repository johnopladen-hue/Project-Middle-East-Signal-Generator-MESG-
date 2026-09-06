# Test Plan — Project MESG

> All tests for the project, tracked in tabular format. Update as build orders/TDDs introduce new components requiring test coverage.

| Test ID | Component/Feature | Test Type | Description | Expected Result | Status | Date | Notes |
|---|---|---|---|---|---|---|---|
| T-001 | Keel gate (`keel_proof.py`) | Unit + gate proof | Self-contained pytest run in CI (`.github/workflows/ci.yml`), required as a status check on `main`. Not MESG feature code — proves the merge-on-green mechanism per Keel Principle 6. | A failing `keel_proof` test blocks PR merge (even for the repo owner); a passing one merges and the `deploy` job runs. | Passing | 2026-09-06 | Witnessed live on PR #4 (5-move proof); see `documents/findings.md` 2026-09-06 entry for the full result. Superseded as the required check by T-002/T-003 once the frontend suite existed (CI job renamed `test-backend`/`test-frontend`). |
| T-002 | Backend suite (`backend/tests/`) | Unit | Grading engine (corroboration cap, TDD §9.2), signal taxonomy, argon2 auth, whitelist-enforcing delivery, health endpoint — all self-contained (Keel Principle 5), no network. | All pass offline; corroboration-cap test proves the guard by tripping it (5 sources + DIRECT access still capped at 3 without an artefact). | Passing | 2026-09-06 | 20 tests, CI job `test-backend`. |
| T-003 | Frontend primitives (`frontend/src/components/primitives/*.test.jsx`) | Unit | Order 2 UI primitives: Badge (grade tone always carries text), Modal (dialog semantics + Escape-to-close), Tabs (arrow-key navigation + panel visibility), FormField (error linked via aria-describedby). All via Vitest + RTL, jsdom, no network (Keel Principle 5, UI-spec §9). | All pass offline in seconds. | Passing | 2026-09-06 | 8 tests, CI job `test-frontend`. Coverage of the remaining §9 requirements (provenance rendering, grade ceiling, role gating, release blast-radius, auth redirects) lands as each order builds the component it applies to. |

**Status legend:** Not Started · In Progress · Passing · Failing · Blocked

**Test Type examples:** Unit · Integration · End-to-End · Manual · Security · Performance
