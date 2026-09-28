import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";
import { server } from "../test/mocks/server";
import { Incoming } from "./Incoming";

const BASE_PAGE = {
  total: 2,
  awaiting_translation: 1,
  silent_sources: [],
};

function renderIncoming() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <Incoming />
    </QueryClientProvider>,
  );
}

describe("Incoming (D-018, I-5/S-5)", () => {
  it("renders Arabic items right-to-left and English items left-to-right", async () => {
    server.use(
      http.get("/api/raw-items", () =>
        HttpResponse.json({
          ...BASE_PAGE,
          items: [
            {
              id: 1,
              source_id: 1,
              source_name: "Al Jazeera Arabic",
              kind: "rss",
              source_class: "native",
              pair_id: null,
              designation_note: null,
              verification_note: null,
              fetched_at: new Date().toISOString(),
              published_at: null,
              original_lang: "ar",
              original_text: "مرحبا بالعالم",
              working_text: null,
              url: "https://example.test/ar",
            },
            {
              id: 2,
              source_id: 2,
              source_name: "NPR World",
              kind: "rss",
              source_class: "english_comparison",
              pair_id: null,
              designation_note: null,
              verification_note: null,
              fetched_at: new Date().toISOString(),
              published_at: null,
              original_lang: "en",
              original_text: "Hello world",
              working_text: null,
              url: "https://example.test/en",
            },
          ],
        }),
      ),
    );
    renderIncoming();

    const arabic = await screen.findByText("مرحبا بالعالم");
    expect(arabic).toHaveAttribute("dir", "rtl");
    expect(arabic).toHaveAttribute("lang", "ar");

    const english = await screen.findByText("Hello world");
    expect(english).toHaveAttribute("dir", "ltr");
    expect(english).toHaveAttribute("lang", "en");
  });

  it("shows class, pair, designated and authenticity-unconfirmed badges", async () => {
    server.use(
      http.get("/api/raw-items", () =>
        HttpResponse.json({
          ...BASE_PAGE,
          total: 1,
          items: [
            {
              id: 3,
              source_id: 3,
              source_name: "Al-Manar",
              kind: "rss",
              source_class: "native",
              pair_id: "almanar",
              designation_note: "Hezbollah-owned. US SDGT (2006).",
              verification_note: "AUTHENTICITY UNCONFIRMED - included by Owner ruling.",
              fetched_at: new Date().toISOString(),
              published_at: null,
              original_lang: "ar",
              original_text: "بيان",
              working_text: null,
              url: "https://example.test/almanar",
            },
          ],
        }),
      ),
    );
    renderIncoming();

    const card = (await screen.findByText("Al-Manar")).closest("div").parentElement;
    expect(within(card).getByText("native")).toBeInTheDocument();
    expect(within(card).getByText("Pair: almanar")).toBeInTheDocument();
    expect(within(card).getByText("Designated")).toBeInTheDocument();
    expect(within(card).getByText("Authenticity unconfirmed")).toBeInTheDocument();
  });

  it("shows the empty state with the run command", async () => {
    server.use(
      http.get("/api/raw-items", () =>
        HttpResponse.json({ items: [], total: 0, awaiting_translation: 0, silent_sources: [] }),
      ),
    );
    renderIncoming();

    expect(await screen.findByText(/No items collected yet/)).toBeInTheDocument();
    expect(screen.getByText("python -m app.ingest --once")).toBeInTheDocument();
  });

  it("shows an error state with retry on failure", async () => {
    server.use(http.get("/api/raw-items", () => new Response(null, { status: 500 })));
    renderIncoming();

    expect(await screen.findByText("Couldn't load incoming items.")).toBeInTheDocument();
  });

  it("shows the honesty line naming silent sources", async () => {
    server.use(
      http.get("/api/raw-items", () =>
        HttpResponse.json({
          items: [],
          total: 0,
          awaiting_translation: 0,
          silent_sources: ["Fars News Agency", "IRNA"],
        }),
      ),
    );
    renderIncoming();

    expect(await screen.findByText(/Fars News Agency, IRNA/)).toBeInTheDocument();
  });
});
