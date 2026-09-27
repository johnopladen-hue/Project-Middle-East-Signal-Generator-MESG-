# D-016 — Translation & analysis providers: free-first hybrid, Claude capped at $20/month

**Date:** 2026-09-27
**Status:** Decided (provisional pending the O-3 bake-off)

## Decision

1. **Triage translation is free and self-hosted:** Meta's **NLLB-200** (distilled 600M) via CTranslate2 on the Owner's PC, behind the existing `Translator` interface. It translates the headline and lede of every native-language item. **Azure Translator's free tier (F0, 2M characters/month, no card)** is the named fallback, used only if NLLB proves inadequate. This is **provisional pending the O-3 bake-off**, which either confirms NLLB or replaces it with evidence.
2. **Deep analysis uses Claude via the Anthropic API.** That covers full-text translation and analysis of items that cluster into real stories, behind the existing `Analyst` interface (Analyst wiring is the next order). **Hard cap: US $20/month**, enforced in two places: a Console spend limit set by the Owner, and an **in-app budget circuit breaker** (O-2 of `MESG-Ingestion-Orders-v0.1.md`, `LlmSpend` ledger). Use the Batch API for anything not time-critical (the daily brief). Alerts may use standard calls.
3. **Already-translated material is used, as its own source class** (see [D-018](D-018-collection-posture.md)). Where an outlet publishes its own English edition, that text is ingested as-is and not re-translated.
4. The Claude API is billed separately from any Claude subscription; the Owner holds a separate Console account.

## Context

Owner rulings, 2026-09-27: Claude as the LLM provider; $20/month; free-first ("prove it works before adding premium services"); hybrid translation; option **A**, meaning Claude for the deep analysis only, over option B (a local LLM for everything). Candidate-source research found verified Telegram volume far above the Planner's first estimate: Fars ~480 posts/day, Akhbar-e Fori ~400, Al Mayadeen ~215, Quds News ~225. That puts total volume at roughly 2,000–3,000 items/day, which makes paid bulk translation unaffordable at $20.

## Options rejected

- **All-Claude translation and analysis.** At 2,000+ items/day, triage alone would exceed $20 many times over.
- **Cloud free-tier machine translation as the triage engine** (DeepL Free 500k chars/month and Google 500k+500k, card required; Azure F0 2M). Each covers only a fraction of the volume. DeepL Free may use submitted text to improve its service. Azure is kept as a fallback only.
- **A local LLM (Ollama: Qwen, Llama or Gemma) for analysis (option B).** Truly zero-cost, but weaker at nuanced Arabic, Persian and Hebrew analysis. A weak brief would leave it ambiguous whether the idea or the model failed. It is kept in the O-3 bake-off as a comparison point, not adopted.

## Evidence

- Owner rulings, 2026-09-27 session.
- Pricing, checked 2026-09-27: Haiku 4.5 $1/$5 per M tokens in/out, Sonnet 5 $2/$10; Batch API −50%; cache reads ~0.1× input.
- The API is billed separately from subscriptions.
- Free MT tiers, 2026 comparison. DeepL lists Arabic, Hebrew and Persian.
- NLLB-200's original weights are CC-BY-NC 4.0 (non-commercial). Acceptable for personal use; **must be revisited if MESG is ever used commercially.**
- Bake-off report (O-3), to be appended.

## Supersedes

None. Resolves the open "Translation provider" and "Analysis/LLM provider" items (TDD §4.2, §4.4).
