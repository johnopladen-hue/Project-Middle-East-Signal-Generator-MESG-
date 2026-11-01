import { screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { rawItemDetailLocated, rawItemDetailUnlocated } from "../test/fixtures";
import { server } from "../test/mocks/server";
import { renderWithProviders } from "../test/renderWithProviders";
import { IncomingItem } from "./IncomingItem";

function renderItem(item, state) {
  server.use(http.get(`/api/raw-items/${item.id}`, () => HttpResponse.json(item)));
  return renderWithProviders(
    <Routes>
      <Route path="/incoming/:id" element={<IncomingItem />} />
    </Routes>,
    { route: { pathname: `/incoming/${item.id}`, state } },
  );
}

describe("IncomingItem (D-023)", () => {
  it("shows the item's original text and where the map put it, with the words that put it there", async () => {
    renderItem(rawItemDetailLocated);
    const { location } = rawItemDetailLocated;
    expect(await screen.findByText(location.place_name)).toBeInTheDocument();
    expect(screen.getByText(`“${location.matched_text}”`)).toBeInTheDocument();
    expect(screen.getByText(/Machine-matched, not verified/)).toBeInTheDocument();
    expect(screen.getByText(rawItemDetailLocated.original_text.split("\n")[0], { exact: false })).toBeInTheDocument();
  });

  it("says plainly when the text named no place, so the item is not on the map", async () => {
    renderItem(rawItemDetailUnlocated);
    expect(await screen.findByText(/No place name found in the original text/)).toBeInTheDocument();
  });

  it("links back to the map when opened from a map dot", async () => {
    renderItem(rawItemDetailLocated, { from: "map" });
    expect(await screen.findByRole("link", { name: "Back to the map" })).toHaveAttribute("href", "/map");
  });
});
