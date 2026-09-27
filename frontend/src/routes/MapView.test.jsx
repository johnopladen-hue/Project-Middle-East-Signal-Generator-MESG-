import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { geoItemsCentcom, regions } from "../test/fixtures";
import { server } from "../test/mocks/server";
import { MapView } from "./MapView";

// The exact file GET /regions/CENTCOM/polygon serves (backend/app/routers/regions.py) - not a
// stand-in. Read from disk rather than imported, so Vite's fs sandbox stays at its default.
// Vitest runs from frontend/ (locally and in CI's `working-directory: frontend`).
const centcomPolygon = JSON.parse(
  readFileSync(resolve(process.cwd(), "../backend/app/geo/aor_centcom.geojson"), "utf-8"),
);

/*
 * jsdom has no WebGL, so MapLibre cannot actually render here. This fake
 * records what MapView asks of the map - sources, layers, controls, markers,
 * popups - which is the contract this component owns. Whether real tiles and
 * glyphs paint is a browser check (PR #24), not something jsdom can prove.
 */
const fake = vi.hoisted(() => {
  const state = { maps: [], markers: [], protocols: { added: [], removed: [] } };

  class FakeMap {
    constructor(options) {
      this.options = options;
      this.sources = {};
      this.layers = [];
      this.controls = [];
      this.removed = false;
      state.maps.push(this);
    }
    addControl(control, position) {
      this.controls.push({ control, position });
    }
    isStyleLoaded() {
      return true;
    }
    once(_event, cb) {
      cb();
    }
    getSource(id) {
      return this.sources[id];
    }
    addSource(id, spec) {
      this.sources[id] = { ...spec, setData: (data) => (this.sources[id].data = data) };
    }
    addLayer(layer) {
      this.layers.push(layer);
    }
    remove() {
      this.removed = true;
    }
  }

  class FakeMarker {
    constructor({ element }) {
      this.element = element;
      this.removed = false;
      state.markers.push(this);
    }
    setLngLat(lngLat) {
      this.lngLat = lngLat;
      return this;
    }
    setPopup(popup) {
      this.popup = popup;
      return this;
    }
    addTo(map) {
      this.map = map;
      return this;
    }
    remove() {
      this.removed = true;
    }
  }

  class FakePopup {
    setDOMContent(node) {
      this.node = node;
      return this;
    }
  }

  class FakeControl {
    constructor(options) {
      this.options = options;
    }
  }

  return { state, FakeMap, FakeMarker, FakePopup, FakeControl };
});

vi.mock("maplibre-gl", () => ({
  Map: fake.FakeMap,
  Marker: fake.FakeMarker,
  Popup: fake.FakePopup,
  AttributionControl: class AttributionControl extends fake.FakeControl {},
  NavigationControl: class NavigationControl extends fake.FakeControl {},
  addProtocol: (name) => fake.state.protocols.added.push(name),
  removeProtocol: (name) => fake.state.protocols.removed.push(name),
}));
vi.mock("maplibre-gl/dist/maplibre-gl.css", () => ({}));
vi.mock("pmtiles", () => ({ Protocol: class Protocol { tile() {} } }));

function LocationProbe() {
  const location = useLocation();
  return <p data-testid="location">{location.pathname}</p>;
}

function serveMapApis({ notes = [] } = {}) {
  const posted = [];
  server.use(
    http.get("/api/regions", () => HttpResponse.json(regions)),
    http.get("/api/regions/:aor/polygon", ({ params }) =>
      params.aor === "CENTCOM"
        ? HttpResponse.json(centcomPolygon)
        : HttpResponse.json({ detail: "No polygon" }, { status: 404 }),
    ),
    http.get("/api/geo/items", () => HttpResponse.json(geoItemsCentcom)),
    http.get("/api/frame-divergence-notes", () => HttpResponse.json([...posted].reverse().concat(notes))),
    http.post("/api/frame-divergence-notes", async ({ request }) => {
      const body = await request.json();
      // Mirrors backend create_note: echoes the payload, server-assigned id/timestamp/author.
      const note = { id: posted.length + 1, ...body, created_at: new Date().toISOString(), created_by: "analyst" };
      posted.push(note);
      return HttpResponse.json(note, { status: 201 });
    }),
  );
  return posted;
}

function renderMap() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/map"]}>
        <Routes>
          <Route path="/map" element={<MapView />} />
          <Route path="*" element={<LocationProbe />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

const located = geoItemsCentcom.located.features;

describe("MapView (D-014, D-015)", () => {
  beforeEach(() => {
    document.body.replaceChildren(); // drop popup nodes a previous test attached
    fake.state.maps.length = 0;
    fake.state.markers.length = 0;
    fake.state.protocols.added.length = 0;
    fake.state.protocols.removed.length = 0;
  });

  it("labels the region layer as a U.S. command frame, not neutral geography", async () => {
    serveMapApis();
    renderMap();
    expect(
      screen.getByText("U.S. command frame (Unified Command Plan) — not neutral geography"),
    ).toBeInTheDocument();
  });

  it("offers every AOR but only enables the ones with data, and says why the rest are disabled", async () => {
    serveMapApis();
    renderMap();

    const centcom = await screen.findByRole("button", { name: "CENTCOM" });
    expect(centcom).toBeEnabled();

    for (const region of regions.filter((r) => !r.has_data)) {
      const button = screen.getByRole("button", { name: region.code });
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute("title", `${region.label} — not yet built`);
    }
  });

  it("builds the map from the self-hosted basemap and glyphs, framed on the full CENTCOM AOR, with attribution shown", () => {
    serveMapApis();
    renderMap();

    const [map] = fake.state.maps;
    expect(fake.state.protocols.added).toContain("pmtiles");
    expect(map.options.bounds).toEqual([
      [23.5, 11],
      [88.5, 56.5],
    ]);

    // Nothing points at a third-party tile or font server (D-014).
    const style = JSON.stringify(map.options.style);
    expect(style).toContain(`${window.location.origin}/basemap/centcom.pmtiles`);
    expect(style).toContain(`${window.location.origin}/fonts/{fontstack}/{range}.pbf`);

    // ODbL requires visible OSM attribution: a non-compact AttributionControl must be added.
    const attribution = map.controls.find((c) => c.control.constructor.name === "AttributionControl");
    expect(attribution).toBeDefined();
    expect(attribution.control.options).toEqual({ compact: false });
  });

  it("overlays the real CENTCOM polygon as a fill + outline", async () => {
    serveMapApis();
    renderMap();

    const [map] = fake.state.maps;
    await waitFor(() => expect(map.sources.aor).toBeDefined());
    expect(map.sources.aor.data).toEqual(centcomPolygon);
    expect(map.layers.map((l) => l.id)).toEqual(["aor-fill", "aor-outline"]);
  });

  it("places exactly one marker per located item, at the API's coordinates, named for screen readers", async () => {
    serveMapApis();
    renderMap();

    await waitFor(() => expect(fake.state.markers).toHaveLength(located.length));
    located.forEach((feature, i) => {
      const marker = fake.state.markers[i];
      expect(marker.lngLat).toEqual(feature.geometry.coordinates);
      expect(marker.element).toHaveAttribute("aria-label", feature.properties.title);
    });
  });

  it("deep-links a marker's call-out to the item's existing detail route via SPA navigation", async () => {
    serveMapApis();
    renderMap();

    await waitFor(() => expect(fake.state.markers).toHaveLength(located.length));
    for (const kind of ["story", "organization"]) {
      const index = located.findIndex((f) => f.properties.kind === kind);
      expect(index).toBeGreaterThanOrEqual(0); // guard: captured data still has both kinds
      const { detail_url: detailUrl, precision } = located[index].properties;
      const popupNode = fake.state.markers[index].popup.node;
      document.body.append(popupNode); // what MapLibre does when the popup opens

      expect(within(popupNode).getByText(`${kind} · ${precision} precision`)).toBeInTheDocument();
      const link = within(popupNode).getByRole("link", { name: "Open detail →" });
      expect(link).toHaveAttribute("href", detailUrl);
    }

    // Clicking navigates in-app to the detail route, and the browser's own full-page
    // navigation is suppressed (jsdom never performs it, so assert it was prevented).
    const storyIndex = located.findIndex((f) => f.properties.kind === "story");
    const link = within(fake.state.markers[storyIndex].popup.node).getByRole("link");
    let defaultPrevented = null;
    link.addEventListener("click", (event) => {
      defaultPrevented = event.defaultPrevented;
    });
    await userEvent.click(link);
    expect(defaultPrevented).toBe(true);
    expect(await screen.findByTestId("location")).toHaveTextContent(located[storyIndex].properties.detail_url);
  });

  it("never drops unlocated items: the tray reports the count against the reconciled total and lists them (A-007)", async () => {
    serveMapApis();
    renderMap();

    const { unlocated, reconciliation } = geoItemsCentcom;
    expect(reconciliation.total).toBe(reconciliation.located_count + reconciliation.unlocated_count);

    expect(await screen.findByText(`Unlocated: ${unlocated.count} of ${reconciliation.total}`)).toBeInTheDocument();
    for (const item of unlocated.items) {
      expect(screen.getByText(item.title)).toBeInTheDocument();
    }
  });

  it("says when no frame-divergence notes exist for the region, rather than rendering nothing", async () => {
    serveMapApis();
    renderMap();
    expect(await screen.findByText("No divergence notes recorded for CENTCOM yet.")).toBeInTheDocument();
  });

  it("records a frame-divergence note scoped to the selected region, then shows it and clears the field", async () => {
    const posted = serveMapApis();
    renderMap();
    await screen.findByText("No divergence notes recorded for CENTCOM yet.");

    const field = screen.getByPlaceholderText("Where does in-region self-conception diverge from this frame?");
    await userEvent.type(field, "Test note: framing comparison pending");
    await userEvent.click(screen.getByRole("button", { name: "Record" }));

    await waitFor(() => expect(posted).toHaveLength(1));
    expect(posted[0]).toMatchObject({ scope_type: "region", scope_id: "CENTCOM" });
    expect(await screen.findByText("Test note: framing comparison pending")).toBeInTheDocument();
    expect(screen.getByText("— analyst")).toBeInTheDocument();
    expect(field).toHaveValue("");
  });

  it("does not post a blank note", async () => {
    const posted = serveMapApis();
    renderMap();
    await screen.findByText("No divergence notes recorded for CENTCOM yet.");

    await userEvent.type(
      screen.getByPlaceholderText("Where does in-region self-conception diverge from this frame?"),
      "   ",
    );
    await userEvent.click(screen.getByRole("button", { name: "Record" }));
    expect(posted).toHaveLength(0);
  });

  it("tears down the map, its markers and the pmtiles protocol on unmount", async () => {
    serveMapApis();
    const { unmount } = renderMap();
    await waitFor(() => expect(fake.state.markers).toHaveLength(located.length));

    unmount();
    expect(fake.state.maps[0].removed).toBe(true);
    expect(fake.state.markers.every((m) => m.removed)).toBe(true);
    expect(fake.state.protocols.removed).toContain("pmtiles");
  });
});
