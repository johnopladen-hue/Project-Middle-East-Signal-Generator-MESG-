import { apiClient } from "./client";

export function fetchCapabilities() {
  return apiClient.get("/capabilities");
}
