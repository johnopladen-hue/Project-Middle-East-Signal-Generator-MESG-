import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { recipientsApi, settingsApi, sourcesApi } from "../api/adminApi";

export function useSources() {
  return useQuery({ queryKey: ["admin", "sources"], queryFn: sourcesApi.list });
}

export function useCreateSource() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: sourcesApi.create,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "sources"] }),
  });
}

export function useUpdateSource() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }) => sourcesApi.update(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "sources"] }),
  });
}

export function useRecipients() {
  return useQuery({ queryKey: ["admin", "recipients"], queryFn: recipientsApi.list });
}

export function useCreateRecipient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: recipientsApi.create,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "recipients"] }),
  });
}

export function useUpdateRecipient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, ...payload }) => recipientsApi.update(id, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "recipients"] }),
  });
}

export function useSettings() {
  return useQuery({ queryKey: ["admin", "settings"], queryFn: settingsApi.get });
}

export function useUpdateSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: settingsApi.update,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "settings"] }),
  });
}
