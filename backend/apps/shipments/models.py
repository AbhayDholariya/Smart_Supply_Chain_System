from django.db import models
from django.conf import settings


class ShipmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    IN_TRANSIT = "in_transit", "In Transit"
    DELIVERED = "delivered", "Delivered"
    DELAYED = "delayed", "Delayed"
    CANCELLED = "cancelled", "Cancelled"


class Shipment(models.Model):
    tracking_number = models.CharField(max_length=50, unique=True)
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=ShipmentStatus.choices, default=ShipmentStatus.PENDING
    )
    carrier = models.CharField(max_length=100, blank=True)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_delivery = models.DateTimeField(null=True, blank=True)
    actual_delivery = models.DateTimeField(null=True, blank=True)

    # GPS coordinates (latest known location)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="shipments",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.tracking_number} — {self.status}"


class ShipmentEvent(models.Model):
    """Immutable log of every status change for a shipment."""
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name="events")
    status = models.CharField(max_length=20, choices=ShipmentStatus.choices)
    location = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return f"{self.shipment.tracking_number} → {self.status} @ {self.timestamp}"
