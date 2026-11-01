import { useQuery } from "@tanstack/react-query";
import { fetchCapabilities } from "../api/capabilitiesApi";

export function useCapabilities() {
  return useQuery({
    queryKey: ["capabilities"],
    queryFn: fetchCapabilities,
    refetchInterval: 60_000,
  });
}
