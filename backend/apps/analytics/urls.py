from django.urls import path
from .views import ShipmentKPIView, InventoryKPIView, SupplierKPIView

urlpatterns = [
    path("shipments/", ShipmentKPIView.as_view(), name="analytics-shipments"),
    path("inventory/", InventoryKPIView.as_view(), name="analytics-inventory"),
    path("suppliers/", SupplierKPIView.as_view(), name="analytics-suppliers"),
]
