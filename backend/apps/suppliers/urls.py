from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, SupplierDeliveryViewSet

router = DefaultRouter()
router.register(r"", SupplierViewSet, basename="supplier")
router.register(r"deliveries", SupplierDeliveryViewSet, basename="supplier-delivery")
urlpatterns = router.urls
