from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Supplier(models.Model):
    name = models.CharField(max_length=200)
    contact_email = models.EmailField(unique=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    # Performance score 0-100
    performance_score = models.FloatField(
        default=100.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
    )
    on_time_delivery_rate = models.FloatField(default=1.0)  # 0.0 – 1.0
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class SupplierDelivery(models.Model):
    """Historical record of deliveries from a supplier."""

    class DeliveryStatus(models.TextChoices):
        ON_TIME = "on_time", "On Time"
        LATE = "late", "Late"
        PARTIAL = "partial", "Partial"
        FAILED = "failed", "Failed"

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="deliveries")
    expected_date = models.DateField()
    actual_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=DeliveryStatus.choices)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.supplier.name} — {self.status} ({self.expected_date})"
