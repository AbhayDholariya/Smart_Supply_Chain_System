from rest_framework import viewsets
from .models import Supplier, SupplierDelivery
from .serializers import SupplierSerializer, SupplierDeliverySerializer


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class SupplierDeliveryViewSet(viewsets.ModelViewSet):
    queryset = SupplierDelivery.objects.select_related("supplier")
    serializer_class = SupplierDeliverySerializer
