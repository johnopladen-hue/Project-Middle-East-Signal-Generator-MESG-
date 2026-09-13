# MESG — Session Close-Out: Map Interface (Self-Hosted Basemap + UCP Region Lens)

**Date:** 2026-09-13
**Session type:** Code session — executed `MESG-Map-Interface-Orders-v0.1.md`
**Roles present:** Owner + Code (Claude Code, local). Planner not in this session.
**Keel version:** v9

---

## 1. Purpose of this session

Build the geographic map view: a self-hosted Middle-East basemap with clickable call-outs on MESG's located signals/stories/actors, the CENTCOM AOR labeled explicitly as a U.S. operational lens (not neutral geography), and a hook for recording where in-region self-conception diverges from that frame.

## 2. What we did

**O-A/O-B/O-C — [D-014](../decisions/D-014-map-interface-technology.md), [D-015](../decisions/D-015-region-taxonomy-ucp-aors.md) committed; [A-006](../assumptions.md)/[A-007](../assumptions.md) registered.**

**O-1 — Grounding.** Live `origin/main` HEAD confirmed at `8e7cfac` at session start (PR #22, actor layer, had merged since the orders were drafted). Highest decision D-013, highest assumption A-005 — the orders' provisional D-014/D-015/A-006/A-007 numbers confirmed correct as-is. Mid-session, PR #21 (richer 8-story seed data) also merged on GitHub, live under us — merged into this branch and re-resolved a real conflict in `backend/app/dev_seed.py` (see §5).

**O-2 — License gate.** Confirmed live rather than assumed: MapLibre GL JS is BSD-3; Protomaps basemap tiles are ODbL (ASM attribution required) with CC0 cartography; self-hosting is the intended use, proven for real by extracting a genuine 2.9 MB Levant basemap from the live 138 GB daily planet build via 19 HTTP range requests (no full download, no public tile server touched). Nominatim's public API is capped and bulk-forbidden; no self-hosted instance was stood up (deferred, `test_plan.md`).

**O-3/O-4 — Basemap + contested cartography.** MapLibre + self-hosted PMTiles wired into `frontend/src/routes/MapView.jsx`; `© OpenStreetMap` attribution shown. The extract's own `boundaries` vector layer carries a native `disputed` field (OSM's own tagging) — styled distinctly (dashed amber) rather than MESG inventing a manual overlay; recorded in `architecture.md`.

**O-5/O-6 — AOR region layer.** `centcom.mil`'s own AOR page returned HTTP 403 (bot-blocked, same pattern as `state.gov` earlier this project); fell back to a Congressional Research Service "In Focus" product (public domain, dated 2022-03-30) for CENTCOM's real 22-country membership, stored as dated/versioned `AorMembership` rows. The AOR polygon is a real `shapely` union of those 22 countries' actual borders (public-domain Natural Earth data), reproducible via `backend/app/geo/build_aor_polygon.py`. All six AORs are named in the registry; only CENTCOM has data (the other five explicitly deferred).

**O-7/O-8 — Geo endpoint + overlay.** `GET /geo/items` returns located items (stories + organizations) as GeoJSON with a `precision` field (point/city/province/country) and a separate unlocated set — verified live with all four precision tiers present and a clean both-direction reconciliation (128 located + 3 unlocated = 131 total). Markers deep-link to existing story/organization detail via real SPA navigation, not a rebuilt popup. A-007 registered but not yet meaningful at this data volume (see `findings.md`).

**O-9 — Frame-divergence.** A minimal recordable `FrameDivergenceNote` (backend model + endpoint + a small form/list in `MapView.jsx`), scoped by region.

**A real bug was caught before it reached the Owner:** MapLibre GL JS v6.9.0 ships no default export (named exports only); a default import loaded fine at Vite's dev-transform time but threw a real runtime `SyntaxError` the moment the browser actually requested the module. Caught by fetching the transformed module and the optimized dependency bundle directly and reading the real `export {}` statement — not by browser inspection, since none was available this session. Fixed before commit; full account in `findings.md`.

**O-10 — Records.** `test_plan.md` gets three new rows (T-023–T-025) and six new honest deferrals (no frontend component tests for `MapView.jsx`; five non-CENTCOM AORs; no self-hosted geocoder; the rich divergence overlay; `centcom.mil` itself as source; routing/3D/real-time). `findings.md` has four new dated entries: the license re-confirmations, the contested-cartography finding, the CENTCOM source fallback, the MapLibre import bug, and the located-to-unlocated ratio.

**O-11 — This close-out.**

## 3. Which of the five documents changed today

All five: `architecture.md` (Map Interface section — self-hosted basemap, cartographic stance, lens framing, precision model), `decisions.md` + `decisions/D-014-*.md`/`D-015-*.md` (two new decisions), `assumptions.md` (A-006, A-007), `findings.md` (four new entries), `test_plan.md` (three new rows, six new deferrals).

## 4. Verified live state (this session's grounding)

- **Live `origin/main` HEAD at session start:** `8e7cfac` (actor layer merged); **HEAD by session end:** `f6ba395` (richer seed data also merged, mid-session, by the Owner) — merged into this branch.
- **Highest decision after this session:** D-015. **Highest assumption:** A-007.
- **72/72 backend pytest pass**, self-contained (the real UCDP/OFAC/Natural Earth source files are gitignored local data, not fetched in the gate; the checked-in PMTiles extract and precomputed AOR polygon/centroids are small, derived, reproducible artifacts).
- **Frontend lint clean; 61/61 pre-existing Vitest tests still pass** (no new frontend tests added this session — see `test_plan.md` deferral, same gap as the prior session's actor view).
- **Live geo data:** 128 located items (1 point, 1 city, 1 province, 125 country-precision) + 3 deliberately-unlocated stories, reconciling exactly.
- **What the Owner can open in a browser:** http://localhost:5173/map — the self-hosted Levant basemap, the CENTCOM AOR outline and "U.S. command frame" label, call-outs for real Hamas/PFLP/PFLP-GC organizations and synthetic seed stories (click through to existing detail pages), an unlocated-items tray, and a frame-divergence note form.

## 5. Open items → carried to next session

1. **Merge this session's PR.** The auto-mode classifier categorically blocks `gh pr merge` from this session.
2. **Add frontend component tests** for `MapView.jsx` (and the still-outstanding `Organizations.jsx`/`OrganizationDetail.jsx` from the prior session) before building further on either UI.
3. **A live PR was merged mid-session** (richer seed data, PR #21) — worth double-checking there's no similar race the next time two orders land close together; this session caught and resolved the resulting `dev_seed.py` conflict cleanly, but it's worth the Owner knowing it happened.
4. **The five non-CENTCOM AORs, a self-hosted geocoder, UN/EU/UK designation lists, the rich frame-divergence overlay** — all named, explicitly deferred, not silently dropped.
5. **A-007's ratio isn't meaningful yet** — re-check once real ingestion volume exists, not against this seed.
6. **Severity vocabulary mismatch** (first-article session's finding) — still not fixed.

---

*This close-out is the baton. Commit it to the repo. Next session starts by reading it.*
