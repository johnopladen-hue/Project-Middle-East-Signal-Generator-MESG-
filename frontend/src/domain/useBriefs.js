import { useQuery } from "@tanstack/react-query";
import { fetchBrief, fetchDailyBriefs } from "../api/briefsApi";

export function useDailyBriefsList() {
  return useQuery({ queryKey: ["briefs", "daily"], queryFn: fetchDailyBriefs });
}

export function useBrief(id) {
  return useQuery({
    queryKey: ["briefs", id],
    queryFn: () => fetchBrief(id),
    enabled: id != null,
  });
}
