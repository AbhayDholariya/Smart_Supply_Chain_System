from django.contrib import admin
from .models import Warehouse, Product, InventoryItem


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ["name", "location", "capacity"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "unit", "weight_kg"]
    search_fields = ["sku", "name"]


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["product", "warehouse", "quantity", "reorder_threshold", "is_low_stock"]
    list_filter = ["warehouse"]
