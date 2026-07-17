from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.in_memory_store import InMemoryStore
from core.consumers import manager
from .serializers import (
    ShipmentSerializer,
    AlertSerializer,
    RerouteRequestSerializer,
    RerouteResponseSerializer,
    RiskUpdateWebhookSerializer
)
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from datetime import datetime, timezone
import json
import asyncio
from asgiref.sync import async_to_sync


store = InMemoryStore()


class ShipmentViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        shipments = store.get_all_active_shipments()
        serializer = ShipmentSerializer(shipments, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        shipment = store.get_shipment(pk)
        if not shipment:
            return Response({"detail": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="reroute")
    def reroute(self, request, pk=None):
        shipment = store.get_shipment(pk)
        if not shipment:
            return Response({"detail": "Shipment not found"}, status=status.HTTP_404_NOT_FOUND)

        req_serializer = RerouteRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)
        req_data = req_serializer.validated_data

        current_risk = float(shipment.get("risk_score", 50))
        origin = shipment.get("origin", "Mumbai")
        destination = shipment.get("destination", "Rotterdam")

        routes_payload = []
        analysis = "Route optimization not available (ML modules not loaded)."

        # Try to import RouteOptimizer (same as fastapi_backend_main
        try:
            from ML.logistics_firm.route_optimizer import RouteOptimizer
            optimizer = RouteOptimizer()
            routes = optimizer.get_alternate_routes(
                origin=origin,
                destination=destination,
                original_cost=shipment.get("value_usd", 3000) * 0.02,
                original_days=float(shipment.get("transit_days", 25))
            )
            for idx, r in enumerate(routes):
                routes_payload.append({
                    "rank": idx + 1,
                    "path": r.path,
                    "total_cost_usd": r.total_cost_usd,
                    "transit_days": r.transit_days,
                    "composite_risk": r.composite_risk,
                    "carriers": r.carriers,
                    "summary": r.summary,
                    "savings_vs_original": r.savings_vs_original
                })

            best = routes[0] if routes else None
            analysis = (
                f"Reroute analysis for {pk}: Current risk {current_risk:.0f}/100. "
                f"Best alternate via {' > '.join(best.path[1:-1] or ['direct'])} "
                f"saves {abs(best.savings_vs_original.get('time_delta_days', 0)):.1f} days "
                f"at a cost delta of ${best.savings_vs_original.get('cost_delta_usd', 0):+,.0f}."
            ) if best else "No alternate routes found."
        except Exception as e:
            pass

        # Save alert and broadcast (same as fastapi
        import uuid
        alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
        alert_data = {
            "id": alert_id,
            "shipment_id": pk,
            "type": "reroute_recommendation",
            "severity": "high" if current_risk > 75 else "medium",
            "message": analysis,
            "risk_score": current_risk,
            "alternate_routes": routes_payload
        }
        store.push_alert(alert_data)

        # Broadcast alert to WebSocket clients
        async_to_sync(manager.broadcast)("alerts", {
            "event": "reroute_recommendation",
            "data": alert_data
        })

        response_data = {
            "shipment_id": pk,
            "current_risk_score": current_risk,
            "routes": routes_payload,
            "recommended_route_idx": 0,
            "analysis": analysis
        }
        serializer = RerouteResponseSerializer(data=response_data)
        return Response(serializer.data)


class AlertViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        hours = int(request.query_params.get("hours", 1))
        alerts = store.get_recent_alerts(hours=hours)
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)


class RiskUpdateWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RiskUpdateWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        store.update_risk_score(
            payload["shipment_id"],
            payload["risk_score"],
            payload["risk_level"],
            payload["is_anomaly"],
        )

        # Broadcast shipment update
        async_to_sync(manager.broadcast)("shipments", {
            "event": "risk_updated",
            "shipment_id": payload["shipment_id"],
            "risk_score": payload["risk_score"],
            "risk_level": payload["risk_level"],
            "is_anomaly": payload["is_anomaly"]
        })

        if payload["risk_score"] > 70 or payload["is_anomaly"]:
            alert_data = {
                "shipment_id": payload["shipment_id"],
                "type": "anomaly_detected" if payload["is_anomaly"] else "high_risk_flag",
                "severity": "critical" if payload["risk_score"] > 85 else "high",
                "message": payload["recommended_action"],
                "risk_score": payload["risk_score"],
                "top_risk_factors": payload["top_risk_factors"],
                "alternate_routes": []
            }
            store.push_alert(alert_data)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)


# Root redirect to /docs
def root_redirect(request):
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect("/docs/")


# Health check
def health_check(request):
    return JsonResponse({"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()})
