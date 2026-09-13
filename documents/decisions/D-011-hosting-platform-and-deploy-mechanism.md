# D-011 — Hosting platform (Fly.io) and localhost dev-for-now

**Date:** 2026-09-13
**Status:** Decided

## Decision

Resolves the long-open "Hosting platform" item in `documents/decisions.md`:

1. **Production host = Fly.io.** The Fly deploy path (`Dockerfile` + `fly.toml`, `flyctl deploy --remote-only` from GitHub's cloud CI using a deploy-scoped `FLY_API_TOKEN` held by name) is the intended shape, **not built or proven yet**, and its specifics are verified against current Fly docs when built — not from memory.
2. **Localhost = the development environment for now**, because Fly is not yet set up. The app is run locally via one documented command for development and inspection. Localhost is **not** an automated deploy target, and no local deploy agent is built.
3. **The gate is unchanged and remains in force.** Tests-must-pass-to-merge + branch protection were proven on PR #4 (`documents/findings.md`, 2026-09-06) and keep running on GitHub's cloud runners. The CI `deploy` job stays the current placeholder until Fly is stood up.
4. **Automated deploy is a Fly deliverable.** It is built and witnessed on Fly's first real deploy — you cannot prove an automated deploy to a host that does not exist, and no local stand-in is built to simulate one.

**Go-remote tripwire:** first real credential / first real user data / first remote deploy → build + prove the Fly path, and flip the repo **Private** (Keel v9 Principle 10).

## Context

`documents/decisions.md` carried "Hosting platform — drives Keel Part B (CI/CD, secrets, deploy gate)… explicitly deferred by the Owner, 2026-09-06; backend work proceeds against the placeholder deploy step" as an open item. Backend and frontend are now built through Order 11 against that placeholder. The Owner ruled the platform (Fly.io) on 2026-09-13.

An earlier draft of this same decision (same date, before commit) proposed a local pull-restart agent that would poll `main` and auto-deploy to localhost, reasoning that "a deploy is a deploy even if hosting is local." The Planner reviewed that draft against the live repo and corrected it before it was committed: localhost is the dev environment, not a deploy target, and no machinery is built to simulate an automated deploy to a host (Fly) that doesn't exist yet. That correction is folded directly into the Decision above; no separate superseding entry is needed since the local-agent draft was never committed as Decided.

## Options rejected

- **A local pull-restart agent polling `main` and auto-deploying to localhost on every green merge** (the earlier draft of this decision). Rejected — this is throwaway machinery built to simulate a deploy target that isn't real; proving "merge triggers a local restart" is not evidence that `flyctl deploy --remote-only` will work, and building it risks the appearance of a proven automated deploy where none exists (Principle 6 — a deploy path never exercised on the real target is a hope, not a guarantee, and a fake stand-in makes that easier to forget).
- **A self-hosted GitHub Actions runner on the (public) repo to perform a local deploy.** Rejected — on a public repository this permits forked-PR arbitrary code execution on the Owner's machine (a documented GitHub hazard), incompatible with Principle 10's build-in-the-open posture.
- **A webhook from GitHub to a local listener.** Rejected — reaching localhost needs a public tunnel, reintroducing the exact remote exposure a local mechanism would exist to avoid.
- **Choosing a different host now (Render, Railway), or deferring the platform choice further.** Rejected — the Owner ruled Fly.io; leaving the platform unchosen keeps the deploy leg unrealized indefinitely.

## Evidence

- Owner ruling, this session, 2026-09-13: hosting platform is Fly.io.
- `documents/decisions.md` — the open "Hosting platform" item this resolves.
- `documents/findings.md`, 2026-09-06 — the PR #4 gate/branch-protection proof this leaves intact and unchanged.
- `.github/workflows/ci.yml` — the `deploy` job stays the existing placeholder until Fly is stood up; not modified by this decision.
- `documents/assumptions.md` — A-003, registered alongside this decision, names the gap between "CI green + runs locally" and "the Fly deploy path has been exercised."
- Keel v9 Principle 6 (prove it by tripping it — not by simulating it), Principle 10 (build public / go private; the tripwire).

## Supersedes

None. Resolves the open "Hosting platform" item in `documents/decisions.md`. Does not overturn any prior decision; the CI gate and branch protection from the D-007 (Adopt Keel v9) era remain in force unchanged.
