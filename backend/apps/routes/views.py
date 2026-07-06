from rest_framework import viewsets
from .models import OptimizedRoute
from .serializers import OptimizedRouteSerializer


class OptimizedRouteViewSet(viewsets.ModelViewSet):
    queryset = OptimizedRoute.objects.select_related("shipment")
    serializer_class = OptimizedRouteSerializer
