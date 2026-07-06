import apiClient from "./apiClient";
import type { Notification } from "@/types/notification";
import type { PaginatedResponse } from "./shipmentService";

export const notificationService = {
  getAll: () =>
    apiClient.get<PaginatedResponse<Notification>>("/notifications/"),

  markAllRead: () =>
    apiClient.post("/notifications/mark-all-read/"),
};
