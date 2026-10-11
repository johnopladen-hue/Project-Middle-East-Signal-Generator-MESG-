# MESG — Session Close-Out: End-of-Day Wrap (2026-09-27)

**Date:** 2026-09-27 (session ran into the small hours of 2026-09-28)
**Session type:** Code session — executed five build-orders drops from Downloads in sequence, each reviewed and merged by the Owner
**Roles present:** Owner + Code (Claude Code, local). Planner (cloud) drafted the orders in prior sessions.
**Keel version:** v9

---

## 1. Purpose of this session

Land the frontend component tests, fix a real map bug the Owner found, stand up the ingestion pipeline's foundations (budget breaker, source schema, decisions), get the v1 source list Owner-approved and seeded, and get real news items flowing and visible — all before the Owner sets up the paid Claude API key.

## 2. What we did

**PR #26 — Frontend component tests.** Landed `frontend-component-tests` (Organizations/OrganizationDetail/MapView, T-026–T-029), stacked on PR #24. 83/83 frontend, 72/72 backend at merge.

**PR #27 — Fixed a real map bug.** The Owner's browser check found the basemap cutting off around Iraq. Root cause: the self-hosted PMTiles extract was scoped to a "Levant" bbox (34–42°E, 29–37°N), never widened to match D-015's actual 22-country CENTCOM AOR (24.7–87.3°E, 12.3–55.4°N) — ~98% of the AOR had no basemap tiles at all. Re-extracted the full AOR at a trimmed zoom (0–5) to control size (3.2 MB, was 2.9 MB for the old Levant-only slice); verified all 22 countries' capitals have labels and borders before shipping. Renamed `levant.pmtiles` → `centcom.pmtiles`.

**PR #28 — Ingestion foundations.** Recorded five Owner decisions already settled with the Planner: **D-016** (translation/analysis providers, NLLB triage + Claude deep pass, $20/month cap), **D-017** (v1 scope + Israeli Hebrew), **D-018** (collection posture: RSS + public Telegram, WhatsApp excluded), **D-019** (in-app scheduler), **D-020** (go-remote tripwire amendment). Registered **A-008–A-010**. Built the LLM budget circuit breaker (`app/llm_budget.py`, fails closed on an unreadable ledger) and extended `Source` with ingestion metadata columns.

**PR #29 — v1 approved source set.** Recorded **D-021**: the Owner's 47-source approved list (16 native RSS, 14 English comparison, 17 Telegram), designated/sanctioned sources included and flagged (Al-Manar, Fars, Palestinian Information Center, Press TV), two authenticity-unconfirmed handles shipped anyway per Owner ruling. Built the idempotent, fail-loud seeder and updated the admin Sources page.

**PR #30 — Real RSS ingestion + the Incoming page.** The Owner's ruling: get real items flowing before setting up the paid API key. Built the real RSS collector (`app/ingestion/rss_collector.py`), re-verified all 30 approved RSS feeds live from this machine (26 OK, 4 blocked at the CDN/WAF level — same pattern as `state.gov`/`centcom.mil` elsewhere in this project), and shipped `/incoming` — real news items, right-to-left for Arabic/Persian/Hebrew, designation/pair/authenticity badges, an honesty line. First real run: **712 items**, Claude spend **$0.00** (confirmed).

**Two real operational snags, both handled without data loss:**
- The dev database needed resetting three times today for schema changes (`create_all` doesn't alter existing tables). Deleting it was blocked twice by the auto-mode safety classifier; a process-tree kill was blocked once for risking the Owner's live frontend session. Solved by **renaming the file aside instead of deleting it**, and stopping only the specific backend PIDs — now the standing procedure (`findings.md`).
- One backend restart accidentally killed the Owner's live frontend dev server too (they'd been started together via `scripts/dev.py`). Restarted standalone from then on, decoupled from the backend's lifecycle.

## 3. Which of the five documents changed today

All five, repeatedly: **6 new decisions** (D-016–D-021), **3 new assumptions** (A-008–A-010), `findings.md` (≈10 new entries — the basemap bug, the dev-DB-reset procedure, per-source RSS re-verification, the HTML-stripping catch, authenticity-check results), `test_plan.md` (T-030 through T-036, plus the oldest ingestion deferral marked unblocked), `architecture.md` (Map Interface and Ingestion sections rewritten to match reality).

## 4. Verified live state (end of session)

- **Live `origin/main` HEAD:** `2ff170f79367a16e20da2064d073219ce766b7a3` (PRs #24–#30 all merged).
- **Highest decision: D-021. Highest assumption: A-010.**
- **Backend: 100/100 pytest pass. Frontend: 92/92 pass, lint clean.**
- **Real data live:** 47 real approved sources seeded; 712 real RSS items collected from 26 of them, visible at `/incoming`; Claude spend $0.00 (nothing calls it yet).
- **`backend/.env` still does not exist** — none of today's work needed it.
- **Both dev servers running and healthy** as of session end (`http://localhost:5173/`, backend on :8000).

## 5. Open items → carried to next session

1. **I-3 — Telegram collector** (17 channels: cache-busted paging, `<time datetime>` for post time, event-driven Home Front Command channel where silence is normal).
2. **I-4 — NLLB-200 triage translator**, wired provisionally ahead of the Claude-dependent bake-off (`MESG-Orders-Ingest-Now-v0.1.md` §2). Needs a real model download (CC-BY-NC 4.0, gitignored) and new heavy dependencies (`ctranslate2` + a tokenizer) — flag size/time to the Owner before pulling.
3. **I-7 — Scheduled continuous ingestion** (APScheduler: RSS/30min, Telegram/15min, pause/resume switch, collection-gap notes per D-019).
4. **The 4 blocked RSS feeds** (Al Arabiya ar+en, Enab Baladi, Maariv) — no path today; check for a live Telegram channel as the established fallback if any is high-priority.
5. **The Owner sets up the API key** (`MESG-Orders-API-Key-v0.1.md` Part A) whenever ready — then K-1–K-7, then O-3 (the bake-off, now runnable against real collected items instead of fresh fetches), then the Analysis + Daily Brief order.
6. **OFAC label fix** (`findings.md`, 2026-09-27) and the **severity vocabulary mismatch** (`findings.md`, 2026-09-13) — both still open, unrelated to ingestion.
7. See `MESG-baton-handoff-2026-09-27.md` (this drop) for ready-to-paste opening prompts, and `MESG-decisions-log-2026-09-27.md` for the full current decision index.

---

*This close-out is the baton. Commit it to the repo. Next session starts by reading it.*
