# D-020 — Go-remote tripwire amended: a local-only credential does not trip it

**Date:** 2026-09-27
**Status:** Decided

## Decision

Amend D-011's tripwire. The **Claude API key lives only in `backend/.env` on the Owner's PC** (gitignored; verified 2026-09-27 via `git check-ignore`), and the **repo stays public**. The tripwire now fires on any of:
1. the first remote deploy;
2. the first real recipient contact data beyond the Owner's own;
3. the first collected content leaving the Owner's machine;
4. any credential being committed or pushed.

**Guards:** `.env` gitignored (verified); GitHub's user-level push protection, which by default blocks pushing recognised secrets to public repos (**confirmed live 2026-09-27**: `secret_scanning` and `secret_scanning_push_protection` both `enabled` on this repo via `gh api repos/.../{repo}` → `security_and_analysis`); a backend startup check that refuses to run with the API key set if `backend/.env` is ever tracked by git.

## Context

[D-011](D-011-hosting-platform-and-deploy-mechanism.md) says the first real credential means "build + prove the Fly path, and flip the repo Private". On **GitHub Free, rulesets do not apply to private repositories** (GitHub Docs, "About rulesets": available "in public repositories with GitHub Free… and in public and private repositories with GitHub Pro, GitHub Team, and GitHub Enterprise Cloud"). Flipping private without paying would silently disable the merge gate proven on PR #4, which breaks Keel Principles 6 and 9 and contradicts the free-first posture.

## Options rejected

- **Flip private and buy a paid GitHub plan.** Safest, but not free; revisit when the tripwire genuinely fires.
- **Flip private on the free plan.** Loses the enforced gate.
- **Keep D-011 literal and deploy to Fly now.** Contradicts "localhost first".

## Evidence

- Owner ruling, 2026-09-27; GitHub Docs "About rulesets" and "About push protection"; `git check-ignore -v backend/.env` → `.gitignore:157:.env` (re-verified live, this session: `backend/.env` does not yet exist on disk — the key has not been created — but the ignore rule is in place and will apply the moment it is).
- Live repo state, confirmed 2026-09-27: `gh api repos/johnopladen-hue/Project-Middle-East-Signal-Generator-MESG-` → `visibility: public`, `security_and_analysis.secret_scanning: enabled`, `security_and_analysis.secret_scanning_push_protection: enabled`. O-C.3's "check push protection is on" is therefore already satisfied; no further Owner action needed for this guard.

## Supersedes

**[D-011](D-011-hosting-platform-and-deploy-mechanism.md), in part** (its tripwire clause only; Fly as the eventual host stands).
