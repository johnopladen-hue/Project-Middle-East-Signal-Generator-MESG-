# D-019 — Scheduler & runtime: in-app scheduler, localhost first

**Date:** 2026-09-27
**Status:** Decided (build deferred to the next order)

## Decision

Pipeline jobs run through an **in-process scheduler (APScheduler) inside the FastAPI backend** on the Owner's PC. On start/wake it **catches up missed runs** and does not skip them silently. A manual `python -m app.ingest --once` command exists for development and for the bake-off. Remote hosting (Fly, [D-011](D-011-hosting-platform-and-deploy-mechanism.md)) waits for the go-remote tripwire ([D-020](D-020-go-remote-tripwire-amendment.md)).

## Context

Owner ruling: "localhost first, then scale." The pipeline therefore only runs while the PC is on, and a brief built after sleep reflects only what was collected. The UI must show that (a "collection gap" note in the pipeline status strip), not hide it.

## Options rejected

- **Windows Task Scheduler.** Works, but lives outside the repo and the gate, and needs different handling on the eventual Fly host.
- **A task queue (Celery/RQ + Redis).** Heavy for one user on one machine.
- **Deploy to Fly now.** Contradicts the Owner's "localhost first".

## Evidence

- Owner ruling, 2026-09-27; TDD §5 ("start with the simplest the platform supports").

## Supersedes

None. Resolves the open "Scheduler mechanism" item. **Built in the next order**, not this one; recorded now so this order's collectors are written to be schedulable.
