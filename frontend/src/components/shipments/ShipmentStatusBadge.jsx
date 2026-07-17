
import Badge from "@/components/ui/Badge";
import { shipmentStatusColor } from "@/utils/statusColors";

const labels = {
  pending: "Pending",
  in_transit: "In Transit",
  "in-transit": "In Transit",
  delivered: "Delivered",
  delayed: "Delayed",
  cancelled: "Cancelled",
  on_schedule: "On Schedule",
  "on-schedule": "On Schedule",
  at_port: "At Port",
  "at-port": "At Port",
  at_warehouse: "At Warehouse",
  customs_hold: "Customs Hold",
  unknown: "Unknown"
};

export default function ShipmentStatusBadge({ status }) {
  return <Badge label={labels[status] || status} className={shipmentStatusColor[status] || "bg-gray-100 text-gray-800"} />;
}
