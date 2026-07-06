"""
Analytics views — aggregate KPI data for the dashboard.
Each endpoint is read-only and intended for chart/report consumption.
"""
from django.db.models import Count, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.shipments.models import Shipment, ShipmentStatus
from apps.inventory.models import InventoryItem
from apps.suppliers.models import Supplier


class ShipmentKPIView(APIView):
    """High-level shipment statistics."""
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        qs = Shipment.objects.all()
        data = {
            "total": qs.count(),
            "by_status": {
                s: qs.filter(status=s).count() for s in ShipmentStatus.values
            },
        }
        return Response(data)


class InventoryKPIView(APIView):
    """Low-stock items and overall stock health."""
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        items = InventoryItem.objects.all()
        low_stock = [i for i in items if i.is_low_stock]
        return Response({
            "total_items": items.count(),
            "low_stock_count": len(low_stock),
            "low_stock_skus": [i.product.sku for i in low_stock],
        })


class SupplierKPIView(APIView):
    """Supplier performance overview."""
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        avg_score = Supplier.objects.aggregate(avg=Avg("performance_score"))["avg"]
        return Response({
            "total_suppliers": Supplier.objects.count(),
            "active_suppliers": Supplier.objects.filter(is_active=True).count(),
            "average_performance_score": round(avg_score or 0, 2),
        })
