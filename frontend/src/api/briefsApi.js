import { apiClient } from "./client";

export function fetchDailyBriefs() {
  return apiClient.get("/briefs?type=daily");
}

export function fetchWeeklyBriefs() {
  return apiClient.get("/briefs?type=weekly");
}

export function fetchBrief(id) {
  return apiClient.get(`/briefs/${id}`);
}
