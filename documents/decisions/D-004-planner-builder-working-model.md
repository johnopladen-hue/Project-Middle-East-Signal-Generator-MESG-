# D-004 — Planner/Builder working model

**Date:** 2026-08-02
**Status:** Decided

## Decision

Build orders and TDDs are authored collaboratively in a Claude.ai project called "Planner." The Owner downloads them to the local Downloads folder; Builder (Claude Code) files them into `documents/`, reads and analyzes them, and returns feedback — it does not implement on receipt. The Owner relays feedback to Planner, iterates as needed, and only an explicit Owner execute order triggers Builder implementation.

## Context

The Owner's day-one kickoff established this division of labor before any feature work began, so that design/planning and execution stay separated and reviewable.

## Options rejected

- **Builder plans and codes directly from Owner instructions, without a separate Planner review stage.** Rejected by the Owner's explicit direction. Also inconsistent with Keel v5's two-AI model — once Keel v5 was filed (see `documents/keel-v5/KEEL-2-The-Day-One-Checklist-V5.md`, "First, understand this — or nothing else makes sense") — which independently prescribes the same split: a sealed-room Planner for thinking, a Builder that works as the Owner for doing, and warns that "neither can do the other's job."

## Evidence

- Owner's initial kickoff message, 2026-08-02, describing the Planner/Builder handoff.
- `documents/keel-v5/KEEL-2-The-Day-One-Checklist-V5.md`, section "First, understand this — or nothing else makes sense," corroborating the same model independently.

## Supersedes

None.
