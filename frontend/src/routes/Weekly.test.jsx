import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { server } from "../test/mocks/server";
import { Weekly } from "./Weekly";

const WEEKLIES = [
  { id: 2, type: "weekly", for_date: "2026-09-06T00:00:00Z" },
  { id: 1, type: "weekly", for_date: "2026-08-30T00:00:00Z" },
];

function briefDetail(id, title) {
  return {
    id,
    type: "weekly",
    for_date: WEEKLIES.find((w) => w.id === id).for_date,
    content: { title, body: `Body of weekly ${id}.` },
    released_at: null,
  };
}

function renderWeekly(initialPath = "/weekly") {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialPath]}>
        <Routes>
          <Route path="/weekly" element={<Weekly />} />
          <Route path="/weekly/:id" element={<Weekly />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Weekly", () => {
  it("renders the empty state when no weekly summary exists yet", async () => {
    server.use(http.get("/api/briefs", () => HttpResponse.json([])));
    renderWeekly();
    expect(
      await screen.findByText("No weekly summary yet — the first lands this Friday afternoon."),
    ).toBeInTheDocument();
  });

  it("renders the error state and can retry", async () => {
    server.use(http.get("/api/briefs", () => new HttpResponse(null, { status: 500 })));
    renderWeekly();
    expect(await screen.findByText("Couldn't load the weekly summaries.")).toBeInTheDocument();
  });

  it("renders the latest weekly by default", async () => {
    server.use(
      http.get("/api/briefs", () => HttpResponse.json(WEEKLIES)),
      http.get("/api/briefs/2", () => HttpResponse.json(briefDetail(2, "What mattered this week"))),
    );
    renderWeekly();
    expect(await screen.findByText("What mattered this week")).toBeInTheDocument();
    expect(screen.getByText("Body of weekly 2.")).toBeInTheDocument();
  });

  it("loads a past weekly by id", async () => {
    server.use(
      http.get("/api/briefs", () => HttpResponse.json(WEEKLIES)),
      http.get("/api/briefs/1", () => HttpResponse.json(briefDetail(1, "Last week's summary"))),
    );
    renderWeekly("/weekly/1");
    expect(await screen.findByText("Last week's summary")).toBeInTheDocument();
    expect(screen.getByText("Body of weekly 1.")).toBeInTheDocument();
  });
});
