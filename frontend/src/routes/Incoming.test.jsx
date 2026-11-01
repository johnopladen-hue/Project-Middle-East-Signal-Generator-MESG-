import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { describe, expect, it, vi } from "vitest";
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

  // U-2 (D-016): genuine collected posts (Al Jazeera Mubasher 510450, BBC Persian
  // 293180) with the real NLLB-200 output the local model produced for them.
  const TRANSLATED_ITEM = {
    id: 10,
    source_id: 10,
    source_name: "Al Jazeera Mubasher",
    kind: "telegram",
    source_class: "native",
    pair_id: null,
    designation_note: null,
    verification_note: null,
    fetched_at: "2026-10-11T15:30:00Z",
    published_at: "2026-10-11T14:38:36Z",
    original_lang: "ar",
    original_text: "عاجل | المتحدث باسم التحالف: اعتداء بمقذوف مجهول على صالة المسافرين رقم 4 بمطار الملك خالد الدولي",
    working_text:
      "Coalition spokesman: An unknown assault on passenger lounge number four at King Khalid International Airport.",
    translation: { status: "ok", engine: "nllb-200-distilled-600M-ct2-int8", src_code: "arb_Arab" },
    url: "https://t.me/ajmubasher/510450",
  };

  function serveItems(items, extra = {}) {
    server.use(
      http.get("/api/raw-items", () =>
        HttpResponse.json({ ...BASE_PAGE, translation_failed: 0, total: items.length, items, ...extra }),
      ),
    );
  }

  it("labels a translated line as unverified machine triage and shows the original beneath it", async () => {
    serveItems([TRANSLATED_ITEM]);
    renderIncoming();

    const english = await screen.findByText(TRANSLATED_ITEM.working_text);
    const original = screen.getByText(TRANSLATED_ITEM.original_text);
    expect(screen.getByText("Machine triage translation (NLLB-200), not verified")).toBeInTheDocument();
    expect(english.compareDocumentPosition(original) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(english).toHaveAttribute("lang", "en");
  });

  it("marks a truncated translation as first part only", async () => {
    serveItems([
      {
        ...TRANSLATED_ITEM,
        id: 11,
        source_name: "BBC Persian",
        original_lang: "fa",
        original_text: "🔻 ترامپ: روسیه و اوکراین با «آتش‌بس زیرساخت‌های انرژی» موافقت کردند",
        working_text: "Trump: Russia and Ukraine agreed to a ceasefire on energy infrastructure",
        translation: { status: "ok_truncated", engine: "nllb-200-distilled-600M-ct2-int8", src_code: "pes_Arab" },
      },
    ]);
    renderIncoming();

    expect(await screen.findByText(/first part only/)).toBeInTheDocument();
  });

  it("says translation failed and still shows the original, never a blank", async () => {
    serveItems([
      {
        ...TRANSLATED_ITEM,
        id: 12,
        working_text: null,
        translation: { status: "failed", engine: "nllb-200-distilled-600M-ct2-int8", src_code: "arb_Arab" },
      },
    ]);
    renderIncoming();

    expect(await screen.findByText(/Translation failed/)).toBeInTheDocument();
    expect(screen.getByText(TRANSLATED_ITEM.original_text)).toBeInTheDocument();
    expect(screen.queryByText(/Awaiting translation/)).not.toBeInTheDocument();
  });

  it("counts failed translations in the honesty line", async () => {
    serveItems([], { translation_failed: 4 });
    renderIncoming();

    expect(await screen.findByText(/4 translation failed/)).toBeInTheDocument();
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

// --- U-4: search, quick filters, time window, auto-refresh -------------------
// Same genuine post as above (Al Jazeera Mubasher 510450) and its real NLLB output.
const AJM_ITEM = {
  id: 10,
  source_id: 10,
  source_name: "Al Jazeera Mubasher",
  kind: "telegram",
  source_class: "native",
  pair_id: null,
  designation_note: null,
  verification_note: null,
  fetched_at: "2026-10-11T15:30:00Z",
  published_at: "2026-10-11T14:38:36Z",
  original_lang: "ar",
  original_text: "عاجل | المتحدث باسم التحالف: اعتداء بمقذوف مجهول على صالة المسافرين رقم 4 بمطار الملك خالد الدولي",
  working_text:
    "Coalition spokesman: An unknown assault on passenger lounge number four at King Khalid International Airport.",
  translation: { status: "ok", engine: "nllb-200-distilled-600M-ct2-int8", src_code: "arb_Arab" },
  url: "https://t.me/ajmubasher/510450",
};

/** Serves `respond(params, n)` and records every request's query params. */
function recordRequests(respond) {
  const seen = [];
  server.use(
    http.get("/api/raw-items", ({ request }) => {
      const params = new URL(request.url).searchParams;
      seen.push(params);
      return HttpResponse.json({
        items: [AJM_ITEM],
        total: 1,
        awaiting_translation: 0,
        translation_failed: 0,
        silent_sources: [],
        max_id: AJM_ITEM.id,
        newer_count: 0,
        ...(respond ? respond(params, seen.length) : {}),
      });
    }),
  );
  return seen;
}

describe("Incoming — daily use (U-4)", () => {
  it("sends the search text as q, so one box searches English and the original script", async () => {
    const user = userEvent.setup();
    const seen = recordRequests();
    renderIncoming();
    await screen.findByText(AJM_ITEM.working_text);

    await user.type(screen.getByRole("searchbox", { name: "Search items" }), "مطار");
    await waitFor(() => expect(seen.at(-1).get("q")).toBe("مطار"));
  });

  it.each([
    ["Kind", "Telegram", "kind", "telegram"],
    ["Language", "Persian", "language", "fa"],
    ["Time", "6h", "window_hours", "6"],
  ])("the %s quick filter %s sends %s=%s and shows as pressed", async (group, label, param, value) => {
    const user = userEvent.setup();
    const seen = recordRequests();
    renderIncoming();
    await screen.findByText(AJM_ITEM.working_text);

    const button = within(screen.getByRole("group", { name: group })).getByRole("button", { name: label });
    await user.click(button);
    await waitFor(() => expect(seen.at(-1).get(param)).toBe(value));
    expect(button).toHaveAttribute("aria-pressed", "true");
  });

  it("pins the list to the newest id it opened with, so a refetch never reflows it", async () => {
    const seen = recordRequests();
    renderIncoming();
    await waitFor(() => expect(seen.at(-1)?.get("up_to_id")).toBe(String(AJM_ITEM.id)));
    expect(seen[0].get("up_to_id")).toBeNull();
  });

  it("shows 'N new since you opened' and re-pins when the reader asks to see them", async () => {
    const user = userEvent.setup();
    // While pinned at 10, three newer items exist and the newest matching id is 13.
    const seen = recordRequests((params) => (params.get("up_to_id") === "10" ? { newer_count: 3, max_id: 13 } : {}));
    renderIncoming();

    await user.click(await screen.findByRole("button", { name: "3 new since you opened — show" }));
    await waitFor(() => expect(seen.at(-1).get("up_to_id")).toBe("13"));
    await waitFor(() => expect(screen.queryByText(/new since you opened/)).not.toBeInTheDocument());
  });

  it("refetches on its own every 60 seconds", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    try {
      const seen = recordRequests();
      renderIncoming();
      await waitFor(() => expect(seen.at(-1)?.get("up_to_id")).toBe(String(AJM_ITEM.id)));
      const before = seen.length;
      await vi.advanceTimersByTimeAsync(60_000);
      await waitFor(() => expect(seen.length).toBeGreaterThan(before));
    } finally {
      vi.useRealTimers();
    }
  });

  it("labels an item whose only time is the fetch time", async () => {
    recordRequests(() => ({ items: [{ ...AJM_ITEM, published_at: null }] }));
    renderIncoming();
    expect(await screen.findByText(/^Fetched .* \(no publication time\)$/)).toBeInTheDocument();
  });

  it("does not call a published item's time a fetch time", async () => {
    recordRequests();
    renderIncoming();
    await screen.findByText(AJM_ITEM.working_text);
    expect(screen.queryByText(/no publication time/)).not.toBeInTheDocument();
  });

  it("says no items match, rather than 'nothing collected', when a filter empties the list", async () => {
    const user = userEvent.setup();
    recordRequests((params) => (params.get("kind") ? { items: [], total: 0, max_id: null } : {}));
    renderIncoming();
    await screen.findByText(AJM_ITEM.working_text);

    await user.click(within(screen.getByRole("group", { name: "Kind" })).getByRole("button", { name: "RSS" }));
    expect(await screen.findByText("No items match these filters.")).toBeInTheDocument();
    expect(screen.queryByText(/No items collected yet/)).not.toBeInTheDocument();
  });
});
