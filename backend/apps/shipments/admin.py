from django.contrib import admin
from .models import Shipment, ShipmentEvent


class ShipmentEventInline(admin.TabularInline):
    model = ShipmentEvent
    extra = 0
    readonly_fields = ["timestamp"]


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ["tracking_number", "origin", "destination", "status", "carrier", "estimated_delivery"]
    list_filter = ["status", "carrier"]
    search_fields = ["tracking_number", "origin", "destination"]
    inlines = [ShipmentEventInline]
