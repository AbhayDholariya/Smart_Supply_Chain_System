from django.db import models
from django.conf import settings


class NotificationType(models.TextChoices):
    SHIPMENT_DELAY = "shipment_delay", "Shipment Delay"
    LOW_STOCK = "low_stock", "Low Stock"
    DELIVERY_STATUS = "delivery_status", "Delivery Status"
    SUPPLIER_ISSUE = "supplier_issue", "Supplier Issue"
    SYSTEM = "system", "System"


class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=30, choices=NotificationType.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.notification_type}] {self.title} → {self.recipient.email}"
