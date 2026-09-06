import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { server } from "../test/mocks/server";
import { Story } from "./Story";

const FIXTURE_STORY = {
  id: 42,
  title: "Convoy movement reported near border",
  event_type: "military_event",
  status: "open",
  facts: [{ text: "Convoy observed overnight.", raw_item_ids: [101] }],
  analysis_text: "Multiple local accounts describe convoy movement.",
  probability_grade: 2,
  contrary_evidence: "Satellite imagery from the same window shows no unusual activity.",
  has_corroborating_artefact: false,
  source_assessments: [
    { source_id: 1, source_name: "Al Jazeera", access_level: "direct", reliability: 0.8, rationale: "On-ground stringer." },
  ],
  divergence: {
    in_region_summary: "Local voices describe heightened military activity.",
    english_media_summary: "English outlets have not covered this yet.",
    divergence_points: ["English media silent so far"],
    convergence_points: ["Both note border tension"],
  },
  raw_items: {
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
  },
  timeline: [101],
};

function renderStory() {
  server.use(http.get("/api/stories/42", () => HttpResponse.json(FIXTURE_STORY)));
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/stories/42"]}>
        <Routes>
          <Route path="/stories/:id" element={<Story />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Story detail", () => {
  it("shows the divergence panel with both summaries and the divergence/convergence lists", async () => {
    renderStory();
    expect(await screen.findByText(/Local voices describe heightened military activity/)).toBeInTheDocument();
    expect(screen.getByText(/English outlets have not covered this yet/)).toBeInTheDocument();
    expect(screen.getByText(/English media silent so far/)).toBeInTheDocument();
    expect(screen.getByText(/Both note border tension/)).toBeInTheDocument();
  });

  it("reaches every fact's raw item in one click", async () => {
    renderStory();
    const user = userEvent.setup();
    // The fixture's one raw item legitimately appears twice: once cited by
    // the fact, once in the related-items timeline. Either chip proves the
    // one-hop requirement, so click the first.
    const [chip] = await screen.findAllByRole("button", { name: /Al Jazeera/ });

    await user.click(chip);

    expect(screen.getByText("نص عربي")).toBeInTheDocument();
    expect(screen.getByText("Arabic text")).toBeInTheDocument();
  });

  it("shows the grade with its contrary evidence", async () => {
    renderStory();
    expect(await screen.findByText(/Satellite imagery from the same window shows no unusual activity/)).toBeInTheDocument();
  });

  it("renders the source assessment table", async () => {
    renderStory();
    expect(await screen.findByText("On-ground stringer.")).toBeInTheDocument();
    expect(screen.getByText("80%")).toBeInTheDocument();
  });
});
