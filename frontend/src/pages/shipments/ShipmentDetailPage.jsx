
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, MapPin } from "lucide-react";
import { useShipment, useRerouteShipment } from "@/hooks/useShipments";
import ShipmentStatusBadge from "@/components/shipments/ShipmentStatusBadge";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Spinner from "@/components/ui/Spinner";

export default function ShipmentDetailPage() {
  const { id } = useParams();
  const { data: shipment, isLoading } = useShipment(id);
  const rerouteMutation = useRerouteShipment();

  const handleReroute = () => {
    rerouteMutation.mutate({ id, data: { reason: "Manual reroute", priority: "normal" } });
  };

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
        <h1 className="text-2xl font-bold text-gray-900">{shipment.id}</h1>
        <ShipmentStatusBadge status={shipment.status} />
        <Button
          onClick={handleReroute}
          disabled={rerouteMutation.isPending}
          variant="outline"
        >
          {rerouteMutation.isPending ? "Rerouting..." : "Reroute Shipment"}
        </Button>
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
              ["Cargo Type", shipment.cargo_type || "—"],
              ["Value (USD)", shipment.value_usd ? `$${shipment.value_usd}` : "—"],
              ["Risk Score", `${shipment.risk_score}/100`],
              ["Risk Level", shipment.risk_level],
              ["Speed (km/h)", shipment.speed_kmh],
              ["Progress", `${Math.round(shipment.progress * 100)}%`],
              ["ETA Days", shipment.eta_days || "—"]
            ].map(([label, value]) => (
              <div key={label} className="flex justify-between">
                <dt className="text-gray-500">{label}</dt>
                <dd className="font-medium text-gray-800">{value}</dd>
              </div>
            ))}
          </dl>
        </Card>

        {/* Location card */}
        <Card>
          <h2 className="mb-3 font-semibold text-gray-700">Current Location</h2>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <MapPin size={16} className="text-primary-600" />
            <span>
              {shipment.lat}, {shipment.lng}
            </span>
          </div>
          {shipment.top_risk_factors && shipment.top_risk_factors.length > 0 && (
            <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
              <h3 className="font-semibold text-yellow-800 mb-2">Top Risk Factors</h3>
              <ul className="text-sm text-yellow-700">
                {shipment.top_risk_factors.map((factor, idx) => (
                  <li key={idx}>{factor}</li>
                ))}
              </ul>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
