# Assumptions — Project MESG

> Per Keel v9 Principle 7 ("the five documents"), this file holds what the project relies on without having explicitly decided to. Two bars for an entry: state the falsifying test, or it does not go in.

## Format

For each entry:

- **ID:** A-NNN
- **Date:**
- **Assumption:** What we are relying on.
- **Falsifying test:** What observation would prove this wrong.
- **If false:** What breaks / what would need to change.

---

- **ID:** A-001
- **Date:** 2026-09-06
- **Assumption:** GitHub Actions' `ubuntu-latest` runner environment (Python/Node versions, available system packages) stays close enough to what a real deploy target will look like that CI passing is a meaningful signal, even though the actual hosting platform (`documents/decisions.md` open item) is not yet chosen.
- **Falsifying test:** The eventual hosting platform requires a runtime, package, or OS-level dependency that `ubuntu-latest` doesn't have or resolves differently (e.g. a native extension, a specific libc), and CI-green code fails to run there.
- **If false:** CI passing stops being sufficient proof of deployability; add a platform-matching CI job (e.g. a container matching the real target) once the hosting decision (D-0XX, pending) is made.

- **ID:** A-002
- **Date:** 2026-09-06
- **Assumption:** A keyword-based event-type classifier (`backend/app/signals.py`) is an acceptable placeholder for the Analyst-driven classification the TDD (§4.5) actually specifies, until the analysis/LLM provider decision is made.
- **Falsifying test:** Real story text from the v1 source scope (Levantine Arabic / Persian, translated) produces classifier false positives/negatives that would materially change a signal's severity or whether it enters the review queue.
- **If false:** Do not let the keyword classifier drive real alerting; gate it behind human review until it is replaced by the real Analyst-driven classification (same contract, per the module's own docstring).
