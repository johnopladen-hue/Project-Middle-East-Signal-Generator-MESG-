import { readdirSync } from "node:fs";
import { resolve } from "node:path";
import { createExpression, validateStyleMin } from "@maplibre/maplibre-gl-style-spec";
import { describe, expect, it } from "vitest";
import { BASEMAP_MAX_ZOOM, LABEL, basemapStyle } from "./basemapStyle";

const style = basemapStyle("http://localhost/basemap/centcom.pmtiles", "http://localhost/fonts/{fontstack}/{range}.pbf");
const layer = (id) => style.layers.find((l) => l.id === id);

// Property values below are copied from features in public/basemap/centcom.pmtiles
// (decoded 2026-10-11), including Türkiye's real one-letter `name:en`.
function label(properties) {
  const parsed = createExpression(LABEL, { type: "string" });
  if (parsed.result !== "success") throw new Error(JSON.stringify(parsed.value));
  return parsed.value.evaluate({ zoom: 4 }, { type: "Point", properties });
}

describe("basemapStyle (D-014 map legibility)", () => {
  it("is a valid MapLibre style", () => {
    expect(validateStyleMin(style)).toEqual([]);
  });

  it("uses the English name when the data has a real one", () => {
    expect(label({ name: "سوريا", "name:en": "Syria" })).toBe("Syria");
  });

  it("falls back to the local name when the English name is a single letter (Türkiye's real data defect)", () => {
    expect(label({ name: "Türkiye", "name:en": "T" })).toBe("Türkiye");
  });

  it("falls back to the local name when there is no English name", () => {
    expect(label({ name: "Surat" })).toBe("Surat");
  });

  it("draws land from the extract's earth layer, distinct from the sea", () => {
    expect(layer("earth").paint["fill-color"]).not.toBe(layer("background").paint["background-color"]);
  });

  it("labels countries from the opening whole-AOR view, not only from zoom 4", () => {
    expect(layer("country-labels").minzoom).toBeUndefined();
  });

  it("caps zoom within one level and a half of the z5 tiles", () => {
    expect(BASEMAP_MAX_ZOOM).toBeGreaterThan(5);
    expect(BASEMAP_MAX_ZOOM).toBeLessThanOrEqual(6.5);
  });

  it("has every glyph range self-hosted that the labels need", () => {
    const ranges = readdirSync(resolve(__dirname, "../../public/fonts/Noto Sans Regular"));
    expect(ranges).toEqual(expect.arrayContaining(["0-255.pbf", "256-511.pbf", "512-767.pbf", "1024-1279.pbf"]));
  });
});
