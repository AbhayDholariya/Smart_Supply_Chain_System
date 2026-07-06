from rest_framework import viewsets
from .models import Warehouse, Product, InventoryItem
from .serializers import WarehouseSerializer, ProductSerializer, InventoryItemSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.select_related("warehouse", "product")
    serializer_class = InventoryItemSerializer
