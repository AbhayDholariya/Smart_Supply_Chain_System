export interface Warehouse {
  id: number;
  name: string;
  location: string;
  capacity: number;
  latitude: number | null;
  longitude: number | null;
  created_at: string;
}

export interface Product {
  id: number;
  sku: string;
  name: string;
  description: string;
  unit: string;
  weight_kg: number | null;
  created_at: string;
}

export interface InventoryItem {
  id: number;
  warehouse: number;
  warehouse_name: string;
  product: number;
  product_name: string;
  quantity: number;
  reorder_threshold: number;
  is_low_stock: boolean;
  updated_at: string;
}
