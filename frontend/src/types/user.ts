export type Role =
  | "admin"
  | "supplier"
  | "warehouse_manager"
  | "transporter"
  | "customer";

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
  phone: string;
  avatar: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}
