from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ShipmentViewSet,
    AlertViewSet,
    RiskUpdateWebhookView,
    root_redirect,
    health_check
)

router = DefaultRouter()
router.register(r"shipments", ShipmentViewSet, basename="shipment")
router.register(r"alerts", AlertViewSet, basename="alert")

urlpatterns = [
    path("", root_redirect, name="root-redirect"),
    path("health", health_check, name="health-check"),
    path("api/v1/", include(router.urls)),
    path("api/v1/webhook/risk-update", RiskUpdateWebhookView.as_view(), name="risk-update-webhook"),
]
