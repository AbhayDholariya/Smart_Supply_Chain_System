from django.contrib import admin
from .models import OptimizedRoute


@admin.register(OptimizedRoute)
class OptimizedRouteAdmin(admin.ModelAdmin):
    list_display = ["shipment", "total_distance_km", "estimated_duration_min", "generated_at"]
