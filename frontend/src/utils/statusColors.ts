import type { ShipmentStatus } from "@/types/shipment";

export const shipmentStatusColor: Record<ShipmentStatus, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  in_transit: "bg-blue-100 text-blue-800",
  delivered: "bg-green-100 text-green-800",
  delayed: "bg-red-100 text-red-800",
  cancelled: "bg-gray-100 text-gray-600",
};
