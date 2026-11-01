import {
  AttributionControl,
  Map as MapLibreMap,
  Marker,
  NavigationControl,
  addProtocol,
  removeProtocol,
  setWorkerUrl,
} from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import maplibreWorkerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url";
import { Protocol } from "pmtiles";
import PropTypes from "prop-types";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/primitives/Button";
import { Card } from "../components/primitives/Card";
import { ErrorState } from "../components/primitives/ErrorState";
import { Skeleton } from "../components/primitives/Skeleton";
import { BASEMAP_MAX_ZOOM, basemapStyle } from "../map/basemapStyle";
import { useCreateFrameDivergenceNote, useFrameDivergenceNotes, useGeoItems, useRegionPolygon, useRegions } from "../domain/useGeo";

const CENTCOM_BOUNDS = [
  [23.5, 11],
  [88.5, 56.5],
]; // the extracted basemap's own bbox: full 22-country CENTCOM AOR + margin (D-014/D-015, findings.md 2026-09-27)

// MapLibre does all tile decoding in a Web Worker it locates relative to its
// own module. When Vite pre-bundles maplibre-gl into node_modules/.vite/deps/
// (which Vite 8 did on 2026-09-28 despite `optimizeDeps.exclude`), that
// relative URL 404s and the map silently shows only the background and DOM
// markers (findings.md, 2026-10-11). Pointing MapLibre at the real worker file
// through Vite's `?worker&url` import (which bundles the worker together with
// the shared chunk it imports) works in dev and in a production build.
setWorkerUrl(maplibreWorkerUrl);

const PRECISION_RADIUS = { point: 5, city: 5, province: 6, country: 7 };
// News items (D-023) in the accent red so real collected items stand apart from the synthetic stories.
const MARKER_COLOR = { story: "#c8912a", organization: "#0e6e77", item: "#b42318" };

/** What the red dots are (D-023): how many are shown of how many placed, and how they were placed. */
function NewsCaption({ summary }) {
  return (
    <Card className="absolute right-14 top-4 max-w-xs">
      <p className="flex items-center gap-2 text-xs font-semibold text-ink">
        <span aria-hidden="true" className="inline-block h-2.5 w-2.5 rounded-full" style={{ background: MARKER_COLOR.item }} />
        News: {summary.shown} most recent of {summary.located_in_aor} placed (last {summary.window_hours}h)
      </p>
      <p className="mt-1 text-xs text-ink-muted">
        Placed where the item&apos;s original text names a place, city-level first. Machine-matched, not verified.{" "}
        {summary.not_located} items named no place and are not shown.
      </p>
    </Card>
  );
}

NewsCaption.propTypes = {
  summary: PropTypes.shape({
    shown: PropTypes.number.isRequired,
    located_in_aor: PropTypes.number.isRequired,
    window_hours: PropTypes.number.isRequired,
    not_located: PropTypes.number.isRequired,
  }).isRequired,
};

/** Geographic map view (D-014/D-015, O-3/O-4/O-6/O-8/O-9): self-hosted
 * basemap, CENTCOM AOR labeled as the U.S. command lens, located-item
 * call-outs deep-linking to existing detail, an unlocated tray, and a
 * recordable frame-divergence note. */
export function MapView() {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const navigate = useNavigate();

  const [selectedAor, setSelectedAor] = useState("CENTCOM");
  const [noteText, setNoteText] = useState("");

  const regionsQuery = useRegions();
  const polygonQuery = useRegionPolygon(selectedAor);
  const geoQuery = useGeoItems(selectedAor);
  const notesQuery = useFrameDivergenceNotes("region", selectedAor);
  const createNote = useCreateFrameDivergenceNote("region", selectedAor);

  useEffect(() => {
    if (mapRef.current || !mapContainerRef.current) return;

    const protocol = new Protocol();
    addProtocol("pmtiles", protocol.tile);

    const map = new MapLibreMap({
      container: mapContainerRef.current,
      style: basemapStyle(
        `${window.location.origin}/basemap/centcom.pmtiles`,
        `${window.location.origin}/fonts/{fontstack}/{range}.pbf`,
      ),
      bounds: CENTCOM_BOUNDS,
      maxZoom: BASEMAP_MAX_ZOOM, // the tiles stop at z5; deeper zoom only stretches them
      attributionControl: false,
    });
    map.addControl(
      new AttributionControl({ compact: false, customAttribution: "Item places: © GeoNames (CC BY 4.0)" }),
    );
    map.addControl(new NavigationControl(), "top-right");
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
      removeProtocol("pmtiles");
    };
  }, []);

  // AOR polygon overlay - a translucent fill + outline, added/updated once the map and data are ready.
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !polygonQuery.data) return;

    const apply = () => {
      if (map.getSource("aor")) {
        map.getSource("aor").setData(polygonQuery.data);
        return;
      }
      map.addSource("aor", { type: "geojson", data: polygonQuery.data });
      map.addLayer({ id: "aor-fill", type: "fill", source: "aor", paint: { "fill-color": "#0e6e77", "fill-opacity": 0.08 } });
      map.addLayer({ id: "aor-outline", type: "line", source: "aor", paint: { "line-color": "#0e6e77", "line-width": 1.5 } });
    };

    if (map.isStyleLoaded()) apply();
    else map.once("load", apply);
  }, [polygonQuery.data]);

  // One dot per located Story/Organization and per placed news item (D-023).
  // Clicking a dot goes straight to its detail page; hovering shows its title.
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !geoQuery.data) return;

    const features = [...geoQuery.data.located.features, ...(geoQuery.data.news_items?.features ?? [])];
    const markers = features.map((feature) => {
      const [lon, lat] = feature.geometry.coordinates;
      const { title, precision, detail_url: detailUrl, kind, place_name: placeName } = feature.properties;
      const label = kind === "item" ? `${title} — ${placeName}` : title;

      const el = document.createElement("button");
      el.type = "button";
      el.setAttribute("aria-label", label);
      el.title = label;
      el.style.width = `${(PRECISION_RADIUS[precision] ?? 5) * 2}px`;
      el.style.height = `${(PRECISION_RADIUS[precision] ?? 5) * 2}px`;
      el.style.borderRadius = "50%";
      el.style.border = "2px solid white";
      el.style.background = MARKER_COLOR[kind] ?? MARKER_COLOR.story;
      el.style.cursor = "pointer";
      el.style.padding = 0;
      el.addEventListener("click", (event) => {
        event.stopPropagation();
        navigate(detailUrl, { state: { from: "map" } });
      });

      return new Marker({ element: el }).setLngLat([lon, lat]).addTo(map);
    });

    return () => markers.forEach((m) => m.remove());
  }, [geoQuery.data, navigate]);

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-rule bg-surface-raised px-4 py-2">
        <div>
          <span className="text-sm font-semibold text-ink">Map</span>
          <span className="ml-2 rounded border border-rule px-2 py-0.5 text-xs text-ink-muted">
            U.S. command frame (Unified Command Plan) — not neutral geography
          </span>
        </div>
        <div className="flex flex-wrap gap-1">
          {(regionsQuery.data ?? []).map((region) => (
            <button
              key={region.code}
              type="button"
              disabled={!region.has_data}
              onClick={() => setSelectedAor(region.code)}
              title={region.has_data ? region.label : `${region.label} — not yet built`}
              className={`rounded px-2 py-1 text-xs
                ${region.code === selectedAor ? "bg-accent text-white" : "text-ink-muted"}
                ${region.has_data ? "hover:bg-accent-weak" : "cursor-not-allowed opacity-40"}`}
            >
              {region.code}
            </button>
          ))}
        </div>
      </div>

      <div className="relative flex-1">
        <div ref={mapContainerRef} className="h-full w-full" />

        {geoQuery.data?.news_items ? <NewsCaption summary={geoQuery.data.news_items.summary} /> : null}

        {geoQuery.data ? (
          <Card className="absolute bottom-4 left-4 max-w-xs">
            <p className="text-xs font-semibold text-ink">
              Unlocated: {geoQuery.data.unlocated.count} of {geoQuery.data.reconciliation.total}
            </p>
            <ul className="mt-1 max-h-32 space-y-1 overflow-y-auto text-xs text-ink-muted">
              {geoQuery.data.unlocated.items.map((item) => (
                <li key={`${item.kind}-${item.id}`}>{item.title}</li>
              ))}
            </ul>
          </Card>
        ) : null}
      </div>

      <div className="border-t border-rule bg-surface-raised p-4">
        <h2 className="mb-2 text-sm font-semibold text-ink">
          Frame divergence — {selectedAor}
        </h2>
        {notesQuery.isLoading ? (
          <Skeleton lines={2} />
        ) : notesQuery.isError ? (
          <ErrorState message="Couldn't load frame-divergence notes." onRetry={() => notesQuery.refetch()} />
        ) : (
          <ul className="mb-2 space-y-1 text-sm text-ink">
            {(notesQuery.data ?? []).map((note) => (
              <li key={note.id} className="border-l-2 border-rule pl-2">
                {note.text}
                <span className="ml-2 text-xs text-ink-muted">— {note.created_by}</span>
              </li>
            ))}
            {(notesQuery.data ?? []).length === 0 ? (
              <li className="text-xs text-ink-muted">No divergence notes recorded for {selectedAor} yet.</li>
            ) : null}
          </ul>
        )}
        <form
          className="flex gap-2"
          onSubmit={(event) => {
            event.preventDefault();
            if (!noteText.trim()) return;
            createNote.mutate(noteText, { onSuccess: () => setNoteText("") });
          }}
        >
          <textarea
            value={noteText}
            onChange={(event) => setNoteText(event.target.value)}
            placeholder="Where does in-region self-conception diverge from this frame?"
            rows={2}
            className="flex-1 rounded-md border border-rule px-3 py-2 text-sm
              focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
          />
          <Button type="submit" busy={createNote.isPending}>
            Record
          </Button>
        </form>
      </div>
    </div>
  );
}
