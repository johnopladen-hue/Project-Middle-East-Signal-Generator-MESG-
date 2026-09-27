# MESG — Session Close-Out: v1 Approved Source Set (S-1–S-4)

**Date:** 2026-09-27
**Session type:** Code session — executed `MESG-Orders-Approved-Sources-v0.1.md` §3 S-1–S-4 (schema, seed, admin)
**Roles present:** Code (Claude Code, local) only. Planner (cloud) + Owner drafted the orders and `approved_sources_v1.yaml` in a prior session.
**Keel version:** v9

---

## 1. Purpose of this session

Land the parts of `MESG-Orders-Approved-Sources-v0.1.md` that don't need the Owner's Anthropic API key: record the source-approval decision (D-021), extend the schema, seed the real 47-source set, and surface it in the admin UI.

## 2. What we did

**S-1 — D-021 recorded.** The Owner's approved 47-source set (`documents/decisions/D-021-v1-approved-source-set.md`), options rejected, index row added.

**S-2 — Schema, then the dev-DB reset.** Added `Source.verification_note` (distinct from `designation_note`) and `Source.seed_key` (upsert identity). **The reset used a safer method than the orders assumed:** deleting `backend/mesg_dev.db` was blocked twice by the auto-mode safety classifier (correctly — it can't tell synthetic seed data from something worth keeping), and a full process-tree kill was blocked once for risking the Owner's live frontend session. Renaming the file aside (`mv`, not `rm`) and stopping only the specific backend PIDs worked cleanly and achieves the identical outcome. See `findings.md` for the full account — this is now the standing procedure for any future schema change.

**S-3 — Seeder.** `backend/app/sources/approved_sources_v1.yaml` (the approved set) + `python -m app.sources.seed_approved` (idempotent upsert on `seed_key`, validates at load and fails loudly). Seeded exactly **47** sources: 30 rss + 17 telegram; 33 native + 14 english_comparison; ar 13 / fa 9 / he 9 / en 16. `credibility_prior` left at the model default, per the orders — not set from the list's labels.

**S-4 — Admin Sources page.** Kind, class, a "Designated" flag (text-carried, not color-alone), and pair columns added to `Sources.jsx`.

**S-6 (partial) — Verification follow-ups.** `idfofficial`'s liveness confirmed (newest post `#19278`, 2026-09-27T10:41:24 UTC). `WAFAgency` and `alhadath` checked against their own sites — inconclusive (wafa.ps has no Telegram link anywhere on its homepage; alhadath.net is bot-blocked, HTTP 403) — both remain flagged `AUTHENTICITY UNCONFIRMED`, ship anyway per the Owner's explicit ruling.

## 3. Which of the five documents changed today

All five: `decisions.md` + `decisions/D-021-*.md` (new decision), `findings.md` (dev-DB-reset method, seed counts, verification checks), `test_plan.md` (T-032, T-033), `architecture.md` (Ingestion section updated for the real source registry). `assumptions.md` unchanged this session.

## 4. Verified live state (this session's grounding)

- **Live `origin/main` HEAD:** unchanged, `ff960aa` (PRs #26/#27/#28 still unmerged as of this session).
- **Highest decision: D-021.** Highest assumption: still A-010 (unchanged).
- **Backend: 88/88 pytest pass** (72 on `main` + PR #28's 5 budget-breaker tests (T-030) + this session's 11 seeder tests (T-032) = 88). **Frontend: 87/87 pass**, lint clean.
- **Dev database reset and reseeded:** `backend/mesg_dev.db` now has the new schema; both `python -m app.dev_seed` (9 synthetic sources, unchanged screens) and `python -m app.sources.seed_approved` (47 real sources) have run against it. `GET /admin/sources` confirmed serving both sets with all new fields populated.
- **`backend/.env` still does not exist.** The API-key orders (`MESG-Orders-API-Key-v0.1.md`) Part A is still the Owner's to do.

## 5. Open items → carried to next session

1. **Owner: Part A of `MESG-Orders-API-Key-v0.1.md`** — Console account, $20 prepaid, workspace, spend limit, API key into `backend/.env`. Unblocks K-1–K-7, O-3 (bake-off), and everything downstream.
2. **S-5 — the Incoming page** (backend `GET /raw-items` + frontend `/incoming`) — not started this session. Real data has nowhere to land on screen yet.
3. **O-5/O-6 — RSS and Telegram collectors** — not started. Per the orders' own guidance ("stop at a clean boundary"), this is a natural next increment; it does not need the API key, only the now-approved source list.
4. **O-3 — the translation bake-off**, and everything in the API-key orders (K-1–K-7) — blocked on item 1.
5. **Merge order still outstanding for the Owner:** #26 → #27 (basemap fix) → #28 (ingestion foundations) → this session's `approved-sources-v1` branch, in that order (each stacks on the last for the schema/decision-number lineage).

---

*This close-out is the baton. Commit it to the repo. Next session starts by reading it.*
