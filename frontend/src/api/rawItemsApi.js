import { apiClient } from "./client";

export function fetchRawItems({ language, sourceId, sourceClass, kind, limit = 50, offset = 0 } = {}) {
  const params = new URLSearchParams();
  if (language) params.set("language", language);
  if (sourceId) params.set("source_id", sourceId);
  if (sourceClass) params.set("source_class", sourceClass);
  if (kind) params.set("kind", kind);
  params.set("limit", limit);
  params.set("offset", offset);
  return apiClient.get(`/raw-items?${params.toString()}`);
}
