
import { Truck, Package, Users, AlertTriangle } from "lucide-react";
import KPICard from "@/components/dashboard/KPICard";
import ShipmentStatusChart from "@/components/dashboard/ShipmentStatusChart";
import Card from "@/components/ui/Card";
import Spinner from "@/components/ui/Spinner";
import { useShipmentKPI, useInventoryKPI, useSupplierKPI } from "@/hooks/useAnalytics";

export default function DashboardPage() {
  const { data: shipmentKPI, isLoading: loadingShipments } = useShipmentKPI();
  const { data: inventoryKPI, isLoading: loadingInventory } = useInventoryKPI();
  const { data: supplierKPI, isLoading: loadingSuppliers } = useSupplierKPI();

  const loading = loadingShipments || loadingInventory || loadingSuppliers;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

      {loading ? (
        <div className="flex justify-center py-20">
          <Spinner />
        </div>
      ) : (
        <>
          {/* KPI row */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KPICard
              label="Total Shipments"
              value={shipmentKPI?.total ?? 0}
              icon={Truck}
            />
            <KPICard
              label="In Transit"
              value={shipmentKPI?.by_status?.in_transit ?? 0}
              icon={Truck}
            />
            <KPICard
              label="Low Stock Items"
              value={inventoryKPI?.low_stock_count ?? 0}
              icon={Package}
              trendUp={false}
            />
            <KPICard
              label="Active Suppliers"
              value={supplierKPI?.active_suppliers ?? 0}
              icon={Users}
            />
          </div>

          {/* Charts row */}
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card>
              <h2 className="mb-4 text-sm font-semibold text-gray-600 uppercase tracking-wide">
                Shipments by Status
              </h2>
              {shipmentKPI?.by_status && (
                <ShipmentStatusChart data={shipmentKPI.by_status} />
              )}
            </Card>

            <Card>
              <h2 className="mb-4 text-sm font-semibold text-gray-600 uppercase tracking-wide">
                Supplier Performance
              </h2>
              <div className="flex items-center justify-center py-8">
                <div className="text-center">
                  <p className="text-5xl font-bold text-primary-600">
                    {supplierKPI?.average_performance_score ?? "—"}
                  </p>
                  <p className="mt-2 text-sm text-gray-500">Avg. Performance Score</p>
                </div>
              </div>
              {inventoryKPI && inventoryKPI.low_stock_count > 0 && (
                <div className="mt-4 flex items-start gap-2 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-800">
                  <AlertTriangle size={16} className="mt-0.5 shrink-0" />
                  <span>
                    {inventoryKPI.low_stock_count} item(s) below reorder threshold:{" "}
                    {inventoryKPI.low_stock_skus.join(", ")}
                  </span>
                </div>
              )}
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
