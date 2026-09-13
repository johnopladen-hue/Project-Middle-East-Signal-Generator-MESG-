import { apiClient } from "./client";

export function fetchRegions() {
  return apiClient.get("/regions");
}

export function fetchRegionPolygon(aor) {
  return apiClient.get(`/regions/${aor}/polygon`);
}

export function fetchGeoItems(aor) {
  return apiClient.get(`/geo/items?aor=${encodeURIComponent(aor)}`);
}

export function fetchFrameDivergenceNotes(scopeType, scopeId) {
  return apiClient.get(`/frame-divergence-notes?scope_type=${scopeType}&scope_id=${encodeURIComponent(scopeId)}`);
}

export function createFrameDivergenceNote(payload) {
  return apiClient.post("/frame-divergence-notes", payload);
}
