import { apiClient } from "./client";

export function login(username, password) {
  return apiClient.post("/auth/login", { username, password });
}

export function logout() {
  return apiClient.post("/auth/logout");
}

export function fetchMe() {
  return apiClient.get("/auth/me");
}
