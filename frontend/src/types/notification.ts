export type NotificationType =
  | "shipment_delay"
  | "low_stock"
  | "delivery_status"
  | "supplier_issue"
  | "system";

export interface Notification {
  id: number;
  recipient: number;
  notification_type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}
