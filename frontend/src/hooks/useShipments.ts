import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { shipmentService } from "@/services/shipmentService";
import type { Shipment } from "@/types/shipment";
import toast from "react-hot-toast";

export function useShipments(params?: Record<string, string>) {
  return useQuery({
    queryKey: ["shipments", params],
    queryFn: () => shipmentService.getAll(params).then((r) => r.data),
  });
}

export function useShipment(id: number) {
  return useQuery({
    queryKey: ["shipment", id],
    queryFn: () => shipmentService.getById(id).then((r) => r.data),
    enabled: !!id,
  });
}

export function useUpdateShipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Shipment> }) =>
      shipmentService.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["shipments"] });
      toast.success("Shipment updated");
    },
    onError: () => toast.error("Failed to update shipment"),
  });
}
