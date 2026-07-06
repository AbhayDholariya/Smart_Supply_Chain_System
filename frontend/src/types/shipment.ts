export type ShipmentStatus =
  | "pending"
  | "in_transit"
  | "delivered"
  | "delayed"
  | "cancelled";

export interface ShipmentEvent {
  id: number;
  status: ShipmentStatus;
  location: string;
  note: string;
  timestamp: string;
}

export interface Shipment {
  id: number;
  tracking_number: string;
  origin: string;
  destination: string;
  status: ShipmentStatus;
  carrier: string;
  weight_kg: number | null;
  estimated_delivery: string | null;
  actual_delivery: string | null;
  current_latitude: number | null;
  current_longitude: number | null;
  customer: number | null;
  events: ShipmentEvent[];
  created_at: string;
  updated_at: string;
}
