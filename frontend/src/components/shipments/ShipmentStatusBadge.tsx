import Badge from "@/components/ui/Badge";
import { shipmentStatusColor } from "@/utils/statusColors";
import type { ShipmentStatus } from "@/types/shipment";

const labels: Record<ShipmentStatus, string> = {
  pending: "Pending",
  in_transit: "In Transit",
  delivered: "Delivered",
  delayed: "Delayed",
  cancelled: "Cancelled",
};

export default function ShipmentStatusBadge({ status }: { status: ShipmentStatus }) {
  return <Badge label={labels[status]} className={shipmentStatusColor[status]} />;
}
