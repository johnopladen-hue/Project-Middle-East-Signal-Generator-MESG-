import { HttpResponse, http } from "msw";

export const VALID_USER = { id: 1, username: "analyst", role: "admin", active: true };

/** Default handlers: not authenticated, login succeeds for VALID_USER's credentials. */
export const handlers = [
  http.get("/api/auth/me", () => new HttpResponse(null, { status: 401 })),
  http.post("/api/auth/login", async ({ request }) => {
    const body = await request.json();
    if (body.username === "analyst" && body.password === "correct-password") {
      return HttpResponse.json(VALID_USER);
    }
    return HttpResponse.json({ detail: "Incorrect username or password." }, { status: 401 });
  }),
  http.post("/api/auth/logout", () => new HttpResponse(null, { status: 204 })),
];
