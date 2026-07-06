import apiClient from "./apiClient";
import type { Warehouse, Product, InventoryItem } from "@/types/inventory";
import type { PaginatedResponse } from "./shipmentService";

export const inventoryService = {
  getWarehouses: () =>
    apiClient.get<PaginatedResponse<Warehouse>>("/inventory/warehouses/"),

  getProducts: () =>
    apiClient.get<PaginatedResponse<Product>>("/inventory/products/"),

  getItems: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<InventoryItem>>("/inventory/items/", { params }),

  updateItem: (id: number, data: Partial<InventoryItem>) =>
    apiClient.patch<InventoryItem>(`/inventory/items/${id}/`, data),
};
