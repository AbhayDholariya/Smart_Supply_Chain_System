import apiClient from "./apiClient";
import type { Supplier, SupplierDelivery } from "@/types/supplier";
import type { PaginatedResponse } from "./shipmentService";

export const supplierService = {
  getAll: () =>
    apiClient.get<PaginatedResponse<Supplier>>("/suppliers/"),

  getById: (id: number) =>
    apiClient.get<Supplier>(`/suppliers/${id}/`),

  create: (data: Partial<Supplier>) =>
    apiClient.post<Supplier>("/suppliers/", data),

  update: (id: number, data: Partial<Supplier>) =>
    apiClient.patch<Supplier>(`/suppliers/${id}/`, data),

  getDeliveries: (supplierId?: number) =>
    apiClient.get<PaginatedResponse<SupplierDelivery>>("/suppliers/deliveries/", {
      params: supplierId ? { supplier: supplierId } : undefined,
    }),
};
