import { useQuery } from "@tanstack/react-query";
import { fetchPipelineStatus } from "../api/pipelineApi";

export function usePipelineStatus() {
  return useQuery({
    queryKey: ["pipeline", "status"],
    queryFn: fetchPipelineStatus,
    // U-3: the scheduler runs on its own, so the strip must not go stale under the reader.
    refetchInterval: 60_000,
  });
}
