import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";
import { server } from "../test/mocks/server";
import { Dashboard } from "./Dashboard";

const FIXTURE_ITEM = {
  story_id: 1,
  title: "Mobilization reported near border",
  event_type: "military_event",
  facts: [{ text: "Convoy movement observed.", raw_item_ids: [101] }],
  analysis_text: "Multiple local accounts describe unusual convoy activity overnight.",
  probability_grade: 4,
  contrary_evidence: null,
  has_corroborating_artefact: true,
};

const FIXTURE_RAW_ITEMS = {
  101: {
    id: 101,
    source_name: "Al Jazeera",
    access_level: "direct",
    url: "https://example.com/item",
    fetched_at: "2026-09-06T08:00:00Z",
    original_lang: "Arabic",
    content_hash: "abc123",
    original_text: "نص عربي",
    working_text: "Arabic text",
  },
};

function renderDashboard() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>,
  );
}

function mockLoadedBrief() {
  server.use(
    http.get("/api/briefs", () =>
      HttpResponse.json([{ id: 1, type: "daily", for_date: "2026-09-06T00:00:00Z" }]),
    ),
    http.get("/api/briefs/1", () =>
      HttpResponse.json({
        id: 1,
        type: "daily",
        for_date: "2026-09-06T00:00:00Z",
        content: { items: [FIXTURE_ITEM], raw_items: FIXTURE_RAW_ITEMS },
        released_at: null,
      }),
    ),
  );
}

describe("Dashboard", () => {
  it("renders a loading skeleton before the briefs list resolves", () => {
    renderDashboard();
    expect(screen.getByRole("status", { name: "Loading" })).toBeInTheDocument();
  });

  it("renders the empty state when no brief has posted today", async () => {
    renderDashboard();
    expect(
      await screen.findByText("No brief yet today — the morning run posts around 09:00."),
    ).toBeInTheDocument();
  });

  it("renders the error state and can retry", async () => {
    server.use(http.get("/api/briefs", () => new HttpResponse(null, { status: 500 })));
    renderDashboard();
    expect(await screen.findByText("Couldn't load the daily brief.")).toBeInTheDocument();
  });

  it("renders today's brief from fixture, and a card expands headline -> facts -> analysis -> grade", async () => {
    mockLoadedBrief();
    const user = userEvent.setup();
    renderDashboard();

    const headline = await screen.findByText("Mobilization reported near border");
    expect(screen.queryByText("Convoy movement observed.")).not.toBeInTheDocument();

    await user.click(headline);

    await waitFor(() => expect(screen.getByText("Convoy movement observed.")).toBeInTheDocument());
    expect(screen.getByText(/Multiple local accounts describe unusual convoy activity/)).toBeInTheDocument();
    expect(screen.getByText("4 · Probably true")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Al Jazeera/ })).toBeInTheDocument();
  });
});
