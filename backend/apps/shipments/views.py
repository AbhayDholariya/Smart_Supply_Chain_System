from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Shipment
from .serializers import ShipmentSerializer


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.select_related("customer").prefetch_related("events")
    serializer_class = ShipmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "carrier"]
    search_fields = ["tracking_number", "origin", "destination"]
    ordering_fields = ["created_at", "estimated_delivery"]
