import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "@/services/analyticsService";

export function useShipmentKPI() {
  return useQuery({
    queryKey: ["kpi-shipments"],
    queryFn: () => analyticsService.getShipmentKPI().then((r) => r.data),
  });
}

export function useInventoryKPI() {
  return useQuery({
    queryKey: ["kpi-inventory"],
    queryFn: () => analyticsService.getInventoryKPI().then((r) => r.data),
  });
}

export function useSupplierKPI() {
  return useQuery({
    queryKey: ["kpi-suppliers"],
    queryFn: () => analyticsService.getSupplierKPI().then((r) => r.data),
  });
}
