from rest_framework import serializers
from .models import Supplier, SupplierDelivery


class SupplierDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierDelivery
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    deliveries = SupplierDeliverySerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]
