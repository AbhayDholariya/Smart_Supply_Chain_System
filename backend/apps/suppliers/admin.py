from django.contrib import admin
from .models import Supplier, SupplierDelivery


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_email", "country", "performance_score", "is_active"]
    list_filter = ["is_active", "country"]
    search_fields = ["name", "contact_email"]


@admin.register(SupplierDelivery)
class SupplierDeliveryAdmin(admin.ModelAdmin):
    list_display = ["supplier", "expected_date", "actual_date", "status"]
    list_filter = ["status"]
