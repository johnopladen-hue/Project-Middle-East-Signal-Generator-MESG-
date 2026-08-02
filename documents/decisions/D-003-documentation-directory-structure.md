# D-003 — Documentation directory structure

**Date:** 2026-08-02
**Status:** Decided (structure evolved further by [D-001](./D-001-decision-log-structure.md))

## Decision

Create `documents/` at the repo root as the single location for build orders, TDDs, close-out/pre-work docs, and standing project documentation, starting with four root documents: `architecture.md`, `decisions.md`, `findings.md`, `test_plan.md`.

## Context

The Owner's day-one kickoff directed creation of a documents directory to hold all build orders, TDDs, and any other document the Owner provides, plus four specific root-level documents for architecture, decisions, findings, and testing — to be read and re-grounded on at the start of every session.

## Options rejected

- **No dedicated folder** — scatter notes across the README or ad hoc files. Rejected as inconsistent with the Owner's explicit directive and with Keel Principle 1 (one canonical copy) once Keel v5 was later filed.
- **Name the folder `docs/`**, matching Keel v5's literal text. Not actually available as an option at the time — Keel v5 had not yet been provided to Builder when this decision was made. The naming tension this created once Keel v5 arrived is resolved separately in [D-001](./D-001-decision-log-structure.md), which keeps `documents/` rather than retrofitting a rename.

## Evidence

- Owner's initial kickoff message, 2026-08-02: "Create a documents directory in the repository... Create 4 root level documents, architecture.md... decisions.md... findings.md... and test plan.md."

## Supersedes

None. (Refined, not overturned, by D-001, which changes how `decisions.md` is structured but not the existence of `documents/` itself.)
