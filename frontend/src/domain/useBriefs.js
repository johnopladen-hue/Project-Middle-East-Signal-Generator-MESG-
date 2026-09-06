import { useQuery } from "@tanstack/react-query";
import { fetchBrief, fetchDailyBriefs, fetchWeeklyBriefs } from "../api/briefsApi";

export function useDailyBriefsList() {
  return useQuery({ queryKey: ["briefs", "daily"], queryFn: fetchDailyBriefs });
}

export function useWeeklyBriefsList() {
  return useQuery({ queryKey: ["briefs", "weekly"], queryFn: fetchWeeklyBriefs });
}

export function useBrief(id) {
  return useQuery({
    queryKey: ["briefs", id],
    queryFn: () => fetchBrief(id),
    enabled: id != null,
  });
}
