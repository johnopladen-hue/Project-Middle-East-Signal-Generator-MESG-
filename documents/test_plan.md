# Test Plan — Project MESG

> All tests for the project, tracked in tabular format. Update as build orders/TDDs introduce new components requiring test coverage.

| Test ID | Component/Feature | Test Type | Description | Expected Result | Status | Date | Notes |
|---|---|---|---|---|---|---|---|
| T-001 | Keel gate (`keel_proof.py`) | Unit + gate proof | Self-contained pytest run in CI (`.github/workflows/ci.yml`), required as a status check on `main`. Not MESG feature code — proves the merge-on-green mechanism per Keel Principle 6. | A failing `keel_proof` test blocks PR merge (even for the repo owner); a passing one merges and the `deploy` job runs. | Passing | 2026-09-06 | Witnessed live on PR #4 (5-move proof); see `documents/findings.md` 2026-09-06 entry for the full result. |

**Status legend:** Not Started · In Progress · Passing · Failing · Blocked

**Test Type examples:** Unit · Integration · End-to-End · Manual · Security · Performance
