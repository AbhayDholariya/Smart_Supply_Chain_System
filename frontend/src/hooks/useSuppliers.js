import { useQuery } from "@tanstack/react-query";
import { supplierService } from "@/services/supplierService";

export function useSuppliers() {
  return useQuery({
    queryKey: ["suppliers"],
    queryFn: () => supplierService.getAll().then((r) => r.data),
  });
}

export function useSupplier(id) {
  return useQuery({
    queryKey: ["supplier", id],
    queryFn: () => supplierService.getById(id).then((r) => r.data),
    enabled: !!id,
  });
}
