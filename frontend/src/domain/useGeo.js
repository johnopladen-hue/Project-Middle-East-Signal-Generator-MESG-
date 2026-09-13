import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createFrameDivergenceNote,
  fetchFrameDivergenceNotes,
  fetchGeoItems,
  fetchRegionPolygon,
  fetchRegions,
} from "../api/geoApi";

export function useRegions() {
  return useQuery({ queryKey: ["regions"], queryFn: fetchRegions });
}

export function useRegionPolygon(aor) {
  return useQuery({
    queryKey: ["regions", aor, "polygon"],
    queryFn: () => fetchRegionPolygon(aor),
    enabled: !!aor,
  });
}

export function useGeoItems(aor) {
  return useQuery({ queryKey: ["geo-items", aor], queryFn: () => fetchGeoItems(aor), enabled: !!aor });
}

export function useFrameDivergenceNotes(scopeType, scopeId) {
  return useQuery({
    queryKey: ["frame-divergence-notes", scopeType, scopeId],
    queryFn: () => fetchFrameDivergenceNotes(scopeType, scopeId),
    enabled: !!scopeId,
  });
}

export function useCreateFrameDivergenceNote(scopeType, scopeId) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (text) => createFrameDivergenceNote({ scope_type: scopeType, scope_id: scopeId, text }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["frame-divergence-notes", scopeType, scopeId] });
    },
  });
}
