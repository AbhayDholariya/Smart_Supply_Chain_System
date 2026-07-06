import apiClient from "./apiClient";
import type { Shipment } from "@/types/shipment";

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const shipmentService = {
  getAll: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Shipment>>("/shipments/", { params }),

  getById: (id: number) =>
    apiClient.get<Shipment>(`/shipments/${id}/`),

  create: (data: Partial<Shipment>) =>
    apiClient.post<Shipment>("/shipments/", data),

  update: (id: number, data: Partial<Shipment>) =>
    apiClient.patch<Shipment>(`/shipments/${id}/`, data),

  delete: (id: number) =>
    apiClient.delete(`/shipments/${id}/`),
};
