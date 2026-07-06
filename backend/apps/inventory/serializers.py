from rest_framework import serializers
from .models import Warehouse, Product, InventoryItem


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class InventoryItemSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.BooleanField(read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    warehouse_name = serializers.CharField(source="warehouse.name", read_only=True)

    class Meta:
        model = InventoryItem
        fields = "__all__"
