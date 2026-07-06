import apiClient from "./apiClient";
import axios from "axios";
import type { AuthTokens, User } from "@/types/user";

const BASE = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const authService = {
  login: (email: string, password: string) =>
    apiClient.post<AuthTokens>("/auth/token/", { email, password }),

  // Accepts a fresh access token so it can be called immediately after login,
  // before the Zustand store has been updated.
  getMe: (accessToken?: string) =>
    apiClient.get<User>("/users/me/", {
      headers: accessToken ? { Authorization: `Bearer ${accessToken}` } : undefined,
    }),

  register: (payload: {
    username: string;
    email: string;
    password: string;
    role: string;
    phone?: string;
  }) => apiClient.post<User>("/users/register/", payload),

  changePassword: (old_password: string, new_password: string) =>
    apiClient.post("/users/change-password/", { old_password, new_password }),
};
