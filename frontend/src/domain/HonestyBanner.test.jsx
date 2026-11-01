import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { Dashboard } from "../routes/Dashboard";
import { Incoming } from "../routes/Incoming";
import { capabilities } from "../test/fixtures";
import { server } from "../test/mocks/server";
import { HonestyBanner } from "./HonestyBanner";

// `capabilities` is captured from the real GET /capabilities over the dev seed
// (scripts/capture_frontend_fixtures.py): nothing collected, synthetic briefs present.
// The other states below are that real shape with flags flipped.
const TODAY = { ...capabilities, rss: true, telegram: true, triage_translation: true, synthetic_data_present: false };

function renderWith(node, caps) {
  if (caps) server.use(http.get("/api/capabilities", () => HttpResponse.json(caps)));
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{node}</MemoryRouter>
    </QueryClientProvider>,
  );
}

/** The banner once it has loaded (it says "Checking…" first). */
async function banner() {
  const el = await screen.findByRole("note", { name: "What MESG is doing today" });
  await waitFor(() => expect(el.textContent).not.toMatch(/^Checking/));
  return el;
}

describe("HonestyBanner (U-5)", () => {
  it("states today's real position in the order's words", async () => {
    renderWith(<HonestyBanner />, TODAY);
    expect(await screen.findByText(
      "Live feed: RSS + Telegram, machine triage translation. Not yet running: graded analysis, daily brief, alerts by email/SMS.",
    )).toBeInTheDocument();
  });

  it("over the dev seed alone, says nothing is collecting and the briefs are synthetic", async () => {
    renderWith(<HonestyBanner />);
    expect(await screen.findByText(
      "Not collecting yet. Not yet running: RSS, Telegram, machine triage translation, graded analysis, daily brief, " +
        "alerts by email/SMS. Briefs and grades on the Dashboard are synthetic dev-seed data, not analysis.",
    )).toBeInTheDocument();
  });

  it("changes on its own once the Analyst track lands: graded analysis moves to running", async () => {
    renderWith(<HonestyBanner />, { ...TODAY, graded_analysis: true });
    const text = (await banner()).textContent;
    expect(text).toContain("Live feed: RSS + Telegram, machine triage translation, graded analysis.");
    expect(text).toContain("Not yet running: daily brief, alerts by email/SMS.");
  });

  it("drops the 'not yet running' clause when everything runs", async () => {
    const all = Object.fromEntries(Object.keys(capabilities).map((k) => [k, k !== "synthetic_data_present"]));
    renderWith(<HonestyBanner />, all);
    expect((await banner()).textContent).not.toContain("Not yet running");
  });

  it("is never blank and never dismissable, even when the check fails", async () => {
    server.use(http.get("/api/capabilities", () => new HttpResponse(null, { status: 500 })));
    renderWith(<HonestyBanner />);
    expect(await screen.findByText("Couldn't check what MESG is running right now.")).toBeInTheDocument();
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("is on the Incoming page", async () => {
    server.use(http.get("/api/raw-items", () => HttpResponse.json({
      items: [], total: 0, awaiting_translation: 0, translation_failed: 0, silent_sources: [], max_id: null, newer_count: 0,
    })));
    renderWith(<Incoming />, TODAY);
    expect(await banner()).toHaveTextContent(/^Live feed: RSS \+ Telegram/);
  });

  it("is on the Dashboard, above the brief", async () => {
    renderWith(<Dashboard />, TODAY);
    expect(await banner()).toHaveTextContent(/^Live feed: RSS \+ Telegram/);
  });
});
