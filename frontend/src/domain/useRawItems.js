import { useQuery } from "@tanstack/react-query";
import { fetchRawItems } from "../api/rawItemsApi";

export function useRawItems(filters) {
  return useQuery({
    queryKey: ["raw-items", filters],
    queryFn: () => fetchRawItems(filters),
  });
}
