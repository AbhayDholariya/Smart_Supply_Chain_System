"""Root URL configuration."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

API_PREFIX = "api/v1/"


def api_root(request):
    """Human-friendly index of all available API endpoints."""
    base = request.build_absolute_uri("/")[:-1]  # e.g. http://127.0.0.1:8000
    return JsonResponse({
        "message": "Welcome to Smart Supply Chain System API",
        "version": "v1",
        "endpoints": {
            "admin":         f"{base}/admin/",
            "auth_token":    f"{base}/api/v1/auth/token/",
            "auth_refresh":  f"{base}/api/v1/auth/token/refresh/",
            "auth_verify":   f"{base}/api/v1/auth/token/verify/",
            "users":         f"{base}/api/v1/users/",
            "shipments":     f"{base}/api/v1/shipments/",
            "inventory":     f"{base}/api/v1/inventory/",
            "suppliers":     f"{base}/api/v1/suppliers/",
            "routes":        f"{base}/api/v1/routes/",
            "analytics":     f"{base}/api/v1/analytics/",
            "notifications": f"{base}/api/v1/notifications/",
            "ai_predict":    f"{base}/api/v1/ai/predict-delay/",
            "ai_route":      f"{base}/api/v1/ai/recommend-route/",
        },
    })


urlpatterns = [
    # Root → show API index
    path("", api_root, name="api-root"),

    # /api/ and /api/v1/ → redirect to root for convenience
    path("api/", RedirectView.as_view(url="/", permanent=False)),
    path("api/v1/", api_root, name="api-v1-root"),

    # Django admin
    path("admin/", admin.site.urls),

    # JWT auth
    path(f"{API_PREFIX}auth/token/",         TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(f"{API_PREFIX}auth/token/refresh/", TokenRefreshView.as_view(),    name="token_refresh"),
    path(f"{API_PREFIX}auth/token/verify/",  TokenVerifyView.as_view(),     name="token_verify"),

    # App routers
    path(f"{API_PREFIX}users/",         include("apps.users.urls")),
    path(f"{API_PREFIX}shipments/",     include("apps.shipments.urls")),
    path(f"{API_PREFIX}inventory/",     include("apps.inventory.urls")),
    path(f"{API_PREFIX}suppliers/",     include("apps.suppliers.urls")),
    path(f"{API_PREFIX}routes/",        include("apps.routes.urls")),
    path(f"{API_PREFIX}analytics/",     include("apps.analytics.urls")),
    path(f"{API_PREFIX}notifications/", include("apps.notifications.urls")),
    path(f"{API_PREFIX}ai/",            include("apps.ai_engine.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
