# MESG — Build Orders: Topic Buttons (Drill-Down by Special Topic, Region vs English)

**Doc ID:** MESG-Orders-Topics-v0.2. This supersedes v0.1 (2026-10-11), which this revision removes from the project so no stale copy drifts.
**From:** Planner (revised in a Code session acting as Planner)
**To:** Builder (Code, local, cwd `C:\MESG`)
**Keel version:** v9
**Date:** 2026-11-01
**Status:** ISSUED. Execute TP-0 → TP-7 in order, one PR each.
**Grounded against:** live `origin/main` @ `f1e9512` (PR #40, D-022, merged 2026-11-01).
- Highest decision on `main`: D-022. The Telegram-widening order expects D-023 next.
- Highest assumption: A-012. Telegram widening expects A-013.
- Highest test: T-049.
- Open: #41 (Telegram widening W-0).
- `backend/app/scheduler.py` has jobs `rss`, `telegram`, `translate`.
- **No backup code exists.**

**Every number this order needs is "next free at the time, confirmed against live".** None is promised here.

**Sequencing (Owner priority, 2026-11-01: "I don't see it in the app"). This order goes next.** It can start as soon as PR #41 (Telegram widening W-0) has merged.
- Telegram widening is paused anyway at its Owner gates (the W-1 probe on the Owner's PC, then the W-2 approvals), so the two don't compete.
- **The one rule:** never have PRs from two different orders open at the same time. Topics, Telegram widening and YouTube all touch `scheduler.py`'s `JOB_INTERVALS`, `scripts/capture_frontend_fixtures.py` and `test_plan.md`, and running them in parallel caused the 2026-11-01 merge churn (`findings.md`).
- If a Telegram widening step is in flight when this order starts, finish and merge that step first.
- Topics doesn't depend on YouTube or on Telegram widening: their items get tagged automatically whenever those land. The `voice_type` filter and the per-perspective split (TP-5) switch on only if Telegram widening W-3 has landed.

### What changed from v0.1

| v0.1 said | v0.2 says, and why |
|---|---|
| Six topics: Iran/Epic Fury, Gaza, Lebanon/Hezbollah, Yemen/Houthis/Red Sea, Hormuz/shipping, Syria/Iraq militias | **Owner ruling 2026-11-01: three to start, "U.S.–Iran War", "Houthis", "Gulf States".** The other v0.1 topics are not seeded. The Owner can add any of them later in the admin page (TP-5), so v0.1's drafts are kept in Appendix B as ready-made starting points, inactive. |
| A Topics nav entry and a grid page | Kept, plus **one-click topic buttons** (TP-5): a `TopicBar` on the Dashboard and `/incoming`, one button per active topic with its 24 h count. That is the Owner's "buttons in-app". |
| D-022, A-012, A-013 | Next free numbers. D-022, A-011 and A-012 were taken on 2026-11-01. |
| Execute after U-2…U-6 and YouTube | **This order goes next, by Owner priority.** U-2…U-5 are merged. TP-0 checks U-2 (translation) and U-3 (scheduler) are live, and reports (without blocking on) U-3's real-run proof. YouTube and Telegram widening are not prerequisites. |
| Native seed terms trusted as drafted | **Every native seed term must be shown in use**, in its intended sense, in a real collected item before it is seeded `approved`. Otherwise it is seeded as `candidate` (TP-3). That is harvest, never generate, applied to vocabulary. |
| No source profiles | If Telegram widening W-3 has landed, topic pages also filter by `voice_type`, and topic stats split by perspective (A-012 of D-022, channel selection as a proxy). |

---

## 0. What the Owner asked for

> 2026-11-01: "I would like to have some buttons in-app so someone can pull up stories by special topic. To start with, I would like to have 'U.S.-Iran War,' 'Houthis,' and 'Gulf States.'"

> 2026-10-11 (still standing): "A topics area. If you want to drill down into all things Iran/Epic Fury, you click that tab and it takes you to the articles relevant to that." Topics are **maintained by the Owner in an admin page**, versioned and logged, with re-tagging automatic.

**What appears under a topic today is items, not stories.** MESG has no real Stories yet: the Analyst track, which needs the Claude API key, makes them, and the Dashboard's stories are the labelled dev seed. A topic page therefore lists **collected items** (articles, posts, later videos), each tagged with the terms that put it there. When real Stories exist, topic pages gain a Stories section. That is carried forward (TP-7), not built here. The page's honesty line says so.

**The region/English split** (v0.1's design, kept). Each topic page puts **"What the region is saying"** (sources classed `native` or `pre_translated`) beside **"What English media is reporting"** (`english_comparison`), with volume over time for both sides. This is MESG's objective made visible per topic, within D-022's scope: public in-region channels, outlets and named voices against English media. A gap in **attention** (the region loud, English media silent, or the reverse) is itself a signal, and it costs nothing to compute.

**What this order is not:** topics are standing, Owner-defined areas, not Stories (event clusters) and not AI analysis. Tagging uses **deterministic multilingual term rules**: free, explainable ("matched on «الحوثي»") and auditable. A Claude-assisted tagger is a later upgrade once the Analyst exists, and is named as deferred in the decision.

---

## 1. Standing orders

The eleven of `MESG-Orders-Telegram-Widening-v0.2` §1:
1. Ground first.
2. The suite stays self-contained.
3. Every result carries its artefact and count, and **every rate carries its n**.
4. Cite decisions by number and name, with numbers confirmed free.
5. Harvest, never generate. Matching fixtures are genuine captured items.
6. Designated sources are read-only.
7. **New tables only, no `ALTER`.**
8. No anti-bot evasion.
9. PRs go to the Owner to merge. Check `base` is `main`, and confirm the merge is on `main` before reporting it.
10. Channels, not people.
11. No incitement-first channels.

---

## 2. Decision and assumptions to record (TP-0)

Confirm each number is free against live before writing it.

**D-0NN — Topic tagging: deterministic multilingual term rules, Owner-maintained in-app.**
- **Decision:**
  - A topic is a set of **rules**. A rule is an AND of **term groups**; a group is an OR of **terms**.
  - An item is in the topic if **any** rule matches and no **exclusion** term matches.
  - Terms match against the **original text** (with per-language normalization and clitic handling, TP-2) and/or the **NLLB English triage translation**.
  - Each tag records which terms matched.
  - Definitions live in the DB, edited in an admin page. Every edit bumps the topic's version and writes a change-log row.
  - **The v1 active topics are the Owner's three of 2026-11-01:** U.S.–Iran War, Houthis, Gulf States.
- **Context:** the Owner rulings of 2026-10-11 and 2026-11-01; D-022 (bounded scope); D-016 (translation & analysis providers) cost model.
- **Options rejected:**
  - **Claude classification of every item:** ~3,000+ items/day breaks D-016's $20 cap. Deferred until the Analyst, then only for ambiguous items.
  - **Source-based topics** (e.g. "every Gulf outlet = Gulf States"): this tags an outlet's football coverage as the topic, and hides what non-Gulf sources say about the Gulf.
  - **A YAML file edited by PR:** the Owner ruled in-app. A YAML export exists for audit and backup only (TP-1).
  - **Embedding/semantic similarity:** opaque about why an item matched, and it needs a model pass per item. Revisit if the recall assumption fails.
  - **The six v1 topics of 2026-10-11:** superseded by the Owner's three. Their drafts are kept in Appendix B, inactive.
- **Evidence:** the Owner rulings; D-016's cost model; U-2's measured NLLB throughput (0.79 items/s, `findings.md` 2026-10-11).
- **Supersedes:** none.
- **Assumptions relied on:** the two below, plus A-008 (NLLB triage good enough), because English rules run against NLLB output, and NLLB is known to mangle names (U-2 spot-check). That is why native terms matter.

**A-0NN — Term rules give usable precision for topic drill-down.**
- **Falsifying test:** after ≥100 Owner flags on a topic (TP-6), precision is below 80%.
- **If false:** tighten the rules, or add the Claude second pass for that topic.

**A-0NN — Term rules miss few relevant items.**
- **Falsifying test:** in TP-6's "review untagged" sample (≥50 items reviewed over 3+ days), more than 10% of reviewed untagged items get marked "belongs to topic X".
- **If false:** run term discovery (TP-3) on the misses, or adopt the semantic option.

---

## 3. The orders

### TP-0 — Ground and record

1. Report:
   - HEAD and open PRs. **If a PR from another order is open, stop and ask the Owner which merges first** (see Sequencing);
   - the highest D-/A-/T- numbers;
   - suite counts;
   - whether Telegram widening W-3 (`SourceProfile`) has landed. It's optional for this order;
   - whether U-3's real-run proof is in `findings.md`. Report it, don't block on it.
2. Confirm U-2 (translation) and U-3 (scheduler) are live on `main`. **If they aren't, stop**, because tagging depends on `working_text` and the scheduler.
3. Write the decision and both assumptions (§2), and add the index rows.
4. Commit this order unedited to `documents/orders/`.

---

### TP-1 — Database backup, verified (Keel v9, Principle 1)

**Why now:** topic definitions are the first **curated, non-re-fetchable** data the Owner builds up in the DB. Collected items can mostly be re-fetched; a month of hand-tuned topic rules can't. `backend/mesg_dev.db` is the only copy today (grounding above: no backup code on `main`).

**Build:**
- **Backup job** `app/backup.py`:
  - Uses SQLite's online backup API (`sqlite3.Connection.backup`) to write `backend/data/backups/mesg-YYYYMMDD-HHMM.db`. `backend/data/` is already gitignored.
  - Runs **daily as a scheduler job** (add `backup` to `JOB_INTERVALS`, writing `IngestRun(job="backup")` like every other job), and on demand via `python -m app.backup --now`.
  - Retention: the newest 14.
- **Verification is part of the backup, not a separate hope:**
  - `PRAGMA integrity_check` on the copy must return `ok`.
  - Record per-table row counts of the copy.
  - **Guard:** the copy must have at least as many rows in append-only tables (`raw_items`, `item_topics`, `topic_change_log`, `ingest_runs`) as the previous backup. A shrink is a **hard failure**, not a warning: the "2,771 rows → 1" scar in Keel v9.
- **New table** `BackupRun(started_at, finished_at, path, status, integrity, row_counts JSON, error)`.
- **Status strip:** "Newest verified backup: N h old". Missing or failed is shown in words, not colour alone, the same pattern as U-3's flags.
- **Write in the code what this does not cover:** the backups sit **on the same disk** as the database, so they don't protect against disk loss or a stolen PC.
  - Copying `backend/data/backups/` off the machine is an **Owner action**. Say so in the close-out.
  - Collected content must stay on the Owner's machines (D-018). An external drive satisfies that. A personal cloud drive is the Owner's call, so state it and don't decide it.
- **Topic definitions export:** `GET /admin/topics/export` (admin only), and the daily job writes `backend/data/backups/topics-YYYYMMDD.yaml`. It is human-readable, so a bad edit can be seen and reverted by eye.
- **Tests:**
  - A backup of a temp DB passes integrity, and its counts match.
  - A shrink between consecutive backups is a hard failure.
  - Retention keeps 14.
  - The job never starts in the test suite (U-3's `hold_jobs`/stand-in-runner pattern; findings 2026-11-01).
  - **Mutation proof:** disable the shrink guard and confirm the shrink test goes failure-red.
- **Real proof:**
  - One real backup: path, size, integrity result and row counts.
  - **Restore rehearsal:** copy the backup to a scratch path, point `MESG_DATABASE_URL` at it in a **separate shell**, start the backend **without** `MESG_SCHEDULER` on another port, and load `/incoming`.
  - Record both in `findings.md`.
  - **Never point the live backend at the copy, and never overwrite `mesg_dev.db`.**

---

### TP-2 — Topic model and matching engine (pure, gate-tested)

**New tables (no `ALTER`):**
- `Topic(id, slug unique, name, description, active, sort_order, version int, created_at, updated_at)`. `sort_order` sets the button order.
- `TopicRule(id, topic_id, label)`
- `TopicTerm(id, rule_id nullable, topic_id, group_no int, term, lang ∈ {en, ar, fa, he}, field ∈ {original, translation, both}, kind ∈ {include, exclude}, status ∈ {approved, candidate}, note, added_by, added_at)`.
  - Exclusions attach at topic level, with `rule_id` null.
  - **Only `approved` terms tag. `candidate` terms only preview.**
- `ItemTopic(raw_item_id, topic_id, topic_version, matched_terms JSON, tagged_at)`, primary key `(raw_item_id, topic_id)`.
- `ItemTagState(raw_item_id pk, topics_fingerprint, had_translation bool, evaluated_at)`.
  - This makes **"evaluated, matched nothing"** distinguishable from **"never evaluated"** (Keel v9, Principle 11).
  - `topics_fingerprint` = a hash of every active topic's `(id, version)`.
- `TopicChangeLog(id, topic_id, from_version, to_version, change JSON, changed_by, changed_at)`
- `TopicFlag(id, raw_item_id, topic_id nullable, verdict ∈ {relevant, not_relevant, missed}, flagged_by, flagged_at)`

**Matching engine** `app/topics/match.py`, pure functions with no DB access.

- **Normalization per language** (store it, test it, and document it in `architecture.md`). Use explicit `\uXXXX` escapes in every regex (findings 2026-11-01: a pasted range lost its end).
  - **Arabic:** strip tashkeel (U+064B–U+0652, U+0670) and tatweel (U+0640); unify أ/إ/آ → ا, ى → ي and ة → ه. Apply the same normalization to terms and to text.
  - **Persian:** ي → ی, ك → ک; treat ZWNJ (U+200C) as a joiner to drop when matching (so «حزب‌الله» = «حزب الله» = «حزبالله»); strip tashkeel.
  - **Hebrew:** strip niqqud (U+0591–U+05C7). Treat geresh `'`, `׳` and `’` as one character (so «חות'ים» = «חות׳ים»), and gershayim `"`, `״` and `”` as one (so «ארה"ב» = «ארה״ב»).
  - **English (translation side):** casefold. A terminal `*` on a term means prefix match (`strike*`).
- **Token-start matching with proclitic tolerance.** A term must begin at a token start, or after an allowed proclitic, and may run into a suffix (prefix match).
  - **Arabic proclitics:** و ف ب ل ك ال وال فال بال كال لل, so «والحوثي» and «بقطر» match «الحوثي» / «قطر».
  - **Hebrew proclitics:** any sequence of up to 3 of ו ה ב ל מ ש כ, so «ובקטאר» matches «קטאר».
  - **Persian:** no proclitic list; suffix tolerance covers ها / های / ی.
  - **English:** word boundaries; no proclitics.
  - **Multi-word terms** match as consecutive tokens after normalization («سلطنة عمان», «Gulf Cooperation Council»).
- `match_item(original, lang, translation, topic_def) -> MatchResult(matched: bool, terms: list[(term, lang, field)])`.
  - Rules: any rule where every group has ≥1 hit; then no exclusion hit.
  - **Return the terms**, because the UI must show why an item is in a topic.

**Tests:**
- **Fixtures are genuine items harvested from the live DB**, saved as JSON: at least 3 per language, and a positive and a negative per topic. Prefer real items that exercise:
  - an Arabic prefixed form;
  - a Hebrew prefixed form;
  - a Persian ZWNJ or spacing variant;
  - a geresh or gershayim variant;
  - an English translation-only match.
- One assertion per property.
- **The case where correct and incorrect implementations differ (Keel v9, Principle 6, clause c):** a real token that *contains* a seeded term mid-word must **not** match. Find one in the DB. «قطر» inside a longer unrelated word is a likely candidate; Arabic «قطار» (train) is a different spelling and won't do. If none exists, record that in `test_plan.md` and test the boundary on the nearest real token. This catches a naive substring implementation.
- **The ambiguity cases in Appendix A must each have a test** on a genuine item, e.g. Arabic «عمان» meaning Amman, Jordan, must not tag Gulf States.
- **Mutation proofs:**
  1. Remove the proclitic list → the prefixed-form tests go failure-red.
  2. Replace token-start matching with plain substring → the mid-word test goes failure-red.
  - Record both in `test_plan.md`.

---

### TP-3 — Seed the three topics, prove the native terms, then discover more

**Seed** `backend/app/topics/seed_topics_v1.yaml` with the three topics in **Appendix A**, loaded by `python -m app.topics.seed`. It is idempotent on `slug`: it never overwrites a topic the Owner has since edited (version > 1 means hands off).
- English terms match against the translation.
- Appendix B's topics are **not** seeded. They are kept for the Owner to add in TP-5 if wanted.

**Prove each native seed term before it is approved (new in v0.2).** For every native-language term in Appendix A, the seeder's companion script `python -m app.topics.check_seed_terms` lists real collected items containing it (normalized, token-start). Code reports per term: hit count, plus 3 sample items (original + translation).
- **≥1 sample where the term is used in its intended sense** → seed it `approved`.
- **No hits, or only other senses** → seed it `candidate`, and say which, in the PR.
- The script only reads. It writes no tags.

**Term discovery** (`python -m app.topics.discover --topic <slug> --days 14`) is the "harvest, never generate" route to native vocabulary:
1. Take items the topic currently matches **via the English translation only**, per source language. That is the "in" set; everything else in that language in the window is the background.
2. Tokenize the **normalized original text**. Rank unigrams and bigrams by log-odds ratio with an informative prior: in-set versus background, with minimum in-set count ≥ 5.
3. Output the top 40 per language, with in-set count, background count and **3 sample items each** (original + translation). Write them as `candidate` terms with `note = "discovered <date>, n_in=…, n_bg=…"`.
4. **Report at more than one setting (Keel v9, Principle 8):** min-count 5 and 10, and how the top 40 changes.
5. Candidates never tag until the Owner approves them in TP-5.

**Proof:**
- Seed the 3 topics. Report the native-term check (approved vs candidate, per term).
- Run discovery for all 3 and report candidate counts per topic per language.
- Run the first full tagging pass (TP-4) and report **items per topic, per side (region/English), per language**, plus the count of evaluated items matching nothing.
- **Before the run**, write the expected share of items matching ≥1 topic, as a guess with reasoning (Keel P8). Compare after.

---

### TP-4 — Tagging pipeline

- `app/topics/tag.py: tag_pending(db, limit)` evaluates items whose `ItemTagState` is missing, **or** whose fingerprint ≠ the current one, **or** that had no translation and now have one. Order newest first.
  - It writes `ItemTopic` rows (adds and removes) and the `ItemTagState` row.
- **Scheduler job `tag`:** every 5 min, after `translate`; `max_instances=1`; it writes `IngestRun(job="tag")`. It joins U-3's catch-up and gap reporting with no new scheduling code.
- **Re-tag on edit:** a version bump changes the fingerprint, so everything is re-evaluated, newest first, in batches of 2,000.
  - The admin page shows "re-tagging: N of M done". A partial state is visible, not hidden.
- **Reconciliation guard (Keel P11, two paths to one number):**
  - Every `ItemTopic` row's item has an `ItemTagState` with the current fingerprint, or is queued for re-tag.
  - The sum over topics of `ItemTopic` counts equals the `/topics` summary.
  - Test both directions.
- **Mutation proof:** skip the "translation arrived" re-evaluation, then confirm a fixture item matched only via translation goes failure-red.

---

### TP-5 — The topic buttons, topic pages and the topic admin

**API:**
- `GET /topics` — each active topic, in `sort_order`, with:
  - item counts for the last 24 h and 7 d, **split region / English**;
  - a 14-day daily series per side.

  Region = `source_class ∈ {native, pre_translated}`; English = `english_comparison`. Telegram and YouTube items follow their source's class.
- `GET /topics/{slug}/items?side=region|english&since=&window_hours=&q=&lang=&kind=&voice_type=&limit=&offset=&up_to_id=` returns the same item shape as `/raw-items`, plus `matched_terms`. It reuses U-4's search, window and "N new since you opened" mechanics (`max_id`, `newer_count`). `voice_type` applies only if Telegram widening W-3 has landed.
- `GET /topics/{slug}/stats` returns per-source and per-language counts over the window, and topic sources that went silent. If W-3 has landed, it also gives per-perspective counts, which is A-012 of D-022 seen per topic.
- **Admin** (role `admin`):
  - topic create, edit, deactivate and reorder;
  - rules, groups and terms: add, remove, include/exclude, approve or reject candidates;
  - **preview before save:** "this change adds X items and removes Y (last 14 days)", with 10 samples of each;
  - saving bumps the version and writes `TopicChangeLog`;
  - a change-log view per topic.

**UI:**
- **The buttons (the Owner's ask):** a `TopicBar` component.
  - It is a row of buttons, one per active topic in `sort_order` ("U.S.–Iran War", "Houthis", "Gulf States"). Each shows its 24 h count in words: "Houthis · 37 today".
  - Clicking goes to `/topics/:slug`.
  - It sits **at the top of the Dashboard and of `/incoming`**, under the honesty banner.
  - Keyboard-operable, with visible focus, meeting the contrast floor (UI-spec §5.5, T-018).
  - With no active topics it renders nothing. If the topics query fails, it says so in words; it is never an empty gap.
  - It reads from `GET /topics`, so a topic the Owner adds in admin appears as a button with no code change.
- **Nav: "Topics"** → `/topics`, a grid of topic cards. Each card shows the name, the 24 h count, a region-vs-English split bar and a 14-day two-line sparkline. Run the `dataviz`/contrast checks on the colours, and never let colour alone carry meaning.
- `/topics/:slug`:
  - **Header:** the description; counts by side and language; a 14-day bar chart (region vs English per day); top sources.
  - **Body:** two columns, **"What the region is saying"** and **"What English media is reporting"**. Each is an item feed reusing Incoming's item card (RTL, badges, the U-2 translation label), with a "Matched: «…»" chip on every item. On narrow screens the columns become two tabs.
  - Search, the time window, language, kind and (if W-3 has landed) voice filters, as on `/incoming`.
  - **Analyst actions on each item:** "Not relevant to this topic" and "Relevant ✓". These write a `TopicFlag`; they never delete a tag, they are measurement.
- **Honesty line** on every topic page: "Tagged by term rules, not AI. Items appear here because they mention a listed term in the original or in the machine translation. These are collected items, not analysed stories."

**Tests:**
- The `TopicBar`:
  - renders one button per active topic, in order, with counts;
  - an inactive topic has no button;
  - an admin-added topic appears with no code change (fixture with a 4th topic);
  - a failed query says so;
  - it is keyboard-operable;
  - it appears on both the Dashboard and `/incoming`.
- **Contract:** `/topics` counts equal the `total` from `/topics/{slug}/items` for each side, in both directions. The frontend fixture is **captured from the real endpoint** by `scripts/capture_frontend_fixtures.py`, not hand-written.
- The region/English split follows `source_class`.
- Preview counts equal what save then produces (another two-paths-to-one-number check).
- A save bumps the version and writes a change-log row.
- The analyst (viewer) role can't reach admin endpoints.
- Component tests for the cards, the two-column page, the matched chip and the flag buttons.

---

### TP-6 — Measure it (Keel v9, Principle 11)

- **Admin → "Topic quality":**
  - Per topic: **precision = relevant ÷ (relevant + not_relevant), always shown with n**.
  - **"Review untagged":** 25 random evaluated-but-untagged items from the last 24 h, each with "belongs to: [topic]" buttons. These write `TopicFlag(verdict="missed")`.
  - Show the missed rate with n.
- These are the falsifying tests for the two assumptions in §2. Put their thresholds in the page footnote, so the Owner sees when one is falsified.
- **Not on a schedule:** read it when tuning a topic, or when something looks wrong.

---

### TP-7 — Close out

- **`architecture.md`:** a new "Topics" section covering the normalization rules, the matching semantics, the `TopicBar`, and what is deliberately absent (no AI tagging, no people's names seeded, items not stories).
- **`test_plan.md`, `findings.md`:** a close-out and a refreshed `MESG-pre-work-next-session.md`.
- **Carry forward:**
  - the Owner's tuning pass on all three topics, including the U.S.–Iran War scope question (Appendix A);
  - the off-disk backup copy, an Owner action;
  - any Appendix B topics the Owner wants;
  - a possible "Iran domestic" topic;
  - the Claude second pass (after the Analyst);
  - **Stories under topics** once real Stories exist.

---

## 4. Contract tests named in this order

| Producer | Consumer | Lands in |
|---|---|---|
| Backup job → `BackupRun` | Status strip "newest verified backup" | TP-1 |
| `match_item` → `ItemTopic.matched_terms` | `/topics/{slug}/items` → matched chip | TP-2 / TP-5 |
| Tagger → `ItemTopic` / `ItemTagState` | `/topics` counts ↔ `/topics/{slug}/items` totals | TP-4 / TP-5 |
| `GET /topics` | `TopicBar` buttons and counts | TP-5 |
| Admin preview | Admin save (same counts) | TP-5 |
| `TopicFlag` | Topic quality precision and missed rate | TP-6 |

## 5. What could go wrong

| Risk | Signal | Response |
|---|---|---|
| NLLB mistranslates names, so English rules miss | TP-6 missed rate; discovery shows native terms the English side never caught | Approve native terms from discovery. This is exactly what discovery is for. |
| Gulf States swallows business and sport ("Dubai", "Qatar" in football and property news) | TP-3 counts far above the written expectation; precision flags | Propose exclusions or an AND-group in the PR. The Owner decides. |
| U.S.–Iran War swallows all Iran coverage (via R3) | TP-3 counts; Owner reads the page | It is the scope question in Appendix A. The Owner rules, and Code doesn't narrow it unasked. |
| A native term is ambiguous (Amman vs Oman, locomotive vs Qatar) | The TP-3 term check, or precision flags | It is already handled in Appendix A. A new case gets an exclusion or AND-group, with a test on a genuine item. |
| Re-tag after an edit is slow at ~100k+ items | Re-tag progress in admin | Newest first, so today's view is right within minutes. Report the measured rate. |
| SQLite contention with `tag` and `backup` jobs added | `IngestRun` notes, API latency | U-3's WAL and 30 s timeout. If it persists, stop and report. No queue. |

---

## Appendix A — The three v1 topics (seed draft; the Owner tunes in TP-5)

**Conventions:**
- English terms match the NLLB translation; `*` means prefix.
- Groups are ANDed; terms within a group are ORed.
- **Every native term is proven in use before approval (TP-3).**
- People's names are deliberately not seeded, because officeholders change. The Owner can add them, and discovery surfaces the ones in use.

### A.1 U.S.–Iran War (`us-iran-war`, sort 1)

*Description:* "The U.S.–Iran war and its aftermath: strikes, the ceasefire, retaliation, the nuclear file, proxies' attacks on U.S. forces, Hormuz, and talks."

| Rule | Groups (AND) |
|---|---|
| R1 | {Epic Fury, Midnight Hammer} |
| R2 | {Iran*, Tehran, IRGC, Revolutionary Guard*} AND {United States, U.S., America*, Washington, Pentagon, CENTCOM, White House} |
| R3 | {Iran*, Tehran, IRGC, Revolutionary Guard*} AND {strike*, attack*, missile*, drone*, ceasefire, truce, retaliat*, war, nuclear, enrich*, IAEA, Fordow, Natanz, Hormuz} |

**Native seed terms (prove them in TP-3):**

| Language | Iran group (R2, R3) | U.S. group (R2) |
|---|---|---|
| Arabic | «إيران», «طهران», «الحرس الثوري» | «الولايات المتحدة», «أمريكا», «واشنطن», «البنتاغون» |
| Persian | «ایران», «تهران», «سپاه» | «آمریکا», «ایالات متحده», «واشنگتن», «پنتاگون» |
| Hebrew | «איראן», «טהרן», «משמרות המהפכה» | «ארה"ב», «אמריקה», «וושינגטון», «הפנטגון» |

Native group-3 (war) terms come from discovery.

**Scope question for the Owner (flagged in the admin note, not decided here).** R3 tags Iran war items **whether or not the U.S. is mentioned**, e.g. Israel–Iran exchanges. That makes this the broad "Iran war" topic, under the name the Owner gave it.
- **Keep R3:** you see the whole war.
- **Drop R3:** you see only items naming the U.S., which is narrower and closer to the title, and misses the rest of the war.

The default is keep, because v0.1's "war + external" ruling of 2026-10-11 still stands.

### A.2 Houthis (`houthis`, sort 2)

*Description:* "The Houthis (Ansar Allah): their attacks on shipping and Israel, strikes on Yemen, and the Red Sea / Bab el-Mandeb front."

| Rule | Groups (AND) |
|---|---|
| R1 | {Houthi*, Ansar Allah, Ansarallah} |
| R2 | {Yemen*, Sanaa, Sana'a, Hodeidah, Saada} AND {strike*, attack*, missile*, drone*, ship*, vessel*, Red Sea} |
| R3 | {Red Sea, Bab el-Mandeb, Bab al-Mandab, Gulf of Aden} AND {attack*, missile*, drone*, seiz*, hijack*} |

**Native seed terms (R1):**
- **Arabic:** «الحوثي», «الحوثيين», «أنصار الله». Note that «الحوثي» with prefix matching also covers «الحوثيون».
- **Persian:** «حوثی», «حوثی‌ها», «انصارالله», «انصار الله». Seed both spacings: ZWNJ is normalized, but spaces are not.
- **Hebrew:** «החות'ים», «חות'י». The geresh is normalized.

**Native seed terms (R2/R3 place group):**
- **Arabic:** «اليمن», «صنعاء», «الحديدة», «البحر الأحمر», «باب المندب»
- **Persian:** «یمن», «صنعا», «دریای سرخ»
- **Hebrew:** «תימן», «הים האדום»

### A.3 Gulf States (`gulf-states`, sort 3)

*Description:* "The six GCC states (Saudi Arabia, UAE, Qatar, Bahrain, Kuwait, Oman): their politics, security, diplomacy and mediation in the region's conflicts."

| Rule | Groups (AND) |
|---|---|
| R1 | {Saudi*, Riyadh, UAE, Emirat*, Abu Dhabi, Qatar*, Doha, Bahrain*, Manama, Kuwait*, Oman*, Muscat, GCC, Gulf Cooperation Council, Gulf states} |
| Exclusions (topic-level, translation side; the Owner tunes) | {Gulf of Oman}. Shipping-lane mentions belong to Hormuz coverage, not GCC politics. |

**Dubai is left out of R1 on purpose.** It is mostly business, property and transit news. The Owner can add it. Expect business and sport noise from "Qatar"/"Saudi" anyway: TP-3's counts and TP-6's precision will show it, and the fix is the Owner's.

**Native seed terms, with the ambiguities handled:**

| Language | Terms | Ambiguity handled |
|---|---|---|
| Arabic | «السعودية», «الرياض», «الإمارات», «أبوظبي», «قطر», «الدوحة», «البحرين», «المنامة», «الكويت», «سلطنة عمان», «مسقط», «مجلس التعاون الخليجي», «دول الخليج» | **«عمان» alone is not seeded.** In Arabic it is both Oman and **Amman, Jordan**, which MESG's Jordanian sources use daily. Use «سلطنة عمان» / «مسقط». TP-2 must test that a genuine Amman item does not tag. «قطر» is token-start only, so the mid-word test covers it. |
| Persian | «عربستان», «ریاض», «امارات», «ابوظبی», «قطر», «دوحه», «بحرین», «کویت», «عمان», «مسقط», «شورای همکاری خلیج فارس» | In Persian «عمان» is Oman (Amman is «امان»), so it is safe here. Watch «عربستان»: it is Saudi Arabia in news usage, but historically also Khuzestan. The TP-3 check decides. |
| Hebrew | «סעודיה», «ריאד», «איחוד האמירויות», «האמירויות», «קטאר», «דוחא», «בחריין», «כווית», «עומאן», «מוסקט» | **«קטר» is not seeded:** it also means "locomotive". Use the common news spelling «קטאר», and let discovery surface «קטר» usage if real items use it for Qatar, with a test. |

The Persian «خلیج فارس» (Persian Gulf) and the Arabic «الخليج العربي» are **not** seeded as Gulf States terms. They name the body of water, and they are politically loaded in opposite directions. Discovery will show whether they belong.

## Appendix B — The v0.1 topics, kept as drafts (inactive; not seeded)

These are the Planner's 2026-10-11 drafts for **Israel–Hamas/Gaza**, **Lebanon/Hezbollah**, **Strait of Hormuz/shipping** and **Syria/Iraq militias**. The Owner can create any of them in the admin page, using v0.1's rules as a starting point: it is in the repo history of `documents/orders/` once TP-0 commits this order, and the v0.1 text follows.

| Topic (slug) | Rule(s): groups ANDed, terms ORed | Native names drafted |
|---|---|---|
| Israel–Hamas / Gaza (`gaza`) | R1: {Gaza, Hamas, Qassam, Rafah, Khan Yunis, Khan Younis, Jabalia, Deir al-Balah, Islamic Jihad} | ar «غزة», «حماس», «القسام» · fa «غزه», «حماس» · he «עזה», «חמאס» |
| Lebanon / Hezbollah (`lebanon-hezbollah`) | R1: {Hezbollah, Hizbollah, Hizballah} · R2: {Lebanon, Lebanese, Beirut, Dahiyeh, Litani, UNIFIL} | ar «حزب الله», «لبنان» · fa «حزب‌الله», «لبنان» · he «חיזבאללה», «לבנון» |
| Strait of Hormuz / shipping (`hormuz-shipping`) | R1: {Hormuz, Bandar Abbas, Gulf of Oman} · R2: {tanker*, vessel*, ship*, maritime} AND {seiz*, attack*, clos*, blockad*, detain*, mine*} | ar «هرمز» · fa «هرمز», «بندرعباس» · he «הורמוז» |
| Syria / Iraq militias (`syria-iraq-militias`) | R1: {Syria*, Damascus, Aleppo, Idlib, HTS, SDF} · R2: {Iraq*, Baghdad} AND {militia*, Popular Mobilization, PMF, Kataib Hezbollah, Kata'ib Hezbollah, Islamic Resistance in Iraq, Nujaba, faction*} | ar «سوريا», «الحشد الشعبي», «كتائب حزب الله» · fa «سوریه», «حشد الشعبی» · he «סוריה» |

v0.1's open question still applies to Syria: R1 is broad as written.
