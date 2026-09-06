import { apiClient } from "./client";

export const sourcesApi = {
  list: () => apiClient.get("/admin/sources"),
  create: (payload) => apiClient.post("/admin/sources", payload),
  update: (id, payload) => apiClient.patch(`/admin/sources/${id}`, payload),
};

export const recipientsApi = {
  list: () => apiClient.get("/admin/recipients"),
  create: (payload) => apiClient.post("/admin/recipients", payload),
  update: (id, payload) => apiClient.patch(`/admin/recipients/${id}`, payload),
};

export const settingsApi = {
  get: () => apiClient.get("/admin/settings"),
  update: (payload) => apiClient.patch("/admin/settings", payload),
};
