import apiClient from "./apiClient";

export const notificationService = {
  getAll: () =>
    apiClient.get("/notifications/"),

  markAllRead: () =>
    apiClient.post("/notifications/mark-all-read/"),
};
