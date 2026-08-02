# D-002 — Repository initialization

**Date:** 2026-08-02
**Status:** Decided

## Decision

Initialize Project MESG by cloning the existing GitHub remote `johnopladen-hue/Project-Middle-East-Signal-Generator-MESG-` into `C:\projects\Project MESG`, rather than running `git init` fresh in that folder.

## Context

At kickoff, the Owner described `C:\projects\projectMESG` as "the local repository." The actual folder at `C:\projects\Project MESG` (note the space) existed but was completely empty — no `.git`, no files. This didn't match "existing local repository" and needed to be resolved before any documents could be filed.

## Options rejected

- **`git init` fresh in the empty folder.** Rejected because a GitHub remote already existed for the project (with a README and a Python-oriented `.gitignore` already committed). Initializing fresh would have orphaned that remote or required manually re-linking it.
- **Assume a different/wrong local path and keep searching.** Rejected once the Owner confirmed the empty folder was correct and supplied the remote URL directly.

## Evidence

- `Test-Path` / `Get-ChildItem` output showing the target directory existed but was empty (session transcript, 2026-08-02).
- Owner-supplied remote: `https://github.com/johnopladen-hue/Project-Middle-East-Signal-Generator-MESG-`.
- `git clone` output and subsequent `git log`/`git status` confirming `README.md` and `.gitignore` present post-clone, on `main`, tracking `origin/main`.

## Supersedes

None.
