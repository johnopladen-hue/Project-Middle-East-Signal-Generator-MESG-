import { apiClient } from "./client";

export function fetchSignals(filters = {}) {
  const params = new URLSearchParams(
    Object.entries(filters).filter(([, value]) => value != null && value !== ""),
  );
  const query = params.toString();
  return apiClient.get(`/signals${query ? `?${query}` : ""}`);
}

export function fetchSignal(id) {
  return apiClient.get(`/signals/${id}`);
}

export function releaseSignal(id) {
  return apiClient.post(`/signals/${id}/release`);
}

export function suppressSignal(id) {
  return apiClient.post(`/signals/${id}/suppress`);
}
