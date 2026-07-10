# backend/firebase_client.py

import os
import json
import threading
import random
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Callable

import firebase_admin
from firebase_admin import credentials, firestore, db
from dotenv import load_dotenv

load_dotenv()


class FirebaseClient:
    """
    Singleton Firebase client wrapping both Firestore (state store)
    and Realtime Database (live alert queue).
    """

    _instance: Optional["FirebaseClient"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "FirebaseClient":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT", "serviceAccount.json")
        rtdb_url = os.getenv("FIREBASE_RTDB_URL")  # e.g. https://your-project-default-rtdb.firebaseio.com

        try:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred, {"databaseURL": rtdb_url})
            self.firestore_client = firestore.client()
            self._dev_mode = False
        except Exception as e:
            print(f"[FirebaseClient] Development mode - Firebase not available: {e}")
            self._dev_mode = True
            self.firestore_client = None

        self._initialized = True
        print("[FirebaseClient] Initialized Firestore + Realtime DB" if not self._dev_mode else "[FirebaseClient] Running in DEV mode (no Firebase)")
    
    # ─────────────────────────────────────────────
    #  MOCK DATA GENERATION  — for dev/testing
    # ─────────────────────────────────────────────
    
    def _generate_mock_shipments(self, count: int = 5) -> list[dict]:
        """Generate realistic mock shipment data"""
        carriers = ["Maersk", "MSC", "CMA-CGM", "COSCO", "Evergreen"]
        origins = ["Mumbai", "Shanghai", "Shenzhen", "Dubai", "Singapore"]
        destinations = ["Rotterdam", "Los Angeles", "Hamburg", "Antwerp", "Port Said"]
        statuses = ["in_transit", "at_port", "delayed", "customs_hold"]
        cargo_types = ["Electronics", "Chemicals", "Textiles", "Machinery", "Containers"]
        risk_factors = ["weather", "congestion", "piracy", "mechanical_issue", "port_delay"]
        
        shipments = []
        for i in range(count):
            risk_score = round(random.uniform(10, 95), 1)
            if risk_score < 30:
                risk_level = "low"
            elif risk_score < 60:
                risk_level = "medium"
            elif risk_score < 80:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            shipment = {
                "id": f"SHP-{4420 + i}",
                "origin": random.choice(origins),
                "destination": random.choice(destinations),
                "carrier": random.choice(carriers),
                "lat": round(random.uniform(-60, 60), 2),
                "lng": round(random.uniform(-180, 180), 2),
                "status": random.choice(statuses),
                "risk_score": risk_score,
                "risk_level": risk_level,
                "is_anomaly": random.choice([False, False, False, True]),  # 25% anomaly rate
                "speed_kmh": round(random.uniform(15, 40), 1),
                "progress": round(random.uniform(0.1, 0.95), 2),
                "cargo_type": random.choice(cargo_types),
                "value_usd": random.randint(50000, 500000),
                "eta_days": round(random.uniform(3, 30), 1),
                "top_risk_factors": random.sample(risk_factors, k=random.randint(1, 3)),
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            shipments.append(shipment)
        
        return shipments
    
    def _generate_mock_alerts(self, count: int = 3) -> list[dict]:
        """Generate realistic mock alert data"""
        alert_types = ["high_risk_flag", "anomaly_detected", "reroute_recommendation", "delay_warning"]
        severities = ["low", "medium", "high", "critical"]
        messages = [
            "Unusual dwell time detected at port",
            "Weather disruption in transit region",
            "Port congestion detected",
            "Vessel speed anomaly detected",
            "Route deviation from planned path",
            "Mechanical issue reported"
        ]
        
        alerts = []
        shipments = self._generate_mock_shipments(20)  # Reference shipments
        
        for i in range(count):
            shipment = random.choice(shipments)
            alert = {
                "id": f"ALT-{random.randint(100000, 999999)}",
                "shipment_id": shipment["id"],
                "type": random.choice(alert_types),
                "severity": random.choice(severities),
                "message": random.choice(messages),
                "risk_score": round(random.uniform(50, 95), 1),
                "alternate_routes": [
                    {
                        "rank": 1,
                        "path": ["Mumbai", "Singapore", "Rotterdam"],
                        "total_cost_usd": random.randint(3000, 6000),
                        "transit_days": random.randint(15, 35),
                        "composite_risk": round(random.uniform(20, 70), 1),
                        "summary": "Optimized for cost and risk balance"
                    },
                    {
                        "rank": 2,
                        "path": ["Mumbai", "Cape Town", "Rotterdam"],
                        "total_cost_usd": random.randint(4000, 7000),
                        "transit_days": random.randint(20, 40),
                        "composite_risk": round(random.uniform(25, 75), 1),
                        "summary": "Longer route with lower piracy risk"
                    }
                ],
                "created_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(0, 12))).isoformat()
            }
            alerts.append(alert)
        
        return alerts

    # ─────────────────────────────────────────────
    #  FIRESTORE  — shipment state store
    # ─────────────────────────────────────────────

    def upsert_shipment(self, shipment_id: str, data: dict) -> None:
        """Write or merge a shipment document into Firestore."""
        if self._dev_mode:
            return
        try:
            data["last_updated"] = firestore.SERVER_TIMESTAMP
            ref = self.firestore_client.collection("shipments").document(shipment_id)
            ref.set(data, merge=True)
        except Exception as e:
            print(f"[Firebase] Error upserting shipment: {e}")

    def get_shipment(self, shipment_id: str) -> Optional[dict]:
        if self._dev_mode:
            return None
        try:
            doc = self.firestore_client.collection("shipments").document(shipment_id).get()
            if doc.exists:
                return {"id": doc.id, **doc.to_dict()}
        except Exception as e:
            print(f"[Firebase] Error getting shipment: {e}")
        return None

    def get_all_active_shipments(self) -> list[dict]:
        if self._dev_mode:
            return self._generate_mock_shipments(count=5)
        try:
            docs = (
                self.firestore_client
                .collection("shipments")
                .where("status", "in", ["in_transit", "at_port", "customs_hold"])
                .stream()
            )
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception as e:
            print(f"[Firebase] Error getting active shipments: {e}")
        return []

    def write_alert_to_firestore(self, alert_id: str, alert: dict) -> None:
        if self._dev_mode:
            return
        try:
            alert["created_at"] = firestore.SERVER_TIMESTAMP
            self.firestore_client.collection("alerts").document(alert_id).set(alert)
        except Exception as e:
            print(f"[Firebase] Error writing alert: {e}")

    def get_recent_alerts(self, hours: int = 1) -> list[dict]:
        if self._dev_mode:
            return self._generate_mock_alerts(count=3)
        try:
            from google.cloud.firestore_v1 import FieldFilter
            cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
            docs = self.firestore_client.collection("alerts").order_by(
                "created_at", direction=firestore.Query.DESCENDING
            ).limit(200).stream()
            return [{"id": d.id, **d.to_dict()} for d in docs]
        except Exception as e:
            print(f"[Firebase] Error getting recent alerts: {e}")
        return []

    def update_risk_score(self, shipment_id: str, risk_score: float, anomaly: bool) -> None:
        if self._dev_mode:
            return
        try:
            self.firestore_client.collection("shipments").document(shipment_id).update({
                "risk_score": risk_score,
                "is_anomaly": anomaly,
                "last_updated": firestore.SERVER_TIMESTAMP,
            })
        except Exception as e:
            print(f"[Firebase] Error updating risk score: {e}")

    # ─────────────────────────────────────────────
    #  REALTIME DATABASE  — live alert queue
    # ─────────────────────────────────────────────

    def push_realtime_alert(self, shipment_id: str, alert: dict) -> None:
        """Write alert to RTDB so the dashboard's onValue() fires instantly."""
        if self._dev_mode:
            return
        try:
            alert["timestamp"] = datetime.now(timezone.utc).isoformat()
            ref = db.reference(f"alerts/{shipment_id}")
            ref.set(alert)
        except Exception as e:
            print(f"[Firebase] Error pushing realtime alert: {e}")

    def clear_realtime_alert(self, shipment_id: str) -> None:
        if self._dev_mode:
            return
        try:
            db.reference(f"alerts/{shipment_id}").delete()
        except Exception as e:
            print(f"[Firebase] Error clearing realtime alert: {e}")
