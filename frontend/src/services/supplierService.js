import apiClient from "./apiClient";

export const supplierService = {
  getAll: () =>
    apiClient.get("/suppliers/"),

  getById: (id) =>
    apiClient.get(`/suppliers/${id}/`),

  create: (data) =>
    apiClient.post("/suppliers/", data),

  update: (id, data) =>
    apiClient.patch(`/suppliers/${id}/`, data),

  getDeliveries: (supplierId) =>
    apiClient.get("/suppliers/deliveries/", {
      params: supplierId ? { supplier: supplierId } : undefined,
    }),
};
