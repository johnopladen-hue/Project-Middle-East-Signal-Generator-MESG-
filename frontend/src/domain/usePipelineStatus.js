import { useQuery } from "@tanstack/react-query";
import { fetchPipelineStatus } from "../api/pipelineApi";

export function usePipelineStatus() {
  return useQuery({
    queryKey: ["pipeline", "status"],
    queryFn: fetchPipelineStatus,
  });
}
