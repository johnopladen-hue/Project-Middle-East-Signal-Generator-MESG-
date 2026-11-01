# MESG — Build Orders: Telegram Widening (Track 1 of D-022)

**Doc ID:** MESG-Orders-Telegram-Widening-v0.2 (v0.2 adds Appendix A.3, the Levantine Arabic candidates; the orders themselves are unchanged from v0.1)
**From:** Planner (written in a Code session acting as Planner, 2026-11-01)
**To:** Builder (Code, local, cwd `C:\MESG`)
**Keel version:** v9
**Date:** 2026-11-01
**Status:** ISSUED. Execute W-0 → W-6 in order, one PR each. **W-2 is an Owner gate: nothing is seeded until the Owner has ruled on each candidate.**
**Executes:** D-022 (bounded scope; widen Telegram; Reddit by research application), item 2, inside D-018 (collection posture) and behind the D-021 (v1 approved source set) approval gate.
**Planner grounded against:** live `origin/main` @ `4207d04` (PR #35 merge, 2026-11-01) plus PR #39 (Reddit probe finding) merged after it.
- PR #40 (D-022) was **open** at writing; W-0 confirms it has merged.
- Highest decision D-021 on `main`, D-022 in #40. Highest assumption A-010 on `main`, A-011/A-012 in #40. Highest test T-049.
- Suites: backend 198/198, frontend 129/129 on `main`; 130 with #40.

Re-confirm every number against live (Standing Order 1).

---

## 0. The goal, in one paragraph

MESG's Telegram set is 17 channels, and most of them are outlets or institutions: Fars, IRNA, WAFA, Al Mayadeen, the IDF. Only a few are individual voices. D-022 bounds the objective to "public in-region channels, outlets and **named voices**". This order adds the voices: named journalists and commentators, local and city channels carrying residents' reports, citizen-reporting and rights-monitoring channels, and a few OSINT watchers. They are balanced by perspective in each language community, so that a divergence MESG reports is not just an artefact of whom we chose to listen to. That last point is A-012 (channel selection as a fair proxy), which this order also instruments.

**Not in this order:**
- Telegram public groups and comment threads. They need an account and a change to D-018, and are D-022 item 5, still open.
- Reddit (D-022 item 3, a research application).
- X/Twitter.
- Any account or credential.

**Clean stopping points:**
1. After **W-1**, the Owner has a per-handle verification report from their own PC.
2. After **W-4**, the approved new channels are collecting on the scheduler.
3. After **W-5**, the Owner can see the perspective balance of what MESG hears.

---

## 1. Standing orders (every step)

The same nine as `MESG-Orders-Usable-Today-v0.1` §1. In short:

1. Ground before you act; if stated state is wrong, stop and say so.
2. The test suite is self-contained: no network, no live Telegram.
3. Every result names its artefact and count.
4. Cite decisions by number **and** name. Confirm D-, A- and T- numbers are free against live.
5. **Harvest, never generate.** Every fixture is a genuine captured excerpt, and so is every candidate fact: handles come from evidence, never from a guess.
6. Designated and sanctioned sources are read-only, flagged and never republished wholesale.
7. **No `ALTER` on existing tables.** New tables only, so `create_all` handles an existing DB with no reset.
8. **No anti-bot evasion.** Use `MESGBot/0.1`, at most 1 request per 2 s to `t.me`, sequential. A blocked handle is recorded as blocked.
9. Branch, PR, and ask the Owner to merge. **Check each PR's base is `main` before merging, and confirm the merge commit is an ancestor of `origin/main` before reporting it landed** (findings, 2026-11-01, the stacked-PR lesson).

**Added for this order:**

10. **Channels, not people (D-018).**
    - Every candidate is a public **channel**: a public figure, a journalist, an organization, or a local news operation.
    - No channel run by a private individual who is not a public figure.
    - No groups and no bots.
    - Store nothing about commenters.
11. **No incitement-first channels.** A channel whose primary content is executions, incitement or graphic violence is rejected at W-1 whatever its analytical value. The reason is recorded.

---

## 2. Owner actions

- **[OWNER] O-a.** Review **Appendix A** (the candidate list, delivered with or shortly after this order) and add or strike names before W-1 runs. The Owner knows sources the research did not find.
- **[OWNER] O-b.** At W-2, rule on each verified candidate: **approve, approve-flagged, or reject**. This is the D-021 gate. Code does not pick.
- **[OWNER] O-c (carried forward, not blocking).** Run U-3's real-run proof: `scripts\run.py` for 35 minutes or more, then 20 minutes off and a restart. W-4's volume check is far more meaningful once the scheduler's own `IngestRun` history exists.
- **[OWNER] O-d (not blocking).** File the Reddit researcher request (draft delivered 2026-11-01). Record the filing date in `assumptions.md` A-011, because its 60-day falsifying clock starts then.

---

## 3. The orders

### W-0 — Ground

1. Pull live and report:
   - HEAD and open PRs;
   - the highest D-, A- and T- numbers;
   - both suite counts;
   - whether `backend/.env` exists.
2. **Confirm PR #40 (D-022) has merged.** If it hasn't, **stop**. This order executes D-022 and must not run ahead of it.
3. Report whether U-3's real-run proof (O-c) has been recorded in `findings.md`. Do not block on it.
4. Commit this order to `documents/orders/` (create the folder) **unedited**, so the order is in the repo it governs. Earlier orders lived only in Downloads and in the Planner's project, and that is how stale copies drifted.

**Proof:** the grounding report in the PR description.

---

### W-1 — Candidate verification probe (from the Owner's PC)

**Build** `scripts/verify_telegram_candidates.py`. It is a script, not app code: it writes no database rows.

- **Input:** `documents/reference/telegram-candidates-2026-11.yaml`. Commit Appendix A into it as data, with every row marked `status: candidate`. Fields per row:
  - `handle`, `name`, `language`, `area`;
  - `voice_type`: one of `named_voice`, `local`, `citizen_reporting`, `rights_monitor`, `osint`, `outlet`, `institution`;
  - `perspective`: a short free-text label, e.g. "reformist", "principlist", "anti-Hezbollah", "Haredi";
  - `evidence_urls`;
  - `designation_note`;
  - `research_confidence`.
- **For each handle**, fetch `https://t.me/s/<handle>` with the collector's own `fetch_channel_page` and politeness, and parse the page with `parse_channel_page`. Reuse; don't re-implement.
- **Classify each result into exactly one category.** Every category is a recorded result, never a blank (Keel P11). Confirm the markup for each category against a genuine capture before relying on it:
  - **`ok_channel`:** posts parsed.
  - **`no_preview`:** the page exists but has no message widget. This covers a group, a bot, a user, or a channel with preview disabled. Capture one genuine example.
  - **`not_found`:** the existing `telegram_no_posts_found.html` fixture shape. Confirm it is truly "no such channel" and not just "no posts".
  - **`blocked`:** HTTP 403 or 429, or a network error.
  - **`stale`:** posts exist, but the newest is older than 30 days.
- **For `ok_channel`, report:**
  - newest post time;
  - posts in the last 48 h;
  - the share of posts in the expected script (Arabic-script / Hebrew / Latin), using **explicit `\uXXXX` escapes** in the regex (findings, 2026-11-01: a pasted range lost its end and matched hyphens);
  - the share of media-only posts;
  - an estimate of posts per day.
- **Output:** a Markdown table plus `telegram_candidates_verified.json` (gitignored under `backend/data/`). Code records the table in `findings.md` with the run timestamp.
- **Volume prediction (Keel P8).** Before the run, write the expected new items/day for the whole candidate set in the PR description. Afterwards, compare it with the measured posts/day. Translation capacity is 0.79 items/s (findings, 2026-10-11 U-2), or roughly 68,000 items/day of CPU if the PC were never idle. State the projected daily total (existing ~3,000 + new) and the CPU-minutes it implies.

**Tests (T-050+; confirm free):**
- The classification has one test per category, each built on a **genuine captured** page. You will need to capture `no_preview` and `stale` examples; `not_found` may reuse the existing fixture once its meaning is confirmed.
- The script regex counts Arabic, Persian and Hebrew correctly, and a hyphen-only title counts as none of them.
- The probe never writes to the database. Assert this against a temp DB: zero `sources` and zero `raw_items` rows after a run with a stubbed fetch.
- **Mutation proof:** make `stale`'s threshold off by one day, confirm a failure-red, and restore. Record it in `test_plan.md`.

**Real run:** run the probe from the Owner's PC over all of Appendix A and record the table in `findings.md`. A handle that is `blocked` is reported to the Owner, not retried more aggressively.

**Stop when:** the PR is green and the table is recorded. Report to the Owner. **This is stopping point 1.**

---

### W-2 — OWNER GATE: rule on each candidate → D-023

1. **Code prepares** a ruling sheet in the PR. List every `ok_channel` candidate with its verification numbers, evidence and designation note, **grouped by language community, then by perspective**. Show the current 17 alongside, so the Owner sees the balance before and after.
2. **The Owner rules** on each one: approve, approve-flagged (e.g. "AUTHENTICITY UNCONFIRMED"), or reject with a reason. **Code never fills a ruling in.**
3. **Write D-023: Telegram widening, approved additions.** It is the next free number; confirm against live, since the Topics and YouTube orders also expected numbers here. All five fields:
   - **decision:** the approved list;
   - **context:** D-022 item 2;
   - **options rejected:** the rejected candidates, each with the Owner's reason;
   - **evidence:** the W-1 table;
   - **supersedes:** none. It extends D-021, and D-021 gets an `Amended by: D-023` line.
4. **Seed data.** Append the approved rows to `backend/app/sources/approved_sources_v1.yaml` under a new section header naming D-023. **Do not create a second file**: D-021 says the approved set lives in one YAML. Give each row `added_by: D-023`. If the seeder's `validate()` rejects unknown keys, extend it to allow `added_by`, `voice_type` and `perspective` (with tests for both a good and a bad value). This is validation code, not a schema change.

**Proof:** D-023 and its index row, the D-021 back-reference, and the YAML diff, with no seeding run yet.

---

### W-3 — Source profile: voice type and perspective, as data

A-012 (channel selection as a fair proxy) can't be checked unless MESG knows each source's voice type and perspective. `Source` has no columns for them, and Standing Order 7 forbids adding any.

- **New table** `SourceProfile`:
  - `source_id`: unique FK to `sources`;
  - `voice_type`: the W-1 enum;
  - `perspective`: free text, ≤ 64 characters;
  - `area`: ≤ 64 characters;
  - `profile_note`: text;
  - `updated_at`.

  It is a new table, so `create_all` adds it and no reset is needed.
- **The seeder** (`python -m app.sources.seed_approved`) upserts a `SourceProfile` for every YAML row that has `voice_type`. Re-running it is idempotent: the upsert identity is `source_id`.
- **Backfill all 47 existing sources** in the YAML with `voice_type` and `perspective`, so the balance report covers the whole set, not just the additions.
  - Code **proposes** the labels in the PR; the Owner confirms them in review.
  - Labels describe the source's **stated or well-documented** alignment and cite evidence in `profile_note`. For example, "IRGC-affiliated (OFAC SDN 2023)" is cited from `designation_note`; "pro-Axis of Resistance" is cited from the existing `verification_note`.
  - Where alignment isn't documented, the label is `unlabelled`, not a guess (Keel P11).
- **The API:**
  - `GET /raw-items` items gain `voice_type` and `perspective` (null-safe);
  - `/admin/sources` shows them;
  - `GET /raw-items` accepts `voice_type=`.
- **The UI:** a **Voice** quick filter on `/incoming` (All / Outlets & institutions / Named voices / Local / Citizen & rights / OSINT), in the same `aria-pressed` pattern as U-4's filters. Each item card shows the perspective label as a neutral badge.

**Tests:**
- The seeder upserts profiles and is idempotent.
- A YAML row with an unknown `voice_type` is rejected loudly.
- `voice_type=` filters correctly.
- **Contract:** `SourceProfile` → `GET /raw-items` → Incoming badge and filter. Capture the frontend fixture via `scripts/capture_frontend_fixtures.py`, not by hand.
- Mutation proof on the filter.

**Stop when:** the PR is green.

---

### W-4 — Seed and collect

1. Run `python -m app.sources.seed_approved` against the dev DB. Report sources created, sources updated and profiles upserted.
2. **Collect for real.**
   - If U-3's scheduler is running (`scripts/run.py`), report the next Telegram `IngestRun` after seeding.
   - Otherwise run `python -m app.ingest --once`.
   - Report, per new channel: fetched / new / skipped_media_only / gap_possible / stale_snapshot / error.
3. **Compare with W-1's volume prediction.** A 10× miss either way is a finding.
4. **Translation load.** After 24 h on the scheduler, report:
   - translate `IngestRun` items/day;
   - whether the backlog drained (count of items still awaiting translation);
   - CPU-minutes/day at 0.79 items/s.

   If the load doesn't fit, **stop and tell the Owner**. D-021's rule applies: throttle the highest-volume channels first and never drop a source silently.
5. **Eyeball `/incoming`** with Voice = Named voices for each language. Confirm right-to-left rendering, and that the perspective badges read correctly.

**Stop when:** the run is recorded in `findings.md`. **This is stopping point 2.**

---

### W-5 — The balance report (A-012's instrument)

MESG should show, not just assume, whose speech it is hearing.

- **`GET /sources/balance?days=7`** returns, per language community × perspective × voice_type:
  - active sources;
  - items collected;
  - items translated;
  - the share of that community's items.

  The top 3 channels by volume per community, with their share, show concentration.
- **A Balance section in Admin → Sources** renders this as a table, not a chart. It is small, exact, and readable without colour (UI-spec §5.5).
- **A concentration flag.** When one channel provides >30% of a community's items in the window, the report says so in words: e.g. "Fars provides 41% of Persian items this week." This is the first observable for A-012's falsifying test.
- **A-013 (or next free):** *a 30% single-channel share is the right threshold for a concentration warning.*
  - Falsifying test: once the Analyst exists, divergence findings change materially when the flagged channel is excluded, at shares below 30%.
  - If false: lower the threshold.

**Tests:**
- Aggregation on a constructed `IngestRun`/`RawItem` history built from genuine fixture posts.
- The concentration flag at exactly 30% (strict `>`: exactly 30% is not flagged) and just over it.
- Both directions of the flag.
- A contract test from the endpoint to the Admin table, with a captured fixture.
- **Mutation:** `>` → `>=` on the threshold goes failure-red.

**Stop when:** the PR is green and the first real 7-day balance (or however many days exist) is recorded in `findings.md`. **This is stopping point 3.**

---

### W-6 — Close out

Write `documents/sessions/MESG-close-out-<date>-telegram-widening.md` with:
- the PRs that landed, each **verified on `main`**;
- HEAD and the highest D-, A- and T- numbers;
- suite counts;
- sources by kind, language and voice type;
- the 7-day balance table;
- open items.

Refresh `MESG-pre-work-next-session.md`. Update `architecture.md`: the Ingestion section and the `SourceProfile` table.

**Open items to carry forward explicitly:**
- D-022 item 5, Telegram groups and comments (an Owner ruling, not a build);
- the Reddit request status (A-011 clock);
- the Claude API key, then the Analyst. A-012 can only be properly tested once divergence findings exist;
- per-perspective sensitivity analysis, once the Analyst exists;
- anything W-1 found `blocked` or `no_preview`.

---

## 4. Contract tests named in this order

| Producer | Consumer | Lands in |
|---|---|---|
| Candidate YAML + `fetch/parse_channel_page` | Verification table and JSON (no DB writes) | W-1 |
| Seeder → `SourceProfile` | `GET /raw-items` `voice_type`/`perspective` → Incoming Voice filter and badge | W-3 |
| `RawItem` + `SourceProfile` + `TranslationRecord` | `GET /sources/balance` → Admin Balance table | W-5 |

## 5. What could go wrong, and what to do

| Risk | Signal | Response |
|---|---|---|
| A candidate handle is wrong or impersonated | W-1 `not_found`, or the channel's content doesn't match the claimed identity | Reject or flag "AUTHENTICITY UNCONFIRMED" at W-2. Check the handle against the person's or outlet's own site where one exists. |
| t.me throttles the probe | 429s in W-1 | Record them. Don't retry faster. Re-run only the blocked rows later, at the same politeness. |
| The perspective labels themselves are the bias | Owner disagrees with labels in W-3 review | The Owner's labels win. `unlabelled` beats a guess. Record contested labels in `profile_note`. |
| Volume swamps translation | W-4 backlog grows day over day | Stop and tell the Owner. Throttle the highest-volume channels first, never silently (D-021). |
| A channel turns to incitement or graphic content after approval | Owner or Code notices in `/incoming` | Set `active=false` through `/admin/sources` (an existing control), record why in `findings.md`, and say so in the next close-out. |

---

## Appendix A — Candidate channels (research input to W-1, not approved)

*Compiled from three parallel research passes (Persian, Levantine Arabic, Hebrew/Israeli) run on 2026-11-01: **51 candidates** (15 + 18 + 18). Each pass's evidence URLs are in its research notes; the tables below carry the research confidence. **Every handle is unverified until W-1 runs from the Owner's PC.** Nothing here is approved: D-023 is the approval.*

**How the research checked handles, and its limits.** Researchers worked from web search, directory listings (tgstat, telemetr), the outlets' and people's own sites, and Factnameh's 2026 analysis of regime-aligned Telegram. A `t.me/s/` preview could be opened only when search had surfaced its URL. Direct requests to `t.me` and `tgstat` were refused in the research environment, and the researchers did not work around that. The previews showed times of day but not calendar dates, so "latest" comes from dates mentioned inside posts (Iranian dates converted). Rates are rough. **W-1 replaces all of this with real measurements from the Owner's PC.**

### A.1 Persian / Iranian (15 proposed)

| handle | name | voice_type | perspective | area | research check | flag | conf. |
|---|---|---|---|---|---|---|---|
| haalvsh | HAALVSH (حال وش) | citizen_reporting | Baluch activists; opposes state policy in the province | Sistan-Baluchestan | ~7 Oct 2026; ~6–10/day; 69K | — | high |
| molanaabdolhamid | Molana Abdolhamid (official) | named_voice | Leading Sunni cleric; regime critic from inside Iran | Zahedan | ~30 Oct 2026; 48.9K | — | high |
| KurdistanHRN | Kurdistan Human Rights Network | rights_monitor | Diaspora rights NGO | Kurdistan provinces | Older page only; 3.3K | — | med-high |
| KHRO_ORG | Karun Human Rights Organization | rights_monitor | Ahwazi Arab activists | Khuzestan | Exists, 992 subs; dates unchecked | — | med |
| Tabriz_khabarlary | Tabriz Khabarlary | local | Commercial; follows IRI law; carries reader messages | Tabriz | ~40+/day; 181K | — | med |
| AkhbarMashhad | Akhbar Mashhad | local | Commercial, government-aligned framing; relays reader reports | Mashhad | ~50+/day; 1.04M | — | med |
| kashowra | Coordinating Council of Teachers' Trade Associations | named_voice (union) | Independent teachers' union | National | ~14 Aug 2026; 2–4/day; 17.6K | — | high |
| Shbazneshasteganir | Retirees' Council of Iran | citizen_reporting | Independent / left labour | National | Older page (2025); 4.9K; current activity unconfirmed | — | med |
| jedaal | Jedaal (Ali Alizadeh) | named_voice | Pro-establishment nationalist; against the exile opposition | Diaspora (London) | ~24 Sep 2026; 1–3/day; 57K | — | med-high |
| dr_a_ganji | Abdollah Ganji | named_voice | Principlist; ex-editor of IRGC-linked *Javan* | Tehran | Exists, 2.6K; dates unchecked | IRGC-linked background | med |
| nasiri42 | Mehdi Nasiri | named_voice | Former *Kayhan* editor, now an establishment critic | Iran | Exists, 11.2K; activity unconfirmed | — | med-low |
| mostafatajzadeh | Farda-ye Behtar (Mostafa Tajzadeh) | named_voice | Reformist; imprisoned politician; statements relayed | Tehran | Older page (2022); 42.5K; activity unconfirmed | — | med |
| Afsaran_ir | Afsaran-e Javan-e Jang-e Narm | institution (network) | Principlist; IRGC/security-linked unofficial network (Factnameh) | National | ~30 Oct 2026; 30–40/day; 183K | **IRGC-affiliated; IRGC is US FTO/SDGT** | high |
| sepahcybery | Sepah Cybery | osint | IRGC-branded, unofficial (Factnameh) | National | Exists, 463K; dates unchecked | **IRGC-affiliated** | high |
| saberin_ir | Saberin News (Persian) | osint | Pro-"Axis"; IRGC/security-linked (Factnameh) | National / Axis | ~Aug 2026; rate unclear; 708K | **IRGC-linked**; no SDN listing found, so a formal check is owed at W-2 | med |

**Persian: gaps and rejections.**
- **Gaps.** No Persian-language Hengaw handle was found; `@Hengaw_kurdi` is Kurdish. No Persian-posting Azeri rights monitor was found. 1500tasvir is "mostly an archive" in 2026, and no handle was found for it.
- **HRANA (`hranews`, 31K).** Left out as an outlet. The Owner may add it as a rights wire.
- **Rejected:**
  - `ir_Protests`: MEK-aligned and anonymous, and posts solicit "armed operations". This is incitement, so it fails Standing Order 11.
  - `Kurdistan_Hana`: hijacked (2 subscribers, spam).
  - `iranmilitary_irgc`: English, not Persian.
  - `Khoozestankhabar`: dead since 2020.
- **Possibly stale, worth checking in W-1:**
  - unions `vahedsyndica` and `syndica_7tape`;
  - named voice `mohamadaliabtahi`;
  - teachers' channel `kasenfi`;
  - Isfahan local `akhbareisfahan`;
  - outlets `Eslahatnews` (reformist) and `rajanews_com` (hardline).
- **A signal worth noting for later (not a channel).** Factnameh found that 65% of text posts across 50 regime-aligned channels in the first 72 hours of the Feb–Mar 2026 war were more than 95% identical. **Copy-paste spread across channels is itself detectable**, and could become a coordinated-narrative signal once the Analyst exists.

### A.2 Israeli / Hebrew, plus Arab citizens of Israel (18 proposed; 13 without caveats)

| handle | name | voice_type | perspective | area | research check | flag | conf. |
|---|---|---|---|---|---|---|---|
| US2020US | Amichai Stein, "the diplomatic channel" | named_voice | Mainstream; i24 diplomatic correspondent | National | ~6 Oct 2026; 10–15/day; 22.2K | — | high |
| Ben_Caspit | Ben Caspit | named_voice | Centre-left columnist (Maariv, Walla, Al-Monitor) | National | 8–10/day; 28.8K | — | high |
| yairsherkinews | Yair Cherki | named_voice | Ch. 12 religious and Haredi affairs; religious-Zionist centre | National | ~3/day; 10.4K | — | high |
| HallelBittonRosen | Hallel Bitton Rosen | named_voice | Right; Ch. 14 military correspondent | National | Not opened (directory listing only) | — | med |
| yinonews | Yinon Magal | named_voice | Populist right (Ch. 14, 103FM) | National | Not opened | Documented false claim (the7eye), useful for tracking claim spread | med |
| TheBigBadShadow | "HaTzel" (Yoav Eliasi) | named_voice | Far-right populist influencer; ~300K | National | Not opened | Inflammatory content; not designated | med |
| arab48official | Arab48 | local | Arab-Israeli nationalist-left outlet (Arabic) | Arab citizens of Israel | Oct 2026; 60–90/day; 54.3K | — | high |
| panetbanet | Panet | local | Mainstream commercial Arab-Israeli (Arabic) | Nazareth / Galilee | 30–50/day; 14.7K | — | med-high |
| yosephhaddad | Yoseph Haddad | named_voice | Arab-Christian Israeli; pro-Israel advocate | National | 1–2/day; 49.7K | — | high |
| standingtogether | Standing Together | citizen_reporting | Jewish-Arab left movement (Hebrew and Arabic) | National | Low activity (newest dated ~Nov 2025); 774 | — | med |
| TheKaplanForce | Kaplan Force | citizen_reporting | Liberal anti-government protest movement | Tel Aviv | Event dated Sep 2026; a few posts/month; 426 | — | med |
| local_call | Local Call (Sikha Mekomit) | named_voice (outlet) | Left; Hebrew sister of +972 | National / West Bank | Sporadic; 442; recency unconfirmed | — | low-med |
| North_Media | Northern News / News Line | local | Unaffiliated regional aggregator | North (Galilee, Golan) | 50–80/day; 17.6K | Operator unidentified; marginal under "channels, not people" | med |
| jerusalemtelgram | Jerusalem Municipality (official) | institution | Official municipal | Jerusalem | Oct 2026; 1–3/day; 2.7K | — | high |
| uh1221 | United Hatzalah (official) | citizen_reporting | Volunteer EMS: incident reports | National | 15–20/day; 5.4K | Useful for independent casualty counts and incident checks | high |
| hatzhalhyosh | Hatzalah Judea & Samaria | local | Settler-area rescue service | West Bank settlements | Not opened (directory listing only) | — | med |
| hakolhayehudi | HaKol HaYehudi | named_voice (outlet) | Hard-right settler outlet | West Bank / national | 6.2K; no dates seen | **Extremist-adjacent: monitor-only flag** | med |
| inssisrael | INSS | osint (analysis) | Mainstream security think tank | National | Oct 2026; a few posts/week; 2.9K | — | high |
| osintil | "Osint Israel (OsintIL)" | osint | Unknown | Israel | Title only, nothing verified | — | low |

**Hebrew: gaps, rejections and designation notes.**
- **Gaps.**
  - Haredi press: `RealKikarHashabat` is claimed but has no evidence; HaPargod is on WhatsApp.
  - Gaza-envelope councils use Facebook and WhatsApp.
  - No public Telegram channels were found for B'Tselem, Peace Now, Yesh Din, Breaking the Silence or the Hostages and Missing Families Forum.
  - Israeli OSINT is thin.
- **Rejected:**
  - `barakravid1`: looks compromised (crypto "mining", requests for personal details).
  - Unofficial mirrors: `kann_news`, `haaretz_plus`, `newsisrael13_il`, `now14_israel`.
  - `SecretFlights`: a flight-deals channel.
  - Anonymous or gossip channels: `hazfon1`, `israel1`, `danielamram3`, `is231`.
- **Designation notes on channels seen but not proposed** (the Owner may want any of them as monitor-only):
  - `benziyongopshtein` (Lehava): US-sanctioned April 2024, reportedly lifted January 2025; EU-listed 2024. Status to verify.
  - `bengvir` and `smutrich`: ministers sanctioned by the UK, Canada, Australia, New Zealand and Norway in June 2025.
  - `otzma_yeudit`: a Kahanist-lineage party.
- **Balance observation.** Right-leaning Hebrew channels are publicly catalogued (`ChannelListIL` lists 89; `israel_catalog` keeps a similar list). Nothing comparable was found for the left, so **the Hebrew set will tilt right unless the Owner adds left-leaning voices by hand.** That is A-012 in practice.

### A.3 Levantine Arabic (Lebanon, Syria, Jordan, Palestine)

| handle | name | voice_type | perspective | area | research check | flag | conf. |
|---|---|---|---|---|---|---|---|
| lebanonnews2 | Lebanon News (ليبانون نيوز) | local | Self-described independent; leans critical of Israel | South Lebanon border villages | ~10 posts over 5.5 h; 32.9K; Airwars cites it for civilian-harm incidents | — | high |
| sadadahiechannel | Sada al-Dahiyeh (صدى الضاحية) | local | Hezbollah-sympathetic (inferred), not party media | Beirut southern suburbs | Bursts of posts; 19.2K; Airwars cites it | — | high |
| alakhbar_news | Al-Akhbar (الأخبار) | named_voice (newspaper) | Left, pro-"resistance" daily | Lebanon | ~1 post every 13 min; 29.2K | — | high |
| mtvlebanonews | MTV Lebanon News | named_voice (broadcaster) | Anti-Hezbollah, Christian-leaning | Lebanon | Info page only; 2.0K | — | med |
| HawarNews | ANHA Arabic (Hawar News Agency) | named_voice (agency) | Kurdish-led self-administration (SDF/AANES) line | NE Syria | ~50/day; posts dated 1 Nov 2026; 7.7K | Not designated; Turkey calls it PKK-linked (PKK is a US FTO) | high |
| D24net | Deir Ezzor 24 (دير الزور 24) | local | Local, opposition-rooted | Deir ez-Zor | ~25/day; 10.6K | — | high |
| TelevisionSyria | Syria TV (تلفزيون سوريا) | named_voice (broadcaster) | Ex-opposition, Qatar-funded; broadly pro-transition | Syria | ~1 post every 40 min; 187K, verified | — | high |
| Hadi_abdullah | Hadi al-Abdullah | named_voice | Revolution-era journalist; has criticised al-Sharaa | Syria | Only an archive page seen (2017); 139K, verified; current activity unconfirmed | — | med |
| sn4hr | Syrian Network for Human Rights (SNHR) | rights_monitor | Independent rights NGO | Syria | Only an archive page seen (2021); 2.4K, verified; current activity unconfirmed | — | med |
| SweidaGov1 | Suwayda Governorate (official) | institution | Damascus-aligned; relays SANA and ministry statements | Suwayda | ~17 posts in 1–2 days; 9.2K; cited by Airwars | — | med |
| sentry_syria_observatory | Syria Observatory (Emergency Ministry early warning) | institution (alerts) | Government civil protection | Syria | Posts reference May 2026; <1/day except in bad weather; 22.1K | Feeds the natural-disaster bulletin directly | med |
| nabuls_news | Nablus News (أخبار نابلس) | local / citizen_reporting | Residents' view; has criticised PA detentions | Nablus, West Bank | ~1 post every 4–5 min; 182K; takes tips via a bot | — | high |
| khalelnews | Hebron News Network (شبكة أخبار الخليل) | local / citizen_reporting | Pro-Palestinian, not tied to a faction | Hebron, south West Bank | ~2–3/hr; content dated Aug 2026; 82.5K | — | high |
| madinat_khanyuns | Khan Younis and Its People | local | Pro-Palestinian, not tied to a faction | Khan Younis, Gaza | Several/day; posts dated ~10 Aug 2026; 6.4K | — | med |
| ultrapalestine | Ultra Palestine (الترا فلسطين) | named_voice (outlet) | Independent (Ultrasawt network) | Ramallah / Gaza | ~1 post every 6 min; 43.7K | — | high |
| saidziad | Saeed Ziad (سعيد زياد) | named_voice | Political researcher; Hamas/"resistance"-sympathetic | Palestine / Gaza | Info page only; 21.2K | Hamas-sympathetic; no designation found | med |
| sohaibpress | Sohaib al-Masalmeh | named_voice | Security journalist; translates Hebrew → Arabic | Palestine / regional | Not opened on t.me; Telemetr: 156.8K, "high" frequency, Aug 2026 | — | med |
| ammonnews | Ammon News (عمون) | named_voice (outlet) | Independent Jordanian | Jordan | Info page only; 4.5K, verified | First Jordanian voice in MESG | med |

**Arabic: gaps, rejections and notes.**
- **Duplicate across passes.** `arab48official` is proposed in A.2 (Arab citizens of Israel) and was held in reserve here. Count it once.
- **Gaps:**
  - **Druze Suwayda voice.** Suwayda 24 publishes on X, Facebook and YouTube. `suwaydaa24` has no bio and an unknown operator, so it was left out. SweidaGov1 gives only Damascus's framing, so **Suwayda would be one-sided until a Druze-side voice is found.**
  - **Anti-Hezbollah Lebanon is nearly absent from Telegram.** DFRLab found those journalists on X, and MTV has only ~2K subscribers. **Lebanon will tilt toward Hezbollah-sympathetic voices on Telegram alone.** Another A-012 case.
  - **Arabic OSINT** turned up nothing usable: the candidates were English or faction media.
  - **Jordan is thin.** Roya (`royatv`, 15K), `khabernijordan` (3K) and `Jordantelegram` (9K) exist but are small.
- **Rejected (Standing Orders 6 and 11):**
  - `gazaalannet` (Gaza Now): **OFAC SDN; UK-sanctioned March 2024.**
  - `SarayaMirror` (PIJ armed wing) and `C_Military1` (Hezbollah Military Media, 353K): combat media.
  - `CoastSyrian24`: posts execution content.
  - `jeninnews1`: approves attacks.
  - `khbrnesho`: doxxing.
  - `ShehabTelegram`: duplicates palinfo.
  - `alichoeib1970`: the journalist was killed 28 Mar 2026, so the channel's operator is unknown.
- **Held in reserve:**
  - `RayaNewsPS` (Ramallah; would fill the PA/Fatah-adjacent slot once its alignment is confirmed);
  - `AlmarsadSyria` (pro-Damascus);
  - `lattakiatartous` (coastal, 52K; content not seen).
- **Useful method:** Airwars' incident archive (`airwars.org/source/t-me-…`) was the best independent evidence for local Lebanese handles, and is worth mining for Gaza too.

### A.4 Balance at a glance (before W-1)

| Community | Gaps where the candidate list leaves MESG one-sided |
|---|---|
| Persian | No Persian-language Azeri rights voice; HRANA held as an outlet (Owner's call) |
| Hebrew | Tilts right (right-leaning channels are catalogued, left ones aren't); Haredi press and the major rights NGOs are absent from Telegram |
| Lebanon | Anti-Hezbollah voices largely absent from Telegram (they post on X) |
| Syria | Druze-side Suwayda voice missing |
| Jordan | Thin: one candidate plus small reserves |
| All | Arabic and Israeli OSINT thin; what exists is mostly English or faction media |

These gaps are the **case for D-022 item 5** (Telegram groups/comments) and for a later X decision. They are not a reason to lower the bar here.
