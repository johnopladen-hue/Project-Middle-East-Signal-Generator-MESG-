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
