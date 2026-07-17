import apiClient from "./apiClient";

export const inventoryService = {
  getWarehouses: () =>
    apiClient.get("/inventory/warehouses/"),

  getProducts: () =>
    apiClient.get("/inventory/products/"),

  getItems: (params) =>
    apiClient.get("/inventory/items/", { params }),

  updateItem: (id, data) =>
    apiClient.patch(`/inventory/items/${id}/`, data),
};
