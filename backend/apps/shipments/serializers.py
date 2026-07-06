from rest_framework import serializers
from .models import Shipment, ShipmentEvent


class ShipmentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentEvent
        fields = ["id", "status", "location", "note", "timestamp"]


class ShipmentSerializer(serializers.ModelSerializer):
    events = ShipmentEventSerializer(many=True, read_only=True)

    class Meta:
        model = Shipment
        fields = "__all__"
        read_only_fields = ["id", "tracking_number", "created_at", "updated_at"]
