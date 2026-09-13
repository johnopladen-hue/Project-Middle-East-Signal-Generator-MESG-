# MESG — Session Close-Out: Actor-Network Layer & Actor Register

**Date:** 2026-09-13
**Session type:** Code session — executed `MESG-Actor-Network-Layer-Orders-v0.2.md`
**Roles present:** Owner + Code (Claude Code, local). Planner not in this session.
**Keel version:** v9

---

## 1. Purpose of this session

Build the actor-network layer (Organization/Relationship/Designation/Theatre/Alias) and seed it with a real, licensed, sourced v1 actor register — not "all the world's factions," and never generated from model knowledge.

## 2. What we did

**O-A/O-B/O-C — [D-012](../decisions/D-012-actor-network-layer.md) and [D-013](../decisions/D-013-source-licensing-posture.md) committed; [A-004](../assumptions.md)/[A-005](../assumptions.md) registered.**

**O-1 — Grounding.** Live `origin/main` HEAD confirmed at `805ab40`. Highest decision D-011, highest assumption A-003 — both D-012/D-013 and A-004/A-005 confirmed free before writing them. First-article app confirmed still running.

**O-2/O-3 — Schema + harvester contract + fixtures (Phase 1, self-contained).** `Organization`, `OrganizationAlias`, `Designation`, `Relationship`, `Theatre` added to `backend/app/models.py` — deliberately no `type`/`is_terrorist` column. The `ActorRecord`/`RelationshipRecord`/`HarvestResult` contract (`backend/app/actors/contracts.py`) and `apply_harvest`/`reconcile` (`backend/app/actors/apply.py`) are the only code path allowed to write actor rows. `backend/tests/test_actor_model.py` (6 tests) proves all four O-3 requirements offline.

**O-4 — License gate.** Re-confirmed UCDP's terms live rather than trusting the snapshot — and found the snapshot's plan was wrong: the Actor Dataset is a plain public CSV download, not the token-gated JSON API the orders assumed. Corrected [D-013](../decisions/D-013-source-licensing-posture.md)'s UCDP line accordingly; full account in `findings.md`.

**O-5 — UCDP harvester.** `backend/app/actors/harvesters/ucdp.py`, tested offline (`backend/tests/test_ucdp_harvester.py`, 5 tests) against `tests/fixtures/ucdp_actor_sample.csv` — a genuine excerpt of real UCDP v26.1 rows, not fabricated.

**O-6 — First real UCDP harvest.** 123 real organizations, 65 aliases, 38 relationships harvested into the local dev DB from the actual downloaded dataset (`backend/data/ucdp/Actor_v26_1.csv`, gitignored). Zero orphan relationships; the 123-count reproduced independently twice. Full account, including two independently-verified real relationship facts (PFLP-GC split from PFLP), in `findings.md`.

**O-7 — Designation harvest.** State Department's own FTO page returned HTTP 403 (bot-blocked) to both `WebFetch` and `curl`; proceeded with OFAC's SDN list instead (also carries an `FTO` tag per entry) rather than scrape past that block. Harvested the real, full SDN list (19,388 rows → 1,356 org-level terrorism-program rows) and identity-matched against the 123 real UCDP organizations. **Found and corrected a real problem along the way:** an initial 0.6 similarity threshold produced false-positive matches at scale (e.g. an oil company matched to a militant faction); raised to 0.85, leaving only 8 matches, every one spot-checked and genuinely correct (Hamas, PFLP, PFLP-GC, Al-Aqsa Martyrs Brigade, PJAK, Jaish al-Adl, Jaish al-Muhajireen wal-Ansar, Liwa al-Aqsa/Jund al-Aqsa). 1,348 designations correctly sit `unmatched_pending_match`, not dropped. Full account in `findings.md`.

**O-8 — First actor view.** `GET /organizations` + `GET /organizations/{id}` (`backend/app/routers/organizations.py`, 3 tests) and a matching frontend (`Organizations.jsx` directory, `OrganizationDetail.jsx` profile — aliases, designations as parallel cards each with body/label/confidence/citation link, followable relationship edges, source citation). Verified against the real running app: Hamas's real alias, real OFAC FTO/SDGT designation at confidence 1.0, and PFLP-GC's real split-from edge to PFLP all render correctly through the live API.

**O-9 — Records.** `test_plan.md` gets four new rows (T-019–T-022) and three new honest deferrals (no frontend component tests yet for the actor view; only OFAC harvested, not UN/EU/UK; the MMP timeline/map and scope-widening remain future work). `findings.md` has four new dated entries covering O-4, O-6, and O-7's threshold correction.

**O-10 — This close-out.**

## 3. Which of the five documents changed today

All five: `architecture.md` (Actor-Network Layer section + revision log), `decisions.md` + `decisions/D-012-*.md`/`D-013-*.md` (two new decisions), `assumptions.md` (A-004, A-005), `findings.md` (four new entries), `test_plan.md` (four new rows, three new deferrals).

## 4. Verified live state (this session's grounding)

- **Live `origin/main` HEAD before this session's commits:** `805ab408ab3f2e81405a70f138e29f83320a1abe`.
- **Highest decision after this session:** D-013. **Highest assumption:** A-005.
- **Actor register row counts (real, in the local dev DB):** 123 organizations, 65 aliases, 38 relationships (24 correctly unresolved - outside v1 scope), 1,356 designation candidates (8 matched, 1,348 unmatched-pending-match).
- **61/61 backend pytest pass**, self-contained, no network in the gate (the real CSVs are gitignored local data, not fetched during tests).
- **Frontend lint clean; 61/61 frontend Vitest tests pass** (pre-existing suite; no new frontend tests added this session — see `test_plan.md` deferral).
- **What the Owner can open in a browser:** http://localhost:5173/organizations (log in `analyst` / `correct-password`) — click into Hamas, PFLP, or PFLP-GC to see real designations, citation, and a followable relationship edge.

## 5. Open items → carried to next session

1. **Merge outstanding PRs** — this session's branch, plus PR #21 (richer seed data) and PR #19/#20 status should be double-checked; the auto-mode classifier categorically blocks `gh pr merge` from this session.
2. **Add frontend component tests** for `Organizations.jsx`/`OrganizationDetail.jsx` before building further on this UI (test_plan.md deferral).
3. **UN/EU/UK designation lists** and the State Department's own FTO page (bot-blocked here; may need a different access path) remain unharvested.
4. **Severity vocabulary mismatch** (`findings.md`, first-article session) — still not fixed.
5. **Next planned work per the orders:** the MMP full interactive timeline/relationship-map — explicitly not this order's scope.

---

*This close-out is the baton. Commit it to the repo. Next session starts by reading it.*
