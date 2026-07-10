# backend/main.py
"""
FastAPI backend with:
  - GET  /shipments/live
  - GET  /alerts
  - POST /reroute/{shipment_id}
  - WS   /ws/{topic}
  - POST /webhook/risk-update  (called internally by Cloud Function bridge)
"""

import sys
import os
# Ensure project root is on the path when running this file directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import os
import uuid
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from backend.in_memory_store import InMemoryStore
from backend.websocket_manager import ConnectionManager

# Try to import ML modules (lazy import with fallback)
try:
    from ML.logistics_firm.route_optimizer import RouteOptimizer
    _HAS_ROUTE_OPTIMIZER = True
except Exception as _e:
    _HAS_ROUTE_OPTIMIZER = False
    RouteOptimizer = None
    print(f"[Main] RouteOptimizer not loaded: {_e}")

try:
    from ML.logistics_firm.risk_scorer import RiskScorer, RiskInput
    _HAS_RISK_SCORER = True
except Exception as _e:
    _HAS_RISK_SCORER = False
    RiskScorer = None
    RiskInput = None
    print(f"[Main] RiskScorer not loaded: {_e}")

try:
    from ML.logistics_firm.anomaly_detector import ShipmentAnomalyDetector
    _HAS_ANOMALY_DETECTOR = True
except Exception as _e:
    _HAS_ANOMALY_DETECTOR = False
    ShipmentAnomalyDetector = None
    print(f"[Main] ShipmentAnomalyDetector not loaded: {_e}")

# Import existing API routes
try:
    from backend.logistics_firm.api import router as api_router
    _HAS_API_ROUTES = True
except Exception:
    _HAS_API_ROUTES = False

# Import new Indian supply chain API
try:
    from backend.ecommerce_b2b.api import router as india_router
    _HAS_INDIA_ROUTES = True
except Exception as _e:
    _HAS_INDIA_ROUTES = False
    print(f"[Main] Indian API router not loaded: {_e}")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ─── Globals ─────────────────────────────────────────────────────────────────
store = InMemoryStore()         # Replaces Firebase
ws_manager = ConnectionManager()
scorer = RiskScorer() if _HAS_RISK_SCORER else None
detector = ShipmentAnomalyDetector() if _HAS_ANOMALY_DETECTOR else None
FLASK_AI_URL = os.getenv("FLASK_AI_URL", "http://localhost:5001")

# ─── Main API Router ─────────────────────────────────────────────────────────
main_router = APIRouter(prefix="/api/v1")


# ─── Lifespan ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Supply Chain AI Backend (Firebase-free)...")
    # Start background store listener that pushes to WebSocket
    listener_task = asyncio.create_task(store_change_listener())
    yield
    listener_task.cancel()
    logger.info("Shutting down...")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Supply Chain Intelligence API",
    description="Real-time shipment tracking with AI disruption detection",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount main API router first
app.include_router(main_router)

# Mount additional API routes
if _HAS_API_ROUTES:
    app.include_router(api_router)

# Mount Indian supply chain API
if _HAS_INDIA_ROUTES:
    app.include_router(india_router)


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class ShipmentResponse(BaseModel):
    id: str
    origin: str
    destination: str
    carrier: str
    lat: float
    lng: float
    status: str
    risk_score: float
    risk_level: str
    is_anomaly: bool
    speed_kmh: float
    progress: float
    cargo_type: str
    value_usd: int
    eta_days: Optional[float] = None
    top_risk_factors: list[str] = []
    last_updated: Optional[Any] = None


class AlertResponse(BaseModel):
    id: str
    shipment_id: str
    type: str
    severity: str
    message: str
    risk_score: float
    alternate_routes: list[dict] = []
    created_at: Optional[Any] = None


class RerouteRequest(BaseModel):
    reason: Optional[str] = Field(default="manual_trigger")
    priority: Optional[str] = Field(default="normal")


class RerouteResponse(BaseModel):
    shipment_id: str
    current_risk_score: float
    routes: list[dict]
    recommended_route_idx: int
    analysis: str


class RiskUpdateWebhook(BaseModel):
    shipment_id: str
    risk_score: float
    risk_level: str
    is_anomaly: bool
    anomaly_score: float
    top_risk_factors: list[str]
    recommended_action: str


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@main_router.get("/shipments/live", response_model=list[ShipmentResponse])
async def get_live_shipments():
    """
    Returns all active shipments with current position, risk score, and ETA.
    """
    try:
        raw_shipments = store.get_all_active_shipments()
        # Show all shipments (no panel filter)
        result = []
        for s in raw_shipments:
            # Compute ETA from progress
            progress = float(s.get("progress", 0.5))
            transit_days = float(s.get("transit_days", 20))
            eta_days = None
            if progress > 0 and progress < 1:
                elapsed_fraction = progress
                total_est = transit_days / elapsed_fraction if elapsed_fraction > 0 else 25
                eta_days = round(total_est * (1 - progress), 1)

            result.append(ShipmentResponse(
                id=s["id"],
                origin=s.get("origin", ""),
                destination=s.get("destination", ""),
                carrier=s.get("carrier", "Unknown"),
                lat=float(s.get("lat", 0)),
                lng=float(s.get("lng", 0)),
                status=s.get("status", "unknown"),
                risk_score=float(s.get("risk_score", 0)),
                risk_level=s.get("risk_level", "unknown"),
                is_anomaly=bool(s.get("is_anomaly", False)),
                speed_kmh=float(s.get("speed_kmh", 0)),
                progress=float(s.get("progress", 0)),
                cargo_type=s.get("cargo_type", "General"),
                value_usd=int(s.get("value_usd", 0)),
                eta_days=eta_days,
                top_risk_factors=s.get("top_risk_factors", []),
                last_updated=s.get("last_updated"),
            ))

        return result

    except Exception as e:
        logger.exception(f"Error fetching live shipments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@main_router.get("/alerts", response_model=list[AlertResponse])
async def get_alerts(hours: int = 1):
    """
    Returns all disruptions detected in the last N hours.
    """
    try:
        raw_alerts = store.get_recent_alerts(hours=hours)
        # Show all alerts (no panel filter)
        result = []
        for a in raw_alerts:
            result.append(AlertResponse(
                id=a.get("id", ""),
                shipment_id=a.get("shipment_id", ""),
                type=a.get("type", "unknown"),
                severity=a.get("severity", "medium"),
                message=a.get("message", ""),
                risk_score=float(a.get("risk_score", 0)),
                alternate_routes=a.get("alternate_routes", []),
                created_at=a.get("created_at"),
            ))
        return result

    except Exception as e:
        logger.exception(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@main_router.post("/reroute/{shipment_id}", response_model=RerouteResponse)
async def reroute_shipment(
    shipment_id: str,
    body: RerouteRequest,
    background_tasks: BackgroundTasks,
):
    """
    Triggers route recalculation and returns top 3 alternate routes.
    Auto-triggered when risk > 70; can also be called manually.
    """
    try:
        shipment = store.get_shipment(shipment_id)
        if not shipment:
            raise HTTPException(status_code=404, detail=f"Shipment {shipment_id} not found")

        current_risk = float(shipment.get("risk_score", 50))
        origin = shipment.get("origin", "Mumbai")
        destination = shipment.get("destination", "Rotterdam")

        routes_payload = []
        analysis = "Route optimization not available (ML modules not loaded)."
        
        if _HAS_ROUTE_OPTIMIZER and RouteOptimizer is not None:
            optimizer = RouteOptimizer()
            routes = optimizer.get_alternate_routes(
                origin=origin,
                destination=destination,
                original_cost=shipment.get("value_usd", 3000) * 0.02,
                original_days=float(shipment.get("transit_days", 25)),
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
                    "savings_vs_original": r.savings_vs_original,
                })

            best = routes[0] if routes else None
            analysis = (
                f"Reroute analysis for {shipment_id}: Current risk {current_risk:.0f}/100. "
                f"Best alternate via {' > '.join(best.path[1:-1] or ['direct'])} "
                f"saves {abs(best.savings_vs_original.get('time_delta_days', 0)):.1f} days "
                f"at a cost delta of ${best.savings_vs_original.get('cost_delta_usd', 0):+,.0f}."
                if best else "No alternate routes found."
            )

        # Save reroute alert to store
        alert_id = f"ALT-{uuid.uuid4().hex[:6].upper()}"
        alert_data = {
            "id": alert_id,
            "shipment_id": shipment_id,
            "type": "reroute_recommendation",
            "severity": "high" if current_risk > 75 else "medium",
            "message": analysis,
            "risk_score": current_risk,
            "alternate_routes": routes_payload,
        }
        background_tasks.add_task(store.push_alert, alert_data)

        # Broadcast via WebSocket
        background_tasks.add_task(ws_manager.broadcast, "alerts", {
            "event": "reroute_recommendation",
            "data": alert_data,
        })

        return RerouteResponse(
            shipment_id=shipment_id,
            current_risk_score=current_risk,
            routes=routes_payload,
            recommended_route_idx=0,
            analysis=analysis,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error computing reroute for {shipment_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@main_router.post("/webhook/risk-update")
async def receive_risk_update(payload: RiskUpdateWebhook, background_tasks: BackgroundTasks):
    """
    Called internally (or by Cloud Function bridge) when AI risk analysis completes.
    Writes back to Firestore and broadcasts via WebSocket.
    """
    try:
        # Update in-memory store
        store.update_risk_score(
            payload.shipment_id,
            payload.risk_score,
            payload.risk_level,
            payload.is_anomaly,
        )

        # Generate alert if high risk
        if payload.risk_score > 70 or payload.is_anomaly:
            alert_data = {
                "shipment_id": payload.shipment_id,
                "type": "anomaly_detected" if payload.is_anomaly else "high_risk_flag",
                "severity": "critical" if payload.risk_score > 85 else "high",
                "message": payload.recommended_action,
                "risk_score": payload.risk_score,
                "top_risk_factors": payload.top_risk_factors,
                "alternate_routes": [],
            }
            background_tasks.add_task(store.push_alert, alert_data)

            # Trigger auto-reroute for critical risk
            if payload.risk_score > 75:
                background_tasks.add_task(_auto_reroute, payload.shipment_id, payload.risk_score)

        # Broadcast to WebSocket clients
        background_tasks.add_task(ws_manager.broadcast, "shipments", {
            "event": "risk_updated",
            "shipment_id": payload.shipment_id,
            "risk_score": payload.risk_score,
            "risk_level": payload.risk_level,
            "is_anomaly": payload.is_anomaly,
        })

        return {"status": "ok"}

    except Exception as e:
        logger.exception(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── WebSocket ────────────────────────────────────────────────────────────────

@app.websocket("/ws/{topic}")
async def websocket_endpoint(websocket: WebSocket, topic: str):
    """
    Real-time WebSocket.
    Topics: "all", "shipments", "alerts", "shipment:SHP-4421"
    """
    await ws_manager.connect(websocket, topic)
    try:
        # Send initial state snapshot
        if topic in ("all", "shipments"):
            shipments = store.get_all_active_shipments()
            await ws_manager.send_personal(websocket, {
                "event": "initial_state",
                "shipments": shipments,
            })

        # Keep connection alive; listen for client pings
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await ws_manager.send_personal(websocket, {"event": "pong"})

    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket, topic)


# ─── Background Tasks ─────────────────────────────────────────────────────────

async def store_change_listener():
    """
    Polls in-memory store periodically and broadcasts changes via WebSocket.
    """
    import time
    last_snapshot: dict[str, Any] = {}

    while True:
        try:
            shipments = store.get_all_active_shipments()
            changes = []
            for s in shipments:
                sid = s["id"]
                old = last_snapshot.get(sid, {})
                # Check for meaningful changes
                if (old.get("risk_score") != s.get("risk_score") or
                        old.get("status") != s.get("status") or
                        old.get("is_anomaly") != s.get("is_anomaly")):
                    changes.append(s)
                last_snapshot[sid] = s

            if changes:
                await ws_manager.broadcast("shipments", {
                    "event": "shipments_updated",
                    "data": changes,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

        except Exception as e:
            logger.warning(f"[Listener] Error: {e}")

        await asyncio.sleep(3)  # poll every 3 seconds


async def _auto_reroute(shipment_id: str, risk_score: float) -> None:
    """Background auto-reroute when risk > 75."""
    try:
        shipment = store.get_shipment(shipment_id)
        if not shipment:
            return

        routes_payload = []
        if _HAS_ROUTE_OPTIMIZER and RouteOptimizer is not None:
            optimizer = RouteOptimizer()
            routes = optimizer.get_alternate_routes(
                origin=shipment.get("origin", "Mumbai"),
                destination=shipment.get("destination", "Rotterdam"),
            )

            routes_payload = [
                {
                    "rank": idx + 1,
                    "path": r.path,
                    "total_cost_usd": r.total_cost_usd,
                    "transit_days": r.transit_days,
                    "composite_risk": r.composite_risk,
                    "summary": r.summary,
                }
                for idx, r in enumerate(routes)
            ]

        await ws_manager.broadcast("alerts", {
            "event": "auto_reroute_computed",
            "shipment_id": shipment_id,
            "risk_score": risk_score,
            "routes": routes_payload,
        })

        logger.info(f"[AutoReroute] {shipment_id} — {len(routes_payload)} routes computed")

    except Exception as e:
        logger.exception(f"[AutoReroute] Error for {shipment_id}: {e}")
