import apiClient from "./apiClient";
import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const authService = {
  login: (email, password) =>
    apiClient.post("/auth/token/", { email, password }),

  // Accepts a fresh access token so it can be called immediately after login,
  // before the Zustand store has been updated.
  getMe: (accessToken) =>
    apiClient.get("/users/me/", {
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
    }),

  register: (payload) => apiClient.post("/users/register/", payload),

  changePassword: (old_password, new_password) =>
    apiClient.post("/users/change-password/", { old_password, new_password }),
};
