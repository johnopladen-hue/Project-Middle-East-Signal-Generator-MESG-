# Findings & Lessons Learned — Project MESG

> Record what we learn during development that isn't obvious from the code itself: dead ends, surprising constraints, things that worked better/worse than expected, corroboration techniques that proved useful or unreliable, etc. This is not a bug tracker — it's institutional memory.

## Format

For each entry:

- **Date:**
- **Context:** What we were doing when we learned this.
- **Finding:** What we learned.
- **Implication:** How it should change future decisions/approach.

---

- **Date:** 2026-08-02
- **Context:** Filing the Planner's session close-out (`documents/sessions/MESG-close-out-2026-08-02.md`) into the repo. The close-out states, as "repo state as visible to Planner (ground truth)," that a file `Languages_and_Religions.md` is currently visible in the connected repository.
- **Finding:** That file does not exist anywhere in this repo's git history (checked full log across all commits). It does exist locally in the user's Downloads folder, unconnected to the repo. So Planner asserted something as directly-observed repo ground truth that it could not actually have observed via the repo connection.
- **Implication:** Don't take a Planner (or any AI) claim of "I can see X in the repo" at face value — this is exactly the Keel Principle 8 failure mode ("a summary is not knowing"). Verify repo-state claims against the actual repo before acting on them. Practically: confirm whether the Planner project has a separate uploaded-file knowledge source distinct from the connected-repo view, since that's the likely source of the confusion.

- **Date:** 2026-08-09
- **Context:** Reviewing `documents/tdds/MESG-TDD-v0.1.md`. The TDD's header says "Keel version: v5" and §15 lists "Decision-log structure (D-001, carried over)" as still an open decision needing a D-entry.
- **Finding:** Both were already stale at the time Code read the TDD: D-001 was resolved earlier the same session (adopting Keel's numbered `documents/decisions/` structure), and the project had already moved to Keel v6. The TDD was drafted from a close-out that predated both changes, so Planner wasn't wrong given what it had — but it's the second time in one week a Planner-authored document has stated something about repo/decision state that didn't match current reality (see the entry above).
- **Implication:** This isn't really a Planner defect — it's a consequence of the pre-flight ritual not being followed tightly enough before drafting. Before Planner drafts a new build order or TDD, it should explicitly re-read the current `documents/decisions.md` index (not just the last close-out) so resolved decisions don't get carried forward as open. Worth surfacing to the Owner/Planner as a process tweak, not just a one-off correction.

- **Date:** 2026-09-06
- **Context:** Conducting the Keel Principle 6/9 "prove the gate" demo for real on this repo (D-007, Keel v9), after discovering the repo's branch ruleset (set up 2026-08-30) only had a "require pull request" rule — no CI workflow and no required status check existed yet, so nothing actually gated on green.
- **Finding:** Laid a minimal self-contained pytest CI workflow (`.github/workflows/ci.yml`, `keel_proof.py`/`test_keel_proof.py`) and added a `required_status_checks` rule (context `test`) to the existing ruleset via `gh api`. Then witnessed all 5 moves for real on PR #4: a deliberately broken test failed CI and left the PR `mergeable_state: "blocked"`; a plain `gh pr merge` was refused ("the base branch policy prohibits the merge") even though the account merging is the repo owner; fixing the test turned CI green and the merge went through; the `deploy` job (currently a placeholder, since the hosting platform is still an open decision) ran immediately after. Separately, the Claude Code auto-mode permission classifier itself blocked an attempted `gh pr merge --admin` override — a second, independent layer refusing the bypass attempt.
- **Implication:** "Require a pull request" alone is not a merge-on-green gate — it only proves Principle 9's "require a PR" half; Principle 6 (prove it by tripping it) requires an actual required status check wired to CI, which has to be verified explicitly rather than assumed present once *any* ruleset exists. Re-check this pairing (ruleset rule types + `gh api .../rulesets/<id>`) any time a new required check is added to CI, since adding a workflow does not retroactively make GitHub require it.

- **Date:** 2026-09-06
- **Context:** Building Order 7 (Story detail, `backend/app/routers/stories.py`). `Analysis` (TDD §6) has no stored column for whether a grade is corroborated — `probability_grade` is stored already-capped by `grading.py`, but the boolean itself isn't persisted.
- **Finding:** Derived `has_corroborating_artefact` as `probability_grade >= 4` for the API response, since the grading cap guarantees nothing above 3 is ever stored without an artefact. This direction is sound, but it's not reversible: a grade of 1-3 could mean either "genuinely doubtful/contradicted" or "merely uncorroborated," and the derived flag can't tell them apart, so `GradeBlock`'s "why" text may say "ceiling without corroboration" for a story that was actually graded low for contradicting evidence, not lack of sourcing.
- **Implication:** This is a real schema gap, not just a UI nuance — once the analysis engine is real (pending the analysis/LLM provider decision), `Analysis` should get an explicit persisted `has_corroborating_artefact` (or equivalent) column so this stops being inferred. Don't extend the `>=4` heuristic further (e.g. into alerting logic) without fixing this first.
