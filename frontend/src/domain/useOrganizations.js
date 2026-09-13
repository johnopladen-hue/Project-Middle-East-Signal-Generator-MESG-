import { useQuery } from "@tanstack/react-query";
import { fetchOrganization, fetchOrganizations } from "../api/organizationsApi";

export function useOrganizationsList() {
  return useQuery({ queryKey: ["organizations"], queryFn: fetchOrganizations });
}

export function useOrganization(id) {
  return useQuery({
    queryKey: ["organizations", id],
    queryFn: () => fetchOrganization(id),
    enabled: id != null,
  });
}
