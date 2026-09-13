/** Neutral MapLibre style over the self-hosted Levant PMTiles extract
 * (D-014). Disputed boundaries render distinctly (O-4) - the vector data's
 * own `disputed` field, not a manual overlay (see findings.md). Palette
 * reuses the app's own design tokens (frontend/src/index.css). */

const INK_MUTED = "#5b626e";
const SURFACE = "#f7f8fa";
const WATER = "#c9d6de";
const DISPUTED = "#c8912a"; // grade-3 amber - "flagged/uncertain", not a verdict

export function basemapStyle(pmtilesUrl, glyphsUrl) {
  // Self-hosted glyphs (frontend/public/fonts/), not a public font/tile
  // server - O-3's PROOF requires zero requests to any public server. Only
  // the "0-255" (basic Latin) range is fetched; English place names only.
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
      { id: "background", type: "background", paint: { "background-color": SURFACE } },
      {
        id: "water",
        type: "fill",
        source: "basemap",
        "source-layer": "water",
        paint: { "fill-color": WATER },
      },
      {
        id: "landuse",
        type: "fill",
        source: "basemap",
        "source-layer": "landuse",
        paint: { "fill-color": "#eceff1", "fill-opacity": 0.6 },
      },
      {
        id: "roads",
        type: "line",
        source: "basemap",
        "source-layer": "roads",
        filter: ["!=", ["get", "kind"], "path"],
        paint: { "line-color": "#d5d9de", "line-width": 0.6 },
      },
      {
        id: "boundaries",
        type: "line",
        source: "basemap",
        "source-layer": "boundaries",
        filter: ["!=", ["get", "disputed"], true],
        paint: { "line-color": INK_MUTED, "line-width": 1 },
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
        paint: { "circle-radius": 2, "circle-color": INK_MUTED },
      },
      {
        id: "places-labels",
        type: "symbol",
        source: "basemap",
        "source-layer": "places",
        minzoom: 4,
        // name:en - English only, matching the one glyph range self-hosted so far.
        layout: {
          "text-field": ["get", "name:en"],
          "text-font": ["Noto Sans Regular"],
          "text-size": 11,
          "text-offset": [0, 1],
          "text-anchor": "top",
        },
        paint: { "text-color": INK_MUTED, "text-halo-color": SURFACE, "text-halo-width": 1.2 },
      },
    ],
  };
}
