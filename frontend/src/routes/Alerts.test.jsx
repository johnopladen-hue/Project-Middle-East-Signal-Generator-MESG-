import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { server } from "../test/mocks/server";
import { Alerts } from "./Alerts";

const FIXTURE_SIGNAL = {
  id: 7,
  story_id: 1,
  story_title: "Border tension escalates",
  type: "military_event",
  severity: "critical",
  is_imminent: true,
  status: "new",
  created_at: "2026-09-06T09:00:00Z",
};

function renderAlerts() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <Alerts />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Alerts", () => {
  it("renders the empty state when no signals match", async () => {
    server.use(http.get("/api/signals", () => HttpResponse.json([])));
    renderAlerts();
    expect(await screen.findByText("No alerts match these filters.")).toBeInTheDocument();
  });

  it("renders a signal row with severity, imminent pill, and event type", async () => {
    server.use(http.get("/api/signals", () => HttpResponse.json([FIXTURE_SIGNAL])));
    renderAlerts();
    expect(await screen.findByText("Border tension escalates")).toBeInTheDocument();
    expect(screen.getByText("Critical")).toBeInTheDocument();
    expect(screen.getByText("Imminent")).toBeInTheDocument();
  });
});
