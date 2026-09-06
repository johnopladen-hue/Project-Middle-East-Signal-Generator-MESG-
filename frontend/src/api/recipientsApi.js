import { apiClient } from "./client";

export function fetchRecipientsSummary() {
  return apiClient.get("/recipients/summary");
}
