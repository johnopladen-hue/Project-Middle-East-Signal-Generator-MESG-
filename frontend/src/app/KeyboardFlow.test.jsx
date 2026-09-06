import { QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { HttpResponse, http } from "msw";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { queryClient } from "./queryClient";
import { AppShell } from "./AppShell";
import { AuthProvider } from "./AuthContext";
import { ProtectedRoute } from "./ProtectedRoute";
import { ToastProvider } from "../components/primitives/Toast";
import { Alerts } from "../routes/Alerts";
import { Dashboard } from "../routes/Dashboard";
import { Login } from "../routes/Login";
import { SignalDetail } from "../routes/SignalDetail";
import { Story } from "../routes/Story";
import { server } from "../test/mocks/server";

/** Tabs forward until `getTarget()` has focus, or throws after a bounded
 * number of attempts — proves real keyboard reachability rather than
 * assuming a specific tab-order. */
async function tabTo(user, getTarget, maxTabs = 40) {
  for (let i = 0; i < maxTabs; i += 1) {
    if (document.activeElement === getTarget()) return;
    await user.tab();
  }
  throw new Error("Could not reach target element via Tab within the attempt limit");
}

function renderApp() {
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={["/"]}>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route
                element={
                  <ProtectedRoute>
                    <AppShell />
                  </ProtectedRoute>
                }
              >
                <Route path="/" element={<Dashboard />} />
                <Route path="/stories/:id" element={<Story />} />
                <Route path="/alerts" element={<Alerts />} />
                <Route path="/alerts/:id" element={<SignalDetail />} />
              </Route>
            </Routes>
          </MemoryRouter>
        </AuthProvider>
      </ToastProvider>
    </QueryClientProvider>,
  );
}

const BRIEF_ITEM = {
  story_id: 42,
  title: "Convoy movement reported",
  event_type: "military_event",
  facts: [{ text: "Convoy observed overnight.", raw_item_ids: [] }],
  analysis_text: "Multiple local accounts describe convoy movement.",
  probability_grade: 3,
  contrary_evidence: null,
  has_corroborating_artefact: false,
};

const STORY_DETAIL = {
  id: 42,
  title: "Convoy movement reported",
  event_type: "military_event",
  status: "open",
  facts: [],
  analysis_text: "Multiple local accounts describe convoy movement.",
  probability_grade: 3,
  contrary_evidence: null,
  has_corroborating_artefact: false,
  source_assessments: [],
  divergence: null,
  raw_items: {},
  timeline: [],
};

const SIGNAL = {
  id: 7,
  story_id: 42,
  story_title: "Convoy movement reported",
  type: "military_event",
  severity: "high",
  is_imminent: false,
  status: "new",
  created_at: "2026-09-06T09:00:00Z",
};

describe("keyboard-only walk-through (Order 11 PROOF): login -> read brief -> open story -> release an alert", () => {
  it("completes the whole flow using only typing, Tab, and Enter", async () => {
    server.use(
      http.get("/api/briefs", () => HttpResponse.json([{ id: 1, type: "daily", for_date: "2026-09-06T00:00:00Z" }])),
      http.get("/api/briefs/1", () =>
        HttpResponse.json({
          id: 1,
          type: "daily",
          for_date: "2026-09-06T00:00:00Z",
          content: { items: [BRIEF_ITEM], raw_items: {} },
          released_at: null,
        }),
      ),
      http.get("/api/stories/42", () => HttpResponse.json(STORY_DETAIL)),
      http.get("/api/signals", () => HttpResponse.json([SIGNAL])),
      http.get("/api/signals/7", () => HttpResponse.json(SIGNAL)),
      http.post("/api/signals/7/release", () => HttpResponse.json({ ...SIGNAL, status: "released" })),
    );

    const user = userEvent.setup();
    renderApp();

    // 1. Login — keyboard-only: Tab to focus the first field, type, Tab, Enter.
    const usernameField = await screen.findByLabelText("Username");
    await tabTo(user, () => usernameField);
    await user.keyboard("analyst");
    await user.tab();
    await user.keyboard("correct-password");
    const signInButton = screen.getByRole("button", { name: "Sign in" });
    await tabTo(user, () => signInButton);
    await user.keyboard("{Enter}");

    // 2. Read the brief — Tab to the card headline, Enter expands it.
    const headline = await screen.findByText("Convoy movement reported");
    await tabTo(user, () => headline.closest("button"));
    await user.keyboard("{Enter}");
    await screen.findByText("Convoy observed overnight.");

    // 3. Open the story — Tab to "View full story", Enter follows the link.
    const storyLink = screen.getByRole("link", { name: "View full story" });
    await tabTo(user, () => storyLink);
    await user.keyboard("{Enter}");
    await screen.findByRole("heading", { name: "Convoy movement reported" });

    // 4. Navigate to Alerts via the left-rail nav, then release the signal.
    const alertsNavLink = screen.getByRole("link", { name: "Alerts" });
    await tabTo(user, () => alertsNavLink);
    await user.keyboard("{Enter}");

    const signalLink = await screen.findByRole("link", { name: /Convoy movement reported/ });
    await tabTo(user, () => signalLink);
    await user.keyboard("{Enter}");

    const releaseButton = await screen.findByRole("button", { name: "Release to recipients" });
    await tabTo(user, () => releaseButton);
    await user.keyboard("{Enter}");

    const confirmButtons = await screen.findAllByRole("button", { name: "Release to recipients" });
    const confirmButton = confirmButtons[confirmButtons.length - 1];
    await tabTo(user, () => confirmButton);
    await user.keyboard("{Enter}");

    await waitFor(() => expect(screen.getByText("Released.")).toBeInTheDocument());
  }, 20000);
});
