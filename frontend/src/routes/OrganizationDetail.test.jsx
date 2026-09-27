import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";
import { orgDetailByName, organizationDetails } from "../test/fixtures";
import { server } from "../test/mocks/server";
import { OrganizationDetail } from "./OrganizationDetail";

function serveCapturedProfiles() {
  server.use(
    http.get("/api/organizations/:id", ({ params }) => {
      const detail = organizationDetails[params.id];
      return detail ? HttpResponse.json(detail) : HttpResponse.json({ detail: "Not found" }, { status: 404 });
    }),
  );
}

function renderProfile(id) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[`/organizations/${id}`]}>
        <Routes>
          <Route path="/organizations/:id" element={<OrganizationDetail />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

function section(headingName) {
  return screen.getByRole("heading", { name: headingName }).closest("section");
}

describe("Organization profile (D-012, O-8)", () => {
  beforeEach(serveCapturedProfiles);

  it("shows name, theatre, aliases and the required source citation", async () => {
    const pflp = orgDetailByName("PFLP");
    renderProfile(pflp.id);

    expect(await screen.findByRole("heading", { level: 1, name: "PFLP" })).toBeInTheDocument();
    expect(screen.getByText(pflp.theatre)).toBeInTheDocument();
    expect(screen.getByText(`Also known as: ${pflp.aliases.join(", ")}`)).toBeInTheDocument();

    // UCDP's CC BY 4.0 licence requires the citation on every surface showing its data (D-013).
    const citation = section("Source & citation");
    expect(within(citation).getByText(pflp.citation)).toBeInTheDocument();
    expect(within(citation).getByRole("link", { name: pflp.source_dataset })).toHaveAttribute("href", pflp.source_url);
  });

  it("renders each designation as a sourced characterization - who said it, which list, match confidence, link", async () => {
    const pflpGc = orgDetailByName("PFLP-GC");
    const [designation] = pflpGc.designations;
    renderProfile(pflpGc.id);

    await screen.findByRole("heading", { level: 1, name: "PFLP-GC" });
    const designations = section("Designations");

    expect(within(designations).getByText(designation.body)).toBeInTheDocument();
    expect(within(designations).getByText(new RegExp(`List ${designation.list_id}`))).toBeInTheDocument();
    // The real OFAC fuzzy-match score for PFLP-GC is < 1.0 - shown, not rounded away to certainty.
    const pct = (designation.match_confidence * 100).toFixed(0);
    expect(within(designations).getByText(`confidence ${pct}%`)).toBeInTheDocument();
    expect(within(designations).getByRole("link", { name: "source" })).toHaveAttribute("href", designation.url);
  });

  it("says so explicitly when an organization has no designations, rather than showing nothing", async () => {
    const fatah = orgDetailByName("Fatah");
    expect(fatah.designations).toHaveLength(0); // guard: the captured data still has this shape
    renderProfile(fatah.id);

    await screen.findByRole("heading", { level: 1, name: "Fatah" });
    expect(within(section("Designations")).getByText("No designations on record.")).toBeInTheDocument();
  });

  it("reads outbound and inbound relationship edges in the right direction", async () => {
    const pflp = orgDetailByName("PFLP");
    renderProfile(pflp.id);

    await screen.findByRole("heading", { level: 1, name: "PFLP" });
    const items = within(section("Relationships")).getAllByRole("listitem");
    expect(items).toHaveLength(pflp.relationships.length);

    // Real UCDP history: PFLP split from the PLO; PFLP-GC split from PFLP.
    expect(items.some((li) => li.textContent === "split-from PLO")).toBe(true);
    expect(items.some((li) => li.textContent === "PFLP-GC split-from this organization")).toBe(true);
  });

  it("follows a relationship edge to the other organization's profile", async () => {
    const pflp = orgDetailByName("PFLP");
    const plo = orgDetailByName("PLO");
    renderProfile(pflp.id);

    await screen.findByRole("heading", { level: 1, name: "PFLP" });
    const [ploLink] = within(section("Relationships")).getAllByRole("link", { name: "PLO" });
    expect(ploLink).toHaveAttribute("href", `/organizations/${plo.id}`);

    await userEvent.click(ploLink);
    expect(await screen.findByRole("heading", { level: 1, name: "PLO" })).toBeInTheDocument();
  });

  it("says so explicitly when an organization has no relationships", async () => {
    const hamas = orgDetailByName("Hamas");
    expect(hamas.relationships).toHaveLength(0);
    renderProfile(hamas.id);

    await screen.findByRole("heading", { level: 1, name: "Hamas" });
    expect(within(section("Relationships")).getByText("No relationships on record.")).toBeInTheDocument();
  });

  it("shows an error state for an id the API does not know", async () => {
    renderProfile(999999);
    expect(await screen.findByText("Couldn't load this organization.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });
});
