export interface ShipmentKPI {
  total: number;
  by_status: Record<string, number>;
}

export interface InventoryKPI {
  total_items: number;
  low_stock_count: number;
  low_stock_skus: string[];
}

export interface SupplierKPI {
  total_suppliers: number;
  active_suppliers: number;
  average_performance_score: number;
}
