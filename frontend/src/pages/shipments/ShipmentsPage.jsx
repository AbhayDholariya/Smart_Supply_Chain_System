
import { useState } from "react";
import { useShipments } from "@/hooks/useShipments";
import ShipmentTable from "@/components/shipments/ShipmentTable";
import Spinner from "@/components/ui/Spinner";
import Input from "@/components/ui/Input";

export default function ShipmentsPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useShipments();
  
  // Filter shipments based on search
  const filteredShipments = (data || []).filter(s => 
    s.id.toLowerCase().includes(search.toLowerCase()) || 
    s.origin.toLowerCase().includes(search.toLowerCase()) || 
    s.destination.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Shipments</h1>
      </div>

      <div className="max-w-sm">
        <Input
          placeholder="Search by tracking #, origin, destination…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Spinner />
        </div>
      ) : filteredShipments.length ? (
        <ShipmentTable shipments={filteredShipments} />
      ) : (
        <p className="py-10 text-center text-gray-400">No shipments found.</p>
      )}
    </div>
  );
}
