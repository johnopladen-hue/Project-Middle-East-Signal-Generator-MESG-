/** Boundary API client — TDD §7, F-3 (httpOnly session cookie, credentials: 'include'). */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export class ApiError extends Error {
  constructor(message, { status, retryAfterSeconds } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.retryAfterSeconds = retryAfterSeconds;
  }
}

async function request(path, { method = "GET", body } = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    method,
    credentials: "include",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 429) {
    const retryAfterSeconds = Number(response.headers.get("Retry-After") ?? 30);
    throw new ApiError("Too many attempts", { status: 429, retryAfterSeconds });
  }

  if (!response.ok) {
    let message = "Request failed";
    try {
      const data = await response.json();
      message = data.detail ?? message;
    } catch {
      // no JSON body
    }
    throw new ApiError(message, { status: response.status });
  }

  if (response.status === 204) return null;
  return response.json();
}

export const apiClient = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  patch: (path, body) => request(path, { method: "PATCH", body }),
};
