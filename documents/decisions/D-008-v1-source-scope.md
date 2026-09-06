# D-008 — v1 source scope: Levantine Arabic + Persian

**Date:** 2026-09-06
**Status:** Decided

## Decision

MESG's Phase 1 (v1) pipeline covers exactly two language communities from `documents/reference/Languages_and_Religions.md`: **Levantine Arabic** (Syria, Lebanon, Jordan, Palestine/Israel — Sunni Islam, Twelver Shia, Alawite, Druze, and multiple Arab Christian rites) and **Iranian Persian/Farsi** (Iran — Twelver Shia majority, with Zoroastrian/Baha'i/Christian/Jewish minorities). All other language communities in the reference file are out of scope until v1 is proven end-to-end and breadth is deliberately added (TDD §14, Phase 3).

## Context

The TDD (`documents/tdds/MESG-TDD-v0.1.md` §14, Phase 1) and the 2026-08-02 pre-work doc both call for narrowing v1 to "one or two language communities... to prove the pipeline end-to-end before adding breadth," but left the specific choice as an open decision requiring Owner input. `Languages_and_Religions.md` itself existed only as an untracked file in the Owner's Downloads folder (flagged in `documents/findings.md`, 2026-08-02 entry) — it needed to be committed into the repo before it could be cited as the source for this decision.

## Options rejected

- **Levantine Arabic only** (single community, narrowest possible v1). Presented as an option; Owner chose the two-community scope instead.
- **A wider initial scope** (e.g., adding Gulf Arabic or Turkish immediately). Not seriously considered — directly contradicts the TDD's explicit "narrow v1" design principle (§2.4, "Start simple").

## Evidence

- `documents/reference/Languages_and_Religions.md` — the source list, now committed (previously only in the Owner's Downloads folder).
- `documents/tdds/MESG-TDD-v0.1.md` §14 — "Narrow source scope (one or two language communities from `Languages_and_Religions.md`)."
- Owner decision, this session, 2026-09-06: "Levantine Arabic + Persian" (selected over "Levantine Arabic only" and an open-ended "I'll choose different ones").

## Supersedes

None — this is the first resolution of the "v1 source scope" item carried as open since `documents/decisions.md`'s pending list (2026-08-02).
