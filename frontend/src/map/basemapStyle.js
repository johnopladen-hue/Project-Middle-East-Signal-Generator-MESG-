/** Neutral MapLibre style over the self-hosted CENTCOM-AOR PMTiles extract
 * (D-014/D-015). Disputed boundaries render distinctly (O-4) - the vector
 * data's own `disputed` field, not a manual overlay (see findings.md).
 * Palette reuses the app's own design tokens (frontend/src/index.css). */

const INK = "#1f2430";
const INK_MUTED = "#5b626e";
const SURFACE = "#f7f8fa";
const LAND = "#eef0ea";
const URBAN = "#e2e4df";
const WATER = "#bfd3de";
const REGION_LINE = "#b3b9c2";
const ROAD = "#c9cdd2";
const DISPUTED = "#c8912a"; // grade-3 amber - "flagged/uncertain", not a verdict

// The extract carries tiles up to zoom 5 only (findings.md, 2026-09-27: the
// full-AOR re-extract was trimmed to z0-5 for size). MapView caps the map's
// zoom at BASEMAP_MAX_ZOOM so the data is never stretched past one level
// of overzoom into jagged, empty detail.
export const BASEMAP_MAX_ZOOM = 6.5;

// English name, falling back to the local name. The fallback also covers a
// real upstream defect: Türkiye's `name:en` is the single letter "T" in the
// 2026-09-27 build (findings.md, 2026-10-11), so a one-character English name
// is treated as missing.
export const LABEL = [
  "case",
  [">", ["length", ["coalesce", ["get", "name:en"], ""]], 1],
  ["get", "name:en"],
  ["get", "name"],
];

export function basemapStyle(pmtilesUrl, glyphsUrl) {
  // Self-hosted glyphs (frontend/public/fonts/), not a public font/tile
  // server - O-3's PROOF requires zero requests to any public server.
  // Ranges self-hosted (Noto Sans Regular, protomaps/basemaps-assets, OFL):
  // 0-255, 256-511, 512-767 (Latin + Latin Extended - e.g. Şanlıurfa) and
  // 1024-1279 (Cyrillic - the few Central Asian places with no English name).
  // Every in-AOR place in the extract has an English name, so Arabic/Hebrew
  // ranges (and the RTL shaping plugin they'd need) aren't required.
  return {
    version: 8,
    glyphs: glyphsUrl,
    sources: {
      basemap: {
        type: "vector",
        url: `pmtiles://${pmtilesUrl}`,
        attribution: '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors',
      },
    },
    layers: [
      // Sea is the background; land is drawn from the extract's `earth` layer.
      { id: "background", type: "background", paint: { "background-color": WATER } },
      { id: "earth", type: "fill", source: "basemap", "source-layer": "earth", paint: { "fill-color": LAND } },
      {
        id: "urban",
        type: "fill",
        source: "basemap",
        "source-layer": "landcover",
        filter: ["==", ["get", "kind"], "urban_area"],
        paint: { "fill-color": URBAN },
      },
      {
        id: "water",
        type: "fill",
        source: "basemap",
        "source-layer": "water",
        paint: { "fill-color": WATER },
      },
      {
        id: "roads",
        type: "line",
        source: "basemap",
        "source-layer": "roads",
        filter: ["!=", ["get", "kind"], "path"],
        paint: { "line-color": ROAD, "line-width": ["interpolate", ["linear"], ["zoom"], 4, 0.5, 6, 1.2] },
      },
      {
        id: "boundaries-region",
        type: "line",
        source: "basemap",
        "source-layer": "boundaries",
        minzoom: 4,
        filter: ["all", ["==", ["get", "kind"], "region"], ["!=", ["get", "disputed"], true]],
        paint: { "line-color": REGION_LINE, "line-width": 0.6, "line-dasharray": [3, 2] },
      },
      {
        id: "boundaries",
        type: "line",
        source: "basemap",
        "source-layer": "boundaries",
        filter: ["all", ["!=", ["get", "kind"], "region"], ["!=", ["get", "disputed"], true]],
        paint: { "line-color": INK_MUTED, "line-width": ["interpolate", ["linear"], ["zoom"], 2, 0.8, 6, 1.6] },
      },
      {
        id: "boundaries-disputed",
        type: "line",
        source: "basemap",
        "source-layer": "boundaries",
        filter: ["==", ["get", "disputed"], true],
        paint: { "line-color": DISPUTED, "line-width": 1.5, "line-dasharray": [2, 2] },
      },
      {
        id: "places-dots",
        type: "circle",
        source: "basemap",
        "source-layer": "places",
        minzoom: 4,
        filter: ["all", ["==", ["get", "kind"], "locality"], ["<=", ["get", "min_zoom"], ["+", ["zoom"], 0.5]]],
        paint: { "circle-radius": 2.5, "circle-color": INK_MUTED, "circle-stroke-color": SURFACE, "circle-stroke-width": 1 },
      },
      {
        id: "places-labels",
        type: "symbol",
        source: "basemap",
        "source-layer": "places",
        minzoom: 4,
        // The data's own min_zoom thins labels so cities don't pile up.
        filter: ["all", ["==", ["get", "kind"], "locality"], ["<=", ["get", "min_zoom"], ["+", ["zoom"], 0.5]]],
        layout: {
          "text-field": LABEL,
          "text-font": ["Noto Sans Regular"],
          "text-size": ["interpolate", ["linear"], ["get", "population_rank"], 9, 11, 15, 13],
          "text-offset": [0, 0.9],
          "text-anchor": "top",
          "symbol-sort-key": ["get", "sort_key"],
        },
        paint: { "text-color": INK, "text-halo-color": SURFACE, "text-halo-width": 1.4 },
      },
      {
        id: "country-labels",
        type: "symbol",
        source: "basemap",
        "source-layer": "places",
        // Countries label from the opening (whole-AOR) view, not only from z4.
        filter: ["all", ["==", ["get", "kind"], "country"], ["<=", ["get", "min_zoom"], ["+", ["zoom"], 1]]],
        layout: {
          "text-field": LABEL,
          "text-font": ["Noto Sans Regular"],
          "text-size": ["interpolate", ["linear"], ["zoom"], 2, 11, 6, 15],
          "text-letter-spacing": 0.08,
          "text-transform": "uppercase",
          "text-max-width": 7,
          "symbol-sort-key": ["get", "sort_key"],
        },
        paint: { "text-color": INK_MUTED, "text-halo-color": LAND, "text-halo-width": 1.5 },
      },
    ],
  };
}
