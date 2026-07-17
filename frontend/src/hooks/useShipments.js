import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { shipmentService } from "@/services/shipmentService";
import toast from "react-hot-toast";

export function useShipments(params) {
  return useQuery({
    queryKey: ["shipments", params],
    queryFn: () => shipmentService.getLiveShipments().then((r) => r.data),
  });
}

export function useShipment(id) {
  return useQuery({
    queryKey: ["shipment", id],
    queryFn: () => shipmentService.getShipmentById(id).then((r) => r.data),
    enabled: !!id,
  });
}

export function useRerouteShipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }) =>
      shipmentService.rerouteShipment(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["shipments"] });
      qc.invalidateQueries({ queryKey: ["alerts"] });
      toast.success("Reroute initiated");
    },
    onError: () => toast.error("Failed to initiate reroute"),
  });
}
