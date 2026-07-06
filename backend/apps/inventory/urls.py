from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, ProductViewSet, InventoryItemViewSet

router = DefaultRouter()
router.register(r"warehouses", WarehouseViewSet, basename="warehouse")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"items", InventoryItemViewSet, basename="inventory-item")
urlpatterns = router.urls
