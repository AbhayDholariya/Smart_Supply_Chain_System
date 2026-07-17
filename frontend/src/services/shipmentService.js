
import apiClient from "./apiClient";

export const shipmentService = {
  getLiveShipments: () =>
    apiClient.get("/shipments/"),

  getShipmentById: (id) =>
    apiClient.get(`/shipments/${id}/`),

  rerouteShipment: (id, data) =>
    apiClient.post(`/shipments/${id}/reroute/`, data),
};

export const alertService = {
  getAlerts: (hours = 1) =>
    apiClient.get("/alerts/", { params: { hours } }),
};
