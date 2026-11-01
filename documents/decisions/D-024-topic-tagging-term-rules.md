# D-024 — Topic tagging: deterministic multilingual term rules, Owner-maintained in-app

**Date:** 2026-11-01
**Status:** Decided (Owner rulings 2026-10-11 and 2026-11-01; recorded at TP-0 of `documents/orders/MESG-Orders-Topics-v0.2.md`)

## Decision

- A topic is a set of **rules**. A rule is an AND of **term groups**; a group is an OR of **terms**.
- An item is in the topic if **any** rule matches and no **exclusion** term matches.
- Terms match against the **original text** (with per-language normalization and clitic handling, TP-2 of the order) and/or the **NLLB English triage translation**.
- Each tag records which terms matched, so the UI can always say why an item is in a topic.
- Definitions live in the database and are edited in an admin page. Every edit bumps the topic's version and writes a change-log row. Only `approved` terms tag; `candidate` terms only preview.
- **The v1 active topics are the Owner's three of 2026-11-01:** U.S.–Iran War, Houthis, Gulf States. A topic page lists collected items, not Stories, until real Stories exist.

## Context

- Owner, 2026-11-01: "I would like to have some buttons in-app so someone can pull up stories by special topic. To start with, I would like to have 'U.S.-Iran War,' 'Houthis,' and 'Gulf States.'"
- Owner, 2026-10-11 (still standing): a topics area to drill down by subject, maintained by the Owner in an admin page, versioned and logged, with automatic re-tagging.
- [D-022](D-022-bounded-scope-and-voice-widening.md) (bounded scope): each topic page sets the region's own channels beside English media.
- [D-016](D-016-translation-analysis-providers.md) (translation & analysis providers): the $20/month cap rules out an AI pass on every item.

## Options rejected

- **Claude classification of every item.** About 3,000+ items/day breaks D-016's $20 cap. Deferred until the Analyst exists, and then only for ambiguous items.
- **Source-based topics** (e.g. "every Gulf outlet = Gulf States"). It tags an outlet's football coverage as the topic, and hides what non-Gulf sources say about the Gulf.
- **A YAML file edited by PR.** The Owner ruled in-app. A YAML export exists for audit and backup only (TP-1).
- **Embedding/semantic similarity.** It can't say why an item matched, and it needs a model pass per item. Revisit if A-014 (recall) fails.
- **The six v1 topics of 2026-10-11.** Superseded by the Owner's three. Their drafts are kept in the order's Appendix B, inactive.

## Evidence

- The Owner rulings quoted above.
- D-016's cost model.
- U-2's measured NLLB throughput: 0.79 items/s (`findings.md`, 2026-10-11).

## Supersedes

None.

**Assumptions relied on:** [A-013](../assumptions.md) (precision) and [A-014](../assumptions.md) (recall), plus A-008 (NLLB triage good enough). English rules run against NLLB output, which is known to mangle names (U-2 spot-check), so the native-language terms carry real weight.
