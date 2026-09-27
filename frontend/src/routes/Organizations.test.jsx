import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { MemoryRouter, Route, Routes, useParams } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { orgSummaryByName, organizations } from "../test/fixtures";
import { server } from "../test/mocks/server";
import { Organizations } from "./Organizations";

function ProfileStub() {
  const { id } = useParams();
  return <p>profile route for organization {id}</p>;
}

function renderDirectory() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/organizations"]}>
        <Routes>
          <Route path="/organizations" element={<Organizations />} />
          <Route path="/organizations/:id" element={<ProfileStub />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Organizations directory (D-012, O-8)", () => {
  it("lists every harvested organization with its theatre and source dataset", async () => {
    server.use(http.get("/api/organizations", () => HttpResponse.json(organizations)));
    renderDirectory();

    expect(await screen.findByRole("heading", { name: "Organizations" })).toBeInTheDocument();

    // One body row per organization the API returned - none dropped, none invented.
    const rows = screen.getAllByRole("row").slice(1); // skip header row
    expect(rows).toHaveLength(organizations.length);

    const hamas = orgSummaryByName("Hamas");
    const hamasRow = screen.getByRole("link", { name: "Hamas" }).closest("tr");
    expect(within(hamasRow).getByText(hamas.theatre)).toBeInTheDocument();
    expect(within(hamasRow).getByText(hamas.source_dataset)).toBeInTheDocument();
  });

  it("renders an em dash, not a blank or a guess, when an organization has no theatre", async () => {
    const hamas = orgSummaryByName("Hamas");
    // Same real record with its theatre removed - exercises the null branch without inventing an org.
    server.use(http.get("/api/organizations", () => HttpResponse.json([{ ...hamas, theatre: null }])));
    renderDirectory();

    const row = (await screen.findByRole("link", { name: "Hamas" })).closest("tr");
    expect(within(row).getByText("—")).toBeInTheDocument();
  });

  it("navigates to the organization's profile route when its name is clicked", async () => {
    server.use(http.get("/api/organizations", () => HttpResponse.json(organizations)));
    renderDirectory();

    const pflp = orgSummaryByName("PFLP");
    await userEvent.click(await screen.findByRole("link", { name: "PFLP" }));
    expect(screen.getByText(`profile route for organization ${pflp.id}`)).toBeInTheDocument();
  });

  it("shows an error state with retry, and recovers on retry", async () => {
    let calls = 0;
    server.use(
      http.get("/api/organizations", () => {
        calls += 1;
        return calls === 1
          ? HttpResponse.json({ detail: "boom" }, { status: 500 })
          : HttpResponse.json(organizations);
      }),
    );
    renderDirectory();

    expect(await screen.findByText("Couldn't load organizations.")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));
    expect(await screen.findByRole("link", { name: "Hamas" })).toBeInTheDocument();
  });
});
