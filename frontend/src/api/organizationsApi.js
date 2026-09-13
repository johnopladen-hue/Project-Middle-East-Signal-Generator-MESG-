import { apiClient } from "./client";

export function fetchOrganizations() {
  return apiClient.get("/organizations");
}

export function fetchOrganization(id) {
  return apiClient.get(`/organizations/${id}`);
}
