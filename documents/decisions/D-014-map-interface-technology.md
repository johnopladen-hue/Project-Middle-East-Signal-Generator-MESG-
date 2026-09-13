# D-014 — Map interface technology + self-hosted basemap

**Date:** 2026-09-13
**Status:** Decided

## Decision

Build the geographic map on **MapLibre GL JS** (open-source BSD-3 renderer; the maintained fork taken up after Mapbox GL JS went proprietary in December 2020) with a **self-hosted OSM-derived vector basemap served as Protomaps/PMTiles**, styled with a **neutral cartography we control**. Geocoding, where needed, uses source-provided coordinates first and a self-hostable geocoder (Nominatim/Pelias) behind a mockable interface — no live geocoder in the test gate.

## Context

The map interface orders (`MESG-Map-Interface-Orders-v0.1.md`) require a self-hosted basemap that touches no public tile server and stays within OSM's ODbL. Re-confirmed live before wiring anything (O-2, per Standing Order 1 and the same gate pattern as [D-013](D-013-source-licensing-posture.md)):

- **MapLibre GL JS** — BSD-3-Clause, confirmed live.
- **Protomaps basemap tiles** — a Produced Work of OpenStreetMap under **ODbL** (attribution required); Protomaps' own styles/cartography are **CC0**. Self-hosting is the explicitly intended use. Confirmed for real, not just read: `pmtiles extract` (go-pmtiles) against the live daily build `https://build.protomaps.com/20260913.pmtiles` (a 138 GB planet file) pulled a 2.9 MB Levant-bbox extract via 19 HTTP range requests — no full download, no public-facing tile endpoint used at runtime.
- **Nominatim** — public API capped at 1 req/sec, bulk/systematic queries forbidden; self-hosting is the documented path for volume. No self-hosted instance was stood up this session (see `findings.md`); the geocoder interface is mockable and unused in the gate.

## Options rejected

- **Google Maps.** Rejected — restrictive ToS, per-load billing, cannot self-host or neutralize the cartography (MESG's own frame-of-record posture, D-015, requires control over the style).
- **Mapbox GL JS.** Rejected — proprietary since December 2020; token, billing, vendor lock-in.
- **The public OSM tile servers** (`tile.openstreetmap.org` et al.). Rejected — explicitly not for production or heavy/programmatic use; can be blocked without notice; unusable offline, which the test gate requires (Standing Order 2).

## Evidence

- Owner ruling (implicit in the orders' own drafted content, ratified this session): self-host, no public tile server, ODbL-compliant.
- `findings.md`, 2026-09-13 — the live license re-confirmation and the real extract.
- `frontend/public/basemap/levant.pmtiles` — the actual self-hosted artefact this decision produces.

## Supersedes

None; extends [D-012](D-012-actor-network-layer.md) (the actor layer this map visualizes) and provides the Theatre taxonomy's geographic backing for [D-015](D-015-region-taxonomy-ucp-aors.md).
