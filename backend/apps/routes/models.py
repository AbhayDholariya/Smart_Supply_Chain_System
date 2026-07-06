from django.db import models
from apps.shipments.models import Shipment


class OptimizedRoute(models.Model):
    """Stores a route recommendation produced by the AI route optimizer."""

    shipment = models.OneToOneField(
        Shipment, on_delete=models.CASCADE, related_name="optimized_route"
    )
    waypoints = models.JSONField(default=list, help_text="Ordered list of lat/lng waypoints")
    total_distance_km = models.FloatField(null=True, blank=True)
    estimated_duration_min = models.FloatField(null=True, blank=True)
    traffic_conditions = models.CharField(max_length=50, blank=True)
    weather_conditions = models.CharField(max_length=50, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Route for {self.shipment.tracking_number}"
