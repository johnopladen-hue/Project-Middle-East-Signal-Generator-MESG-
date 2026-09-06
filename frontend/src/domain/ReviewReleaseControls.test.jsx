import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { describe, expect, it } from "vitest";
import { AuthProvider } from "../app/AuthContext";
import { ToastProvider } from "../components/primitives/Toast";
import { ADMIN_USER, VIEWER_USER } from "../test/mocks/handlers";
import { server } from "../test/mocks/server";
import { ReviewReleaseControls } from "./ReviewReleaseControls";

function renderAs(user) {
  server.use(http.get("/api/auth/me", () => HttpResponse.json(user)));
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthProvider>
          <ReviewReleaseControls signalId={1} />
        </AuthProvider>
      </ToastProvider>
    </QueryClientProvider>,
  );
}

describe("ReviewReleaseControls", () => {
  it("renders nothing for a viewer — cannot see or invoke release/suppress (F-7)", async () => {
    renderAs(VIEWER_USER);
    await new Promise((resolve) => setTimeout(resolve, 0));
    expect(screen.queryByRole("button", { name: /Release to recipients/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Suppress/ })).not.toBeInTheDocument();
  });

  it("shows recipient counts before confirming, and does not call release until confirmed", async () => {
    let releaseCallCount = 0;
    server.use(
      http.post("/api/signals/1/release", () => {
        releaseCallCount += 1;
        return HttpResponse.json({ id: 1, status: "released" });
      }),
    );

    const user = userEvent.setup();
    renderAs(ADMIN_USER);

    await user.click(await screen.findByRole("button", { name: "Release to recipients" }));

    expect(
      await screen.findByText(/This sends to 4 active recipients \(3 email, 1 SMS\)\. This cannot be recalled\./),
    ).toBeInTheDocument();
    expect(releaseCallCount).toBe(0);

    const confirmButtons = screen.getAllByRole("button", { name: "Release to recipients" });
    await user.click(confirmButtons[confirmButtons.length - 1]);

    await waitFor(() => expect(releaseCallCount).toBe(1));
  });

  it("suppress needs only a light inline confirm, not the full modal", async () => {
    let suppressCallCount = 0;
    server.use(
      http.post("/api/signals/1/suppress", () => {
        suppressCallCount += 1;
        return HttpResponse.json({ id: 1, status: "suppressed" });
      }),
    );

    const user = userEvent.setup();
    renderAs(ADMIN_USER);

    await user.click(await screen.findByRole("button", { name: "Suppress" }));
    expect(screen.getByText("Suppress this signal?")).toBeInTheDocument();
    expect(suppressCallCount).toBe(0);

    await user.click(screen.getByRole("button", { name: "Yes" }));

    await waitFor(() => expect(suppressCallCount).toBe(1));
  });
});
