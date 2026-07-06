import { useParams, Link } from "react-router-dom";
import { ArrowLeft, MapPin } from "lucide-react";
import { useShipment } from "@/hooks/useShipments";
import ShipmentStatusBadge from "@/components/shipments/ShipmentStatusBadge";
import Card from "@/components/ui/Card";
import Spinner from "@/components/ui/Spinner";
import { formatDateTime } from "@/utils/formatDate";

export default function ShipmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: shipment, isLoading } = useShipment(Number(id));

  if (isLoading) {
    return (
      <div className="flex justify-center py-20">
        <Spinner />
      </div>
    );
  }

  if (!shipment) return <p className="text-center text-gray-400">Shipment not found.</p>;

  return (
    <div className="space-y-6">
      <Link
        to="/shipments"
        className="inline-flex items-center gap-1 text-sm text-primary-600 hover:underline"
      >
        <ArrowLeft size={14} /> Back to Shipments
      </Link>

      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold text-gray-900">{shipment.tracking_number}</h1>
        <ShipmentStatusBadge status={shipment.status} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Details card */}
        <Card>
          <h2 className="mb-4 font-semibold text-gray-700">Shipment Details</h2>
          <dl className="space-y-2 text-sm">
            {[
              ["Origin", shipment.origin],
              ["Destination", shipment.destination],
              ["Carrier", shipment.carrier || "—"],
              ["Weight", shipment.weight_kg ? `${shipment.weight_kg} kg` : "—"],
              [
                "Estimated Delivery",
                shipment.estimated_delivery ? formatDateTime(shipment.estimated_delivery) : "—",
              ],
              [
                "Actual Delivery",
                shipment.actual_delivery ? formatDateTime(shipment.actual_delivery) : "—",
              ],
            ].map(([label, value]) => (
              <div key={label} className="flex justify-between">
                <dt className="text-gray-500">{label}</dt>
                <dd className="font-medium text-gray-800">{value}</dd>
              </div>
            ))}
          </dl>
        </Card>

        {/* Location card */}
        {shipment.current_latitude && shipment.current_longitude && (
          <Card>
            <h2 className="mb-3 font-semibold text-gray-700">Current Location</h2>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <MapPin size={16} className="text-primary-600" />
              <span>
                {shipment.current_latitude}, {shipment.current_longitude}
              </span>
            </div>
          </Card>
        )}
      </div>

      {/* Event timeline */}
      <Card>
        <h2 className="mb-4 font-semibold text-gray-700">Event Timeline</h2>
        {shipment.events.length === 0 ? (
          <p className="text-sm text-gray-400">No events recorded.</p>
        ) : (
          <ol className="relative border-l border-gray-200 pl-6 space-y-4">
            {shipment.events.map((ev) => (
              <li key={ev.id} className="relative">
                <div className="absolute -left-[25px] mt-1 h-3 w-3 rounded-full border-2 border-primary-500 bg-white" />
                <p className="text-xs text-gray-400">{formatDateTime(ev.timestamp)}</p>
                <p className="text-sm font-medium text-gray-800 capitalize">
                  {ev.status.replace("_", " ")}
                </p>
                {ev.location && <p className="text-xs text-gray-500">{ev.location}</p>}
                {ev.note && <p className="text-xs text-gray-500 italic">{ev.note}</p>}
              </li>
            ))}
          </ol>
        )}
      </Card>
    </div>
  );
}
