import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { fetchRawItems } from "../api/rawItemsApi";

// U-4: the scheduler (U-3) collects on its own, so the feed refetches every
// minute. The Incoming page pins the list to a baseline id, so a refetch
// updates counts and translations in place but never reflows the list.
export const RAW_ITEMS_REFETCH_MS = 60_000;

export function useRawItems(filters) {
  return useQuery({
    queryKey: ["raw-items", filters],
    queryFn: () => fetchRawItems(filters),
    refetchInterval: RAW_ITEMS_REFETCH_MS,
    placeholderData: keepPreviousData,
  });
}
