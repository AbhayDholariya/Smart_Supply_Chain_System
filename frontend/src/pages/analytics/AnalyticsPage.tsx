import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import Card from "@/components/ui/Card";
import Spinner from "@/components/ui/Spinner";
import { useShipmentKPI, useInventoryKPI, useSupplierKPI } from "@/hooks/useAnalytics";

export default function AnalyticsPage() {
  const { data: shipmentKPI, isLoading: ls } = useShipmentKPI();
  const { data: inventoryKPI, isLoading: li } = useInventoryKPI();
  const { data: supplierKPI, isLoading: lsu } = useSupplierKPI();

  if (ls || li || lsu) {
    return (
      <div className="flex justify-center py-20">
        <Spinner />
      </div>
    );
  }

  const statusChartData = shipmentKPI
    ? Object.entries(shipmentKPI.by_status).map(([name, value]) => ({
        name: name.replace("_", " "),
        value,
      }))
    : [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Shipments by status */}
        <Card>
          <h2 className="mb-4 font-semibold text-gray-700">Shipments by Status</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={statusChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="name" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Inventory health */}
        <Card>
          <h2 className="mb-4 font-semibold text-gray-700">Inventory Health</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-lg bg-gray-50 p-4 text-center">
              <p className="text-3xl font-bold text-gray-900">{inventoryKPI?.total_items ?? 0}</p>
              <p className="text-xs text-gray-500">Total Items</p>
            </div>
            <div className="rounded-lg bg-red-50 p-4 text-center">
              <p className="text-3xl font-bold text-red-600">{inventoryKPI?.low_stock_count ?? 0}</p>
              <p className="text-xs text-red-500">Low Stock</p>
            </div>
          </div>
          {inventoryKPI?.low_stock_skus.length ? (
            <div className="mt-4">
              <p className="text-xs font-medium text-gray-500 mb-1">Low stock SKUs</p>
              <div className="flex flex-wrap gap-1">
                {inventoryKPI.low_stock_skus.map((sku) => (
                  <span key={sku} className="rounded bg-red-100 px-2 py-0.5 text-xs text-red-700">
                    {sku}
                  </span>
                ))}
              </div>
            </div>
          ) : null}
        </Card>

        {/* Supplier summary */}
        <Card className="lg:col-span-2">
          <h2 className="mb-4 font-semibold text-gray-700">Supplier Overview</h2>
          <div className="grid grid-cols-3 gap-4">
            {[
              ["Total Suppliers", supplierKPI?.total_suppliers],
              ["Active", supplierKPI?.active_suppliers],
              ["Avg. Score", supplierKPI?.average_performance_score],
            ].map(([label, val]) => (
              <div key={label as string} className="rounded-lg bg-gray-50 p-4 text-center">
                <p className="text-3xl font-bold text-primary-600">{val ?? "—"}</p>
                <p className="text-xs text-gray-500">{label as string}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
