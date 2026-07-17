from rest_framework import serializers


class ShipmentSerializer(serializers.Serializer):
    id = serializers.CharField()
    origin = serializers.CharField(allow_blank=True)
    destination = serializers.CharField(allow_blank=True)
    carrier = serializers.CharField(allow_blank=True)
    lat = serializers.FloatField()
    lng = serializers.FloatField()
    status = serializers.CharField(allow_blank=True)
    risk_score = serializers.FloatField()
    risk_level = serializers.CharField(allow_blank=True)
    is_anomaly = serializers.BooleanField()
    speed_kmh = serializers.FloatField()
    progress = serializers.FloatField()
    cargo_type = serializers.CharField(allow_blank=True)
    value_usd = serializers.IntegerField()
    eta_days = serializers.FloatField(required=False, allow_null=True)
    top_risk_factors = serializers.ListField(child=serializers.CharField())
    last_updated = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class AlertSerializer(serializers.Serializer):
    id = serializers.CharField()
    shipment_id = serializers.CharField()
    type = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    risk_score = serializers.FloatField()
    alternate_routes = serializers.ListField(child=serializers.DictField(), required=False, default=list)
    created_at = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class RerouteRequestSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True, default="manual_trigger")
    priority = serializers.CharField(required=False, allow_blank=True, default="normal")


class RerouteResponseSerializer(serializers.Serializer):
    shipment_id = serializers.CharField()
    current_risk_score = serializers.FloatField()
    routes = serializers.ListField(child=serializers.DictField())
    recommended_route_idx = serializers.IntegerField()
    analysis = serializers.CharField()


class RiskUpdateWebhookSerializer(serializers.Serializer):
    shipment_id = serializers.CharField()
    risk_score = serializers.FloatField()
    risk_level = serializers.CharField()
    is_anomaly = serializers.BooleanField()
    anomaly_score = serializers.FloatField()
    top_risk_factors = serializers.ListField(child=serializers.CharField())
    recommended_action = serializers.CharField()
