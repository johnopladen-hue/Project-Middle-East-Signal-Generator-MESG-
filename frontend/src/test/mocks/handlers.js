import { HttpResponse, http } from "msw";

export const ADMIN_USER = { id: 1, username: "analyst", role: "admin", active: true };
export const VIEWER_USER = { id: 2, username: "viewer1", role: "viewer", active: true };

const USERS_BY_USERNAME = {
  [ADMIN_USER.username]: ADMIN_USER,
  [VIEWER_USER.username]: VIEWER_USER,
};

/** Default handlers: not authenticated, login succeeds for either fixture user's credentials. */
export const handlers = [
  http.get("/api/auth/me", () => new HttpResponse(null, { status: 401 })),
  http.post("/api/auth/login", async ({ request }) => {
    const body = await request.json();
    const user = USERS_BY_USERNAME[body.username];
    if (user && body.password === "correct-password") {
      return HttpResponse.json(user);
    }
    return HttpResponse.json({ detail: "Incorrect username or password." }, { status: 401 });
  }),
  http.post("/api/auth/logout", () => new HttpResponse(null, { status: 204 })),
  http.get("/api/pipeline/status", () =>
    HttpResponse.json({ last_run_at: "2026-09-06T09:12:00Z", silent_source_count: 3 }),
  ),
  http.get("/api/briefs", () => HttpResponse.json([])),
];
