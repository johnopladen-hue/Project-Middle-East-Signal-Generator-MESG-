import { apiClient } from "./client";

export function fetchStory(id) {
  return apiClient.get(`/stories/${id}`);
}
