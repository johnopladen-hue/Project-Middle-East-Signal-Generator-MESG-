/** Neutral MapLibre style over the self-hosted Levant PMTiles extract
 * (D-014). Disputed boundaries render distinctly (O-4) - the vector data's
 * own `disputed` field, not a manual overlay (see findings.md). Palette
 * reuses the app's own design tokens (frontend/src/index.css). */

const INK_MUTED = "#5b626e";
const SURFACE = "#f7f8fa";
const WATER = "#c9d6de";
const DISPUTED = "#c8912a"; // grade-3 amber - "flagged/uncertain", not a verdict

export function basemapStyle(pmtilesUrl) {
  // No `glyphs` URL: label text needs a self-hosted glyph server we don't
  // have yet, and O-3's PROOF requires zero requests to any public server
  // (verified in the network panel with the internet off) - so this first
  // cut renders no text labels rather than reaching out for fonts.
  return {
    version: 8,
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
    ],
  };
}
