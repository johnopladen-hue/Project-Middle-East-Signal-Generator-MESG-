# D-023 — Map item geolocation: place names in the original text, top 20 on the map

**Date:** 2026-11-01
**Status:** Decided (Owner direction, 2026-11-01)

## Decision

1. **Real collected items go on the map where their text says the event happened, not where the source is based.** The Owner's words: "If a geographic location can be determined, then I want you to place the dot in the vicinity of that location, not the origin of the news story itself."
2. **How the location is determined.** Place names in each item's **original-language text** (Arabic, Persian, Hebrew or English) are matched against an offline gazetteer derived from GeoNames (CC BY 4.0) for the 22 CENTCOM AOR countries (`app/geo/gazetteer.py`, `build_gazetteer.py`, committed `gazetteer.json`). **NLLB triage output is never used.** The 2026-10-11 spot-check showed it garbles place names. There is no live geocoder, which keeps D-014's offline posture.
   - The headline beats the body. Within each, a city beats a province beats a country, and ties go to the first mention.
   - A match with an attached prefix stripped (e.g. Arabic "in Gaza", Hebrew "in Gaza") only counts for major places: 15,000+ people, an administrative seat, a province or a country.
   - A stop list of words that collide with place names is maintained from evidence (`build_gazetteer.STOP_WORDS`, each entry with its ordinary meaning).
3. **No match, no dot.** An item whose text names no place is recorded as `none` and stays off the map, and the map says how many (Keel P11). No source-country fallback.
4. **At most 20 dots ("top 10–20").** These are the 20 most recent placed items in the last 48 hours. City- and province-level placements come first; country-level ones only fill spare slots. Items sharing a place are spread on a small circle around it (about 6 km for a city), so each dot stays clickable.
5. **One click opens the item.** A dot goes straight to the new item page `/incoming/:id`. That page shows the item, where it was placed, and the item's own words that placed it, labelled "machine-matched, not verified".
6. **Storage.** A new table, `ItemLocation`, holds one row per item (no `ALTER`, Standing Order 7). It is written by a five-minute scheduler job, `locate`, and by `app.ingest --once`. Rows carry the gazetteer version, so a rebuilt gazetteer re-checks every item.

## Context

The Owner looked at the live map on 2026-11-01 and found no real news on it. The map only plotted Stories and Organizations, and Stories come from the Analyst, which is not built yet (no Claude API key). So the only Stories were the labelled synthetic dev seed, and the 5,900+ real collected items had no location at all. The Owner asked to be able to click a dot and go straight to the story.

## Options rejected

- **Source's home country.** Fast, but it shows where an outlet sits, not where events happen: BBC Persian on London, Al Jazeera on Qatar, thousands of items piled on about 8 dots. Rejected by the Owner's direction (decision 1).
- **Wait for the Analyst.** It would place Stories properly, but nothing would change on the map until the API key and the Analyst order exist.
- **Geolocate from the NLLB English line.** Rejected on the 2026-10-11 evidence: place names were the most frequent NLLB error (4 of 10).
- **Every GeoNames populated place.** Tried first. Common words matched thousands of village names: "عاجل" (urgent) became a Syrian village 198 times. The population floor (1,000 in the core theatre, 15,000 elsewhere, with administrative seats always kept) and the major-place rule for prefixed matches replaced it.
- **Showing every placed item.** About 1,600 placed items fall in a 48-hour window, far too many dots to read or click. The Owner set the cap.

## Evidence

- Build-time runs over all 5,936 real items: **3,429 located** (city 1,782, province 163, country 1,484), **2,507 with no place name**. The full run took about 3 s.
- Hand-checked random samples, by where the event happened (`findings.md`, 2026-11-01): 24/30, then 21/30 (+1 near), then a final untouched 40-item sample at **30/40 (75%), 31 counting one near miss**. City level was 12/15 (+1 near) and country level 17/23. Country-level misses were mostly statements made abroad about a country.
- Tests T-050–T-054 (`test_plan.md`), with mutation proofs on the city-first ordering, the major-place rule and the dot click.

## Supersedes

None. It extends D-014 (map interface technology), whose geo endpoint gains a `news_items` collection beside the existing Story/Organization set and its reconciliation.
