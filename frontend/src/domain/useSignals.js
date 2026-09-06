import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchRecipientsSummary } from "../api/recipientsApi";
import { fetchSignal, fetchSignals, releaseSignal, suppressSignal } from "../api/signalsApi";

export function useSignalsList(filters) {
  return useQuery({ queryKey: ["signals", filters], queryFn: () => fetchSignals(filters) });
}

export function useSignal(id) {
  return useQuery({
    queryKey: ["signals", "detail", id],
    queryFn: () => fetchSignal(id),
    enabled: id != null,
  });
}

export function useRecipientsSummary(enabled) {
  return useQuery({
    queryKey: ["recipients", "summary"],
    queryFn: fetchRecipientsSummary,
    enabled,
  });
}

export function useReleaseSignal(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => releaseSignal(id),
    onSuccess: (updated) => {
      queryClient.setQueryData(["signals", "detail", id], updated);
      queryClient.invalidateQueries({ queryKey: ["signals"] });
    },
  });
}

export function useSuppressSignal(id) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => suppressSignal(id),
    onSuccess: (updated) => {
      queryClient.setQueryData(["signals", "detail", id], updated);
      queryClient.invalidateQueries({ queryKey: ["signals"] });
    },
  });
}
