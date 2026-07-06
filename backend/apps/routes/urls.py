from rest_framework.routers import DefaultRouter
from .views import OptimizedRouteViewSet

router = DefaultRouter()
router.register(r"", OptimizedRouteViewSet, basename="route")
urlpatterns = router.urls
