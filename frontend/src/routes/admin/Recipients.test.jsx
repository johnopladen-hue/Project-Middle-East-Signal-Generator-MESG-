import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";
import { server } from "../../test/mocks/server";
import { AdminRecipients } from "./Recipients";

const FIXTURE_RECIPIENTS = [
  { id: 1, name: "Owner", email: "owner@example.com", phone: "+15551234567", channels: ["email", "sms"], active: true, approved_by: "owner" },
];

function renderRecipients() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AdminRecipients />
    </QueryClientProvider>,
  );
}

describe("AdminRecipients", () => {
  it("shows the Private-repo tripwire note (TDD §10)", async () => {
    server.use(http.get("/api/admin/recipients", () => HttpResponse.json([])));
    renderRecipients();
    expect(
      await screen.findByText(/The moment real recipient data lands, this repository flips to Private/),
    ).toBeInTheDocument();
  });

  it("masks email and phone by default, and reveals on intent", async () => {
    server.use(http.get("/api/admin/recipients", () => HttpResponse.json(FIXTURE_RECIPIENTS)));
    const user = userEvent.setup();
    renderRecipients();

    await screen.findByText("Owner");
    expect(screen.queryByText("owner@example.com")).not.toBeInTheDocument();
    expect(screen.queryByText("+15551234567")).not.toBeInTheDocument();

    const revealButtons = screen.getAllByRole("button", { name: "Reveal" });
    await user.click(revealButtons[0]);

    expect(screen.getByText("owner@example.com")).toBeInTheDocument();
  });
});
