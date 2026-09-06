import { useQuery } from "@tanstack/react-query";
import { fetchStory } from "../api/storiesApi";

export function useStory(id) {
  return useQuery({
    queryKey: ["stories", id],
    queryFn: () => fetchStory(id),
    enabled: id != null,
  });
}
