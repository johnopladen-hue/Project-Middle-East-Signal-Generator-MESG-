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
- **If false:** CI passing stops being sufficient proof of deployability; add a platform-matching CI job (e.g. a container matching the real target) once the hosting decision (now [D-011](decisions/D-011-hosting-platform-and-deploy-mechanism.md)) is exercised against a real Fly deploy.

- **ID:** A-002
- **Date:** 2026-09-06
- **Assumption:** A keyword-based event-type classifier (`backend/app/signals.py`) is an acceptable placeholder for the Analyst-driven classification the TDD (§4.5) actually specifies, until the analysis/LLM provider decision is made.
- **Falsifying test:** Real story text from the v1 source scope (Levantine Arabic / Persian, translated) produces classifier false positives/negatives that would materially change a signal's severity or whether it enters the review queue.
- **If false:** Do not let the keyword classifier drive real alerting; gate it behind human review until it is replaced by the real Analyst-driven classification (same contract, per the module's own docstring).

- **ID:** A-003
- **Date:** 2026-09-13
- **Assumption:** The localhost dev run and the passing CI gate together are sufficient assurance the app deploys and runs correctly — even though the automated deploy path to Fly ([D-011](decisions/D-011-hosting-platform-and-deploy-mechanism.md)) has never been exercised.
- **Falsifying test:** Fly's first real deploy fails, or the app behaves differently on Fly than on localhost, despite green CI.
- **If false:** CI-green + local-run is not proof of deployability; the Fly deploy path must be built and witnessed (Principle 6) before anything is relied upon in production. Adjacent to A-001 (CI runner ≈ deploy target).

- **ID:** A-004
- **Date:** 2026-09-13
- **Assumption:** UCDP's organized-violence scope ≈ our v1 actor universe ([D-012](decisions/D-012-actor-network-layer.md)/[D-013](decisions/D-013-source-licensing-posture.md)).
- **Falsifying test:** A v1 actor of interest (e.g. a purely political or non-violent religious faction) has no UCDP entry.
- **If false:** The register has a systematic blind spot for non-combatant actors; a second source is needed. Known gap already: UCDP excludes actors never involved in organized violence.

- **ID:** A-005
- **Date:** 2026-09-13
- **Assumption:** A designation list's silence about a group means the group is *not* so designated ([D-013](decisions/D-013-source-licensing-posture.md)).
- **Falsifying test:** A group absent from the FTO list is nonetheless designated elsewhere/later.
- **If false:** Absence must be stored as "not found on list Y as of date Z," never as "not a terrorist." (The schema already stores unmatched designations as their own category, `Designation.match_status = unmatched_pending_match`, rather than as silent absence — see `architecture.md`'s Actor-Network Layer section.)

- **ID:** A-006
- **Date:** 2026-09-13
- **Assumption:** AOR membership is current as of the harvested UCP revision ([D-015](decisions/D-015-region-taxonomy-ucp-aors.md), sourced from CRS IF11428 v3, dated 2022-03-30).
- **Falsifying test:** A country is reassigned to a different command after our harvest date (as Israel was, EUCOM → CENTCOM, 2021-01-15 — the exact kind of change this guards against, already inside the harvested document's own history).
- **If false:** The map mislabels a country's command and an AOR polygon is wrong. **Guard:** UCP revision/source + date stored per mapping; render "as of ‹revision›"; re-harvest on a new UCP. This assumption is already known to be *stale by construction* — the source itself is dated 2022, not 2026, because the primary `centcom.mil` source blocks automated access (`findings.md`).

- **ID:** A-007
- **Date:** 2026-09-13
- **Assumption:** The map's located subset fairly represents the signal picture.
- **Falsifying test:** The located-to-unlocated ratio shows that most signals — or most of a high-value signal type — are unlocatable, making the map a biased view.
- **If false:** The map silently under-represents what it can't pin. **Guard:** always surface the unlocated count and tray, and report the ratio; unlocated items never vanish.
