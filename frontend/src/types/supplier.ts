export interface Supplier {
  id: number;
  name: string;
  contact_email: string;
  contact_phone: string;
  address: string;
  country: string;
  performance_score: number;
  on_time_delivery_rate: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SupplierDelivery {
  id: number;
  supplier: number;
  expected_date: string;
  actual_date: string | null;
  status: "on_time" | "late" | "partial" | "failed";
  notes: string;
  created_at: string;
}
