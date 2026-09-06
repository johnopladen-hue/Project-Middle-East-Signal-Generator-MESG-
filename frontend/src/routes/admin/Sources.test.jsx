import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";
import { server } from "../../test/mocks/server";
import { AdminSources } from "./Sources";

const FIXTURE_SOURCES = [
  { id: 1, name: "Al Jazeera", url: "https://aljazeera.com", language: "Arabic", dialect: null, type: "rss", region: null, credibility_prior: 0.8, last_seen_at: new Date().toISOString(), active: true },
  { id: 2, name: "Stale Outlet", url: "https://stale.example.com", language: "Persian", dialect: null, type: "rss", region: null, credibility_prior: 0.5, last_seen_at: null, active: true },
];

function renderSources() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminSources />
    </QueryClientProvider>,
  );
}

describe("AdminSources", () => {
  it("lists sources and shows the silence flag for a source with no last_seen_at", async () => {
    server.use(http.get("/api/admin/sources", () => HttpResponse.json(FIXTURE_SOURCES)));
    renderSources();

    expect(await screen.findByText("Al Jazeera")).toBeInTheDocument();
    expect(screen.getByText("Stale Outlet")).toBeInTheDocument();
    expect(screen.getByText("Silent")).toBeInTheDocument();
  });

  it("can add a source", async () => {
    let created = null;
    server.use(
      http.get("/api/admin/sources", () => HttpResponse.json(FIXTURE_SOURCES)),
      http.post("/api/admin/sources", async ({ request }) => {
        created = await request.json();
        return HttpResponse.json({ id: 3, ...created, dialect: null, region: null, last_seen_at: null }, { status: 201 });
      }),
    );
    const user = userEvent.setup();
    renderSources();

    await user.click(await screen.findByRole("button", { name: "Add source" }));
    await user.type(screen.getByLabelText("Name"), "Rudaw");
    await user.type(screen.getByLabelText("URL"), "https://rudaw.net");
    await user.type(screen.getByLabelText("Language"), "Kurdish");
    await user.click(screen.getByRole("button", { name: "Save" }));

    await screen.findByRole("button", { name: "Add source" });
    expect(created).toMatchObject({ name: "Rudaw", url: "https://rudaw.net", language: "Kurdish" });
  });
});
