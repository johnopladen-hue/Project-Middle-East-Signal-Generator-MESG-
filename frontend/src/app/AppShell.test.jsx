import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ADMIN_USER, VIEWER_USER } from "../test/mocks/handlers";
import { server } from "../test/mocks/server";
import { AppShell } from "./AppShell";
import { AuthProvider } from "./AuthContext";

function renderShellAs(user) {
  server.use(http.get("/api/auth/me", () => HttpResponse.json(user)));

  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={["/"]}>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/" element={<p>Dashboard content</p>} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>,
  );
}

describe("AppShell", () => {
  it("shows the Admin nav link for an admin user", async () => {
    renderShellAs(ADMIN_USER);
    await waitFor(() => expect(screen.getByText(ADMIN_USER.username)).toBeInTheDocument());
    expect(screen.getByRole("link", { name: /admin/i })).toBeInTheDocument();
  });

  it("hides the Admin nav link for a viewer (F-7 role gating)", async () => {
    renderShellAs(VIEWER_USER);
    await waitFor(() => expect(screen.getByText(VIEWER_USER.username)).toBeInTheDocument());
    expect(screen.queryByRole("link", { name: /admin/i })).not.toBeInTheDocument();
  });

  it("shows the pipeline status strip from fixture data", async () => {
    renderShellAs(ADMIN_USER);
    expect(await screen.findByText(/3 sources silent/)).toBeInTheDocument();
  });
});
