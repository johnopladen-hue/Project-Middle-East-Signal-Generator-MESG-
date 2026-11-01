import { apiClient } from "./client";

export function fetchRawItems({
  language,
  sourceId,
  sourceClass,
  kind,
  q,
  windowHours,
  upToId,
  limit = 50,
  offset = 0,
} = {}) {
  const params = new URLSearchParams();
  if (language) params.set("language", language);
  if (sourceId) params.set("source_id", sourceId);
  if (sourceClass) params.set("source_class", sourceClass);
  if (kind) params.set("kind", kind);
  if (q) params.set("q", q);
  if (windowHours) params.set("window_hours", windowHours);
  if (upToId != null) params.set("up_to_id", upToId);
  params.set("limit", limit);
  params.set("offset", offset);
  return apiClient.get(`/raw-items?${params.toString()}`);
}

export function fetchRawItem(id) {
  return apiClient.get(`/raw-items/${encodeURIComponent(id)}`);
}
