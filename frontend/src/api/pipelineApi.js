import { apiClient } from "./client";

export function fetchPipelineStatus() {
  return apiClient.get("/pipeline/status");
}
