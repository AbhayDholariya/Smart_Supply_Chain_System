import { useQuery } from "@tanstack/react-query";
import { inventoryService } from "@/services/inventoryService";

export function useWarehouses() {
  return useQuery({
    queryKey: ["warehouses"],
    queryFn: () => inventoryService.getWarehouses().then((r) => r.data),
  });
}

export function useInventoryItems(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["inventory-items", params],
    queryFn: () => inventoryService.getItems(params).then((r) => r.data),
  });
}
