import apiClient from "./apiClient";
import type { ShipmentKPI, InventoryKPI, SupplierKPI } from "@/types/analytics";

export const analyticsService = {
  getShipmentKPI: () =>
    apiClient.get<ShipmentKPI>("/analytics/shipments/"),

  getInventoryKPI: () =>
    apiClient.get<InventoryKPI>("/analytics/inventory/"),

  getSupplierKPI: () =>
    apiClient.get<SupplierKPI>("/analytics/suppliers/"),
};
