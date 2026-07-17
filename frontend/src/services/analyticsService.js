
import { shipmentService, alertService } from "./shipmentService";

export const analyticsService = {
  getShipmentKPI: async () => {
    const response = await shipmentService.getLiveShipments();
    const shipments = response.data;
    
    // Calculate KPI's
    const by_status = {};
    shipments.forEach(shipment => {
      const status = shipment.status || "unknown";
      by_status[status] = (by_status[status] || 0) + 1;
    });

    return {
      data: {
        total: shipments.length,
        by_status: by_status
      }
    };
  },
  
  getInventoryKPI: async () => {
    // Mock data for now
    return {
      data: {
        low_stock_count: 2,
        low_stock_skus: ["SKU-1234", "SKU-5678"]
      }
    };
  },
  
  getSupplierKPI: async () => {
    // Mock data for now
    return {
      data: {
        active_suppliers: 12,
        average_performance_score: 85
      }
    };
  }
};
