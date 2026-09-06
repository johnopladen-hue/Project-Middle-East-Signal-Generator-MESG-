import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { HttpResponse, http } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ADMIN_USER, VIEWER_USER } from "../test/mocks/handlers";
import { server } from "../test/mocks/server";
import { AuthProvider } from "./AuthContext";
import { ProtectedRoute } from "./ProtectedRoute";

function renderAdminRouteAs(user) {
  server.use(http.get("/api/auth/me", () => HttpResponse.json(user)));
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={["/admin/sources"]}>
          <Routes>
            <Route path="/" element={<p>Dashboard</p>} />
            <Route
              path="/admin/sources"
              element={
                <ProtectedRoute requireRole="admin">
                  <p>Admin sources page</p>
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>,
  );
}

describe("ProtectedRoute requireRole", () => {
  it("lets an admin through to an admin-only route", async () => {
    renderAdminRouteAs(ADMIN_USER);
    expect(await screen.findByText("Admin sources page")).toBeInTheDocument();
  });

  it("refuses a viewer — redirected away from the admin-only route (Order 10 PROOF)", async () => {
    renderAdminRouteAs(VIEWER_USER);
    await waitFor(() => expect(screen.getByText("Dashboard")).toBeInTheDocument());
    expect(screen.queryByText("Admin sources page")).not.toBeInTheDocument();
  });
});
