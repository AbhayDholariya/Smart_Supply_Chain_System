# backend/in_memory_store.py
"""
In-Memory Data Store  — CSV-powered
=====================================
Loads real shipment data from data/supply_chain_1M.csv instead of random mock data.
Thread-safe, singleton, no external database required.
"""

import threading
import uuid
import csv
import os
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ─── City coordinates for Indian cities ──────────────────────────────────────
CITY_COORDS = {
    "Mumbai": (19.0760, 72.8777), "Delhi": (28.6139, 77.2090),
    "Bangalore": (12.9716, 77.5946), "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639), "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567), "Ahmedabad": (23.0225, 72.5714),
    "Surat": (21.1702, 72.8311), "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462), "Nagpur": (21.1458, 79.0882),
    "Coimbatore": (11.0168, 76.9558), "Chandigarh": (30.7333, 76.7794),
    "Indore": (22.7196, 75.8577), "Bhopal": (23.2599, 77.4126),
    "Patna": (25.5941, 85.1376), "Kochi": (9.9312, 76.2673),
    "Visakhapatnam": (17.6868, 83.2185), "Guwahati": (26.1445, 91.7362),
    "Rajkot": (22.3039, 70.8022), "Vadodara": (22.3072, 73.1812),
    "Nashik": (19.9975, 73.7898), "Varanasi": (25.3176, 82.9739),
    "Agra": (27.1767, 78.0081), "Ludhiana": (30.9010, 75.8573),
    "Amritsar": (31.6340, 74.8723), "Jodhpur": (26.2389, 73.0243),
    "Udaipur": (24.5854, 73.7125), "Kanpur": (26.4499, 80.3319),
    "Vijayawada": (16.5062, 80.6480), "Mysore": (12.2958, 76.6394),
    "Bhavnagar": (21.7645, 72.1519), "Faridabad": (28.4089, 77.3178),
    "Meerut": (28.9845, 77.7064), "Jabalpur": (23.1815, 79.9864),
    "Gwalior": (26.2183, 78.1828), "Raipur": (21.2514, 81.6296),
    "Hubli": (15.3647, 75.1240), "Mangalore": (12.9141, 74.8560),
    "Tirupur": (11.1085, 77.3411), "Madurai": (9.9252, 78.1198),
    "Srinagar": (34.0837, 74.7973), "Ranchi": (23.3441, 85.3096),
    "Bhubaneswar": (20.2961, 85.8245), "Siliguri": (26.7271, 88.3953),
}

# ─── Weather code → display label + icon ─────────────────────────────────────
WEATHER_LABEL = {
    "rain": ("Rain", "🌧️"),
    "light_rain": ("Light Rain", "🌦️"),
    "heavy_rain": ("Heavy Rain", "⛈️"),
    "fog": ("Fog", "🌫️"),
    "storm": ("Storm", "🌩️"),
    "clear": ("Clear", "☀️"),
    "cloudy": ("Cloudy", "☁️"),
    "overcast": ("Overcast", "🌥️"),
    "snow": ("Snow", "❄️"),
}

# ─── City → State mapping ─────────────────────────────────────────────────────
CITY_STATE = {
    "Mumbai": "Maharashtra", "Pune": "Maharashtra", "Nashik": "Maharashtra",
    "Nagpur": "Maharashtra", "Solapur": "Maharashtra",
    "Delhi": "Delhi", "Faridabad": "Haryana", "Gurgaon": "Haryana",
    "Bangalore": "Karnataka", "Mysore": "Karnataka", "Hubli": "Karnataka",
    "Mangalore": "Karnataka",
    "Chennai": "Tamil Nadu", "Coimbatore": "Tamil Nadu", "Madurai": "Tamil Nadu",
    "Tirupur": "Tamil Nadu",
    "Kolkata": "West Bengal", "Siliguri": "West Bengal",
    "Hyderabad": "Telangana",
    "Vijayawada": "Andhra Pradesh", "Visakhapatnam": "Andhra Pradesh",
    "Ahmedabad": "Gujarat", "Surat": "Gujarat", "Vadodara": "Gujarat",
    "Rajkot": "Gujarat", "Bhavnagar": "Gujarat",
    "Jaipur": "Rajasthan", "Jodhpur": "Rajasthan", "Udaipur": "Rajasthan",
    "Lucknow": "Uttar Pradesh", "Kanpur": "Uttar Pradesh", "Varanasi": "Uttar Pradesh",
    "Agra": "Uttar Pradesh", "Meerut": "Uttar Pradesh",
    "Chandigarh": "Punjab", "Amritsar": "Punjab", "Ludhiana": "Punjab",
    "Indore": "Madhya Pradesh", "Bhopal": "Madhya Pradesh", "Jabalpur": "Madhya Pradesh",
    "Gwalior": "Madhya Pradesh",
    "Patna": "Bihar",
    "Kochi": "Kerala",
    "Guwahati": "Assam",
    "Raipur": "Chhattisgarh",
    "Ranchi": "Jharkhand",
    "Bhubaneswar": "Odisha",
    "Srinagar": "J&K",
}

CARRIER_NAMES = {
    "SHADOWFAX-04": "Shadowfax", "TCI-02": "TCI Freight", "DELHIVERY-07": "Delhivery",
    "BLUEDART-03": "Blue Dart", "RIVIGO-05": "Rivigo", "XPRESSBEES-01": "XpressBees",
    "ECOM-06": "Ecom Express", "DTDC-08": "DTDC", "GATI-09": "Gati",
    "EKART-10": "Ekart", "AMAZON-11": "Amazon Logistics", "FEDEX-12": "FedEx India",
}


def _safe_float(val, default=0.0) -> float:
    """Safely convert any value to float."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance between two points using the Haversine formula.
    Returns distance in kilometres."""
    import math
    R = 6371.0  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _is_flag_set(val) -> bool:
    """Check if a flag field is truthy (handles '1', 1, 'True', True)."""
    return str(val).strip() in ("1", "True", "true", "yes")


def _compute_risk_score(row: dict) -> float:
    """Compute risk score from CSV columns (0-100)."""
    score = 20.0
    weather_risk = {
        "storm": 40, "heavy_rain": 35, "fog": 25, "snow": 30,
        "rain": 20, "light_rain": 12, "overcast": 5, "cloudy": 3, "clear": 0
    }
    score += weather_risk.get(str(row.get("weather_code", "clear")).lower(), 5)
    score += _safe_float(row.get("segment_congestion_idx", 0)) * 20
    score += _safe_float(row.get("port_congestion_idx", 0)) * 10
    score += min(_safe_float(row.get("delay_hours_current", 0)) * 5, 25)
    score += min(_safe_float(row.get("route_avg_delay_7d", 0)) * 3, 15)
    if _is_flag_set(row.get("road_closure_flag", "0")):
        score += 20
    if _is_flag_set(row.get("strike_event_flag", "0")):
        score += 18
    if _is_flag_set(row.get("traffic_incident_flag", "0")):
        score += 12
    if _is_flag_set(row.get("maintenance_flag", "0")):
        score += 8
    carrier_rate = _safe_float(row.get("carrier_on_time_rate", 0.8), 0.8)
    score += (1 - carrier_rate) * 20
    avg_sp = _safe_float(row.get("avg_speed_kmh", 40), 40)
    exp_sp = _safe_float(row.get("expected_speed_kmh", 50), 50)
    if exp_sp > 0:
        ratio = avg_sp / exp_sp
        if ratio < 0.5:
            score += 15
        elif ratio < 0.7:
            score += 8
    vis = _safe_float(row.get("visibility_km", 10), 10)
    if vis < 2:
        score += 15
    elif vis < 5:
        score += 8
    return round(min(max(score, 10.0), 100), 1)


def _build_risk_factors(row: dict, weather_label: str) -> list:
    """Build human-readable risk factor list from CSV row."""
    factors = []
    weather = str(row.get("weather_code", "clear")).lower()
    if weather in ("storm", "heavy_rain", "fog", "snow", "rain"):
        icon = WEATHER_LABEL.get(weather, ("", "☁️"))[1]
        factors.append(f"{icon} {weather_label} — reduced visibility & road risk")
    if _is_flag_set(row.get("road_closure_flag", "0")):
        factors.append("🚧 Road closure on route — rerouting required")
    if _is_flag_set(row.get("strike_event_flag", "0")):
        factors.append("🪧 Strike event detected — possible blockage")
    if _is_flag_set(row.get("traffic_incident_flag", "0")):
        factors.append("🚨 Traffic incident on segment")
    seg = _safe_float(row.get("segment_congestion_idx", 0))
    if seg > 0.7:
        factors.append(f"🚦 High congestion index: {seg:.2f}")
    delay = _safe_float(row.get("delay_hours_current", 0))
    if delay > 1:
        factors.append(f"⏰ Active delay: {delay:.1f}h behind schedule")
    carrier_rate = _safe_float(row.get("carrier_on_time_rate", 0.8), 0.8)
    if carrier_rate < 0.6:
        factors.append(f"📉 Low carrier on-time rate: {carrier_rate*100:.0f}%")
    vis = _safe_float(row.get("visibility_km", 10), 10)
    if vis < 5:
        factors.append(f"👁️ Low visibility: {vis} km")
    if _is_flag_set(row.get("customs_hold_flag", "0")):
        factors.append("🛃 Customs hold — clearance pending")
    if not factors:
        factors.append("✅ No critical risk factors — standard monitoring")
    return factors[:4]


def _status_from_row(row: dict) -> str:
    """Map CSV disruption_type / delay_severity to status."""
    disp = str(row.get("disruption_type", "none")).lower()
    delay_sev = str(row.get("delay_severity", "low")).lower()
    delay_h = _safe_float(row.get("delay_hours_current", 0))
    if disp in ("accident", "vehicle_breakdown"):
        return "delayed"
    if _is_flag_set(row.get("customs_hold_flag", "0")):
        return "customs_hold"
    if _is_flag_set(row.get("idle_flag", "0")):
        return "at_warehouse"
    if delay_h > 2 or delay_sev in ("high", "critical"):
        return "delayed"
    return "in_transit"


def _build_reroute_options(origin: str, destination: str, weather: str, congestion: float) -> list:
    """Build 2-3 alternate route options based on real conditions."""
    routes = []
    # Route A: NH (national highway) — fastest
    base_dist = CITY_COORDS.get(origin, (20, 77))
    dest_c = CITY_COORDS.get(destination, (23, 80))
    est_dist = round(((base_dist[0]-dest_c[0])**2 + (base_dist[1]-dest_c[1])**2)**0.5 * 111, 0)
    routes.append({
        "rank": 1, "name": "Via NH (Fastest)",
        "path": [origin, destination],
        "distance_km": est_dist,
        "transit_hours": round(est_dist / 55, 1),
        "toll_cost_inr": round(est_dist * 2.5, 0),
        "risk_score": round(20 + congestion * 30, 0),
        "recommended": True,
        "reason": "Fastest via National Highway"
    })
    # Route B: State roads — avoids toll/congestion
    routes.append({
        "rank": 2, "name": "Via State Roads (Low Toll)",
        "path": [origin, "via State Roads", destination],
        "distance_km": round(est_dist * 1.15, 0),
        "transit_hours": round(est_dist * 1.15 / 45, 1),
        "toll_cost_inr": round(est_dist * 0.8, 0),
        "risk_score": round(15 + congestion * 15, 0),
        "recommended": False,
        "reason": "Lower toll, avoids highway congestion"
    })
    # Route C: weather-safe if bad weather
    if weather in ("storm", "heavy_rain", "fog"):
        routes.append({
            "rank": 3, "name": "Weather-Safe Alternate",
            "path": [origin, "via Covered Shelter Points", destination],
            "distance_km": round(est_dist * 1.25, 0),
            "transit_hours": round(est_dist * 1.25 / 40, 1),
            "toll_cost_inr": round(est_dist * 3.0, 0),
            "risk_score": 18,
            "recommended": False,
            "reason": f"Safer alternate due to {weather} — passes shelter points"
        })
    return routes


class InMemoryStore:
    """
    Singleton in-memory store loading real data from supply_chain_1M.csv.
    Falls back to minimal mock data if CSV not available.
    """

    _instance: Optional["InMemoryStore"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "InMemoryStore":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._data_lock = threading.Lock()
        self._shipments: dict[str, dict] = {}
        self._alerts: list[dict] = []
        self._cascade_events: list[dict] = []
        self._load_csv_data()
        self._initialized = True

    # ─── Public API ──────────────────────────────────────────────────────────

    def upsert_shipment(self, shipment_id: str, data: dict) -> None:
        with self._data_lock:
            data["last_updated"] = datetime.now(timezone.utc).isoformat()
            if shipment_id in self._shipments:
                self._shipments[shipment_id].update(data)
            else:
                self._shipments[shipment_id] = {"id": shipment_id, **data}

    def get_shipment(self, shipment_id: str) -> Optional[dict]:
        with self._data_lock:
            return self._shipments.get(shipment_id)

    def get_all_active_shipments(self) -> list[dict]:
        with self._data_lock:
            active_statuses = {"in_transit", "at_warehouse", "delayed", "customs_hold",
                               "loading", "at_port", "in-transit"}
            return [s for s in self._shipments.values() if s.get("status") in active_statuses]

    def update_risk_score(self, shipment_id: str, risk_score: float, risk_level: str,
                          is_anomaly: bool, delay_probability: float = 0.0) -> None:
        with self._data_lock:
            if shipment_id in self._shipments:
                self._shipments[shipment_id].update({
                    "risk_score": risk_score, "risk_level": risk_level,
                    "is_anomaly": is_anomaly, "delay_probability": delay_probability,
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                })

    def get_high_risk_shipments(self, threshold: float = 70.0) -> list[dict]:
        with self._data_lock:
            return [s for s in self._shipments.values() if s.get("risk_score", 0) >= threshold]

    def push_alert(self, alert: dict) -> str:
        alert_id = alert.get("id") or f"ALT-{uuid.uuid4().hex[:8].upper()}"
        alert["id"] = alert_id
        alert["created_at"] = alert.get("created_at") or datetime.now(timezone.utc).isoformat()
        with self._data_lock:
            self._alerts.insert(0, alert)
            self._alerts = self._alerts[:500]
        return alert_id

    def get_recent_alerts(self, hours: int = 24) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        with self._data_lock:
            result = []
            for a in self._alerts:
                try:
                    created = datetime.fromisoformat(a["created_at"].replace("Z", "+00:00"))
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                    if created >= cutoff:
                        result.append(a)
                except Exception:
                    result.append(a)
            return result

    def get_all_alerts(self) -> list[dict]:
        with self._data_lock:
            return list(self._alerts)

    def push_cascade_event(self, event: dict) -> str:
        event_id = f"CASCADE-{uuid.uuid4().hex[:8].upper()}"
        event["id"] = event_id
        event["created_at"] = datetime.now(timezone.utc).isoformat()
        with self._data_lock:
            self._cascade_events.insert(0, event)
            self._cascade_events = self._cascade_events[:100]
        return event_id

    def get_cascade_events(self, limit: int = 10) -> list[dict]:
        with self._data_lock:
            return self._cascade_events[:limit]

    # ─── CSV Loading ─────────────────────────────────────────────────────────

    def _load_csv_data(self) -> None:
        """Load real shipment data from supply_chain_1M.csv, international_supply_chain_500k.csv, or indian_route_legs.csv."""
        loaded_ind = 0
        # Try supply_chain_1M.csv first
        csv_path_ind = Path(__file__).parent.parent / "data" / "supply_chain_1M.csv"
        if csv_path_ind.exists():
            try:
                loaded_ind = self._load_indian_shipments_from_csv(str(csv_path_ind))
                print(f"[InMemoryStore] Loaded {loaded_ind} real Indian shipments from supply_chain_1M.csv")
            except Exception as e:
                print(f"[InMemoryStore] Indian CSV load error: {e}")
        
        # If supply_chain_1M.csv not found, try indian_route_legs.csv
        if loaded_ind == 0:
            csv_path_indian_legs = Path(__file__).parent.parent / "data" / "indian_route_legs.csv"
            if csv_path_indian_legs.exists():
                try:
                    loaded_ind = self._load_indian_route_legs_from_csv(str(csv_path_indian_legs))
                    print(f"[InMemoryStore] Loaded {loaded_ind} real Indian shipments from indian_route_legs.csv")
                except Exception as e:
                    print(f"[InMemoryStore] indian_route_legs.csv load error: {e}")
                
        csv_path_int = Path(__file__).parent.parent / "data" / "international_supply_chain_500k.csv"
        loaded_int = 0
        if csv_path_int.exists():
            try:
                loaded_int = self._load_intl_shipments_from_csv(str(csv_path_int))
                print(f"[InMemoryStore] Loaded {loaded_int} real International shipments from international_supply_chain_500k.csv")
            except Exception as e:
                print(f"[InMemoryStore] Intl CSV load error: {e}")

        if loaded_ind == 0 and loaded_int == 0:
            self._seed_fallback_mock()
            print("[InMemoryStore] Using fallback mock data (CSVs not found)")
        
        self._seed_alerts_from_high_risk()

    def _load_indian_route_legs_from_csv(self, csv_path: str, sample_size: int = 500) -> int:
        """Load shipments from indian_route_legs.csv and convert to shipment dicts."""
        # Count total lines quickly
        with open(csv_path, "r", encoding="utf-8") as f:
            total = sum(1 for _ in f) - 1  # minus header

        step = max(1, total // (sample_size * 3))  # read more, filter down
        loaded_count = 0
        seen_trip_ids = set()

        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i % step != 0:
                    continue
                origin = row.get("origin_city", "").strip()
                destination = row.get("destination_city", "").strip()
                trip_id = row.get("trip_id", "").strip()
                if origin not in CITY_COORDS or destination not in CITY_COORDS:
                    continue
                if origin == destination:
                    continue
                # Only load one shipment per trip ID
                if trip_id in seen_trip_ids:
                    continue
                seen_trip_ids.add(trip_id)

                shipment = self._route_leg_row_to_shipment(row)
                self._shipments[shipment["id"]] = shipment
                loaded_count += 1
                if loaded_count >= sample_size:
                    break

        return loaded_count

    def _route_leg_row_to_shipment(self, row: dict) -> dict:
        """Convert an indian_route_legs.csv row to a shipment dict."""
        trip_id = row.get("trip_id", f"IND-{uuid.uuid4().hex[:8].upper()}")
        shipment_id = f"IND-{trip_id.upper()}"

        origin = row.get("origin_city", "Mumbai").strip()
        destination = row.get("destination_city", "Delhi").strip()
        orig_coords = CITY_COORDS.get(origin, (19.076, 72.877))
        dest_coords = CITY_COORDS.get(destination, (28.613, 77.209))
        orig_state = row.get("origin_state", CITY_STATE.get(origin, "India"))
        dest_state = row.get("destination_state", CITY_STATE.get(destination, "India"))

        # Progress from distance covered vs total
        dist_cov = _safe_float(row.get("distance_from_origin_km", 0))
        dist_rem_csv = _safe_float(row.get("distance_remaining_km", 100), 100)
        total_dist_csv = _safe_float(row.get("total_route_distance_km", dist_cov + dist_rem_csv), dist_cov + dist_rem_csv)
        progress = round(dist_cov / total_dist_csv, 3) if total_dist_csv > 0 else 0.5

        cur_lat = orig_coords[0] + (dest_coords[0] - orig_coords[0]) * progress
        cur_lng = orig_coords[1] + (dest_coords[1] - orig_coords[1]) * progress

        # Haversine-based accurate distances
        total_dist = round(_haversine_km(orig_coords[0], orig_coords[1],
                                        dest_coords[0], dest_coords[1]) * 1.25, 1)  # road factor ~1.25x
        dist_rem = round(_haversine_km(cur_lat, cur_lng,
                                        dest_coords[0], dest_coords[1]) * 1.25, 1)
        dist_cov_val = round(total_dist - dist_rem, 1)

        # Map weather condition to our weather code
        weather_condition = str(row.get("weather_condition", "Clear")).strip()
        weather_code_map = {
            "Clear": "clear",
            "Fog/Low Visibility": "fog",
            "Heavy Rain/Waterlogging": "heavy_rain",
            "Thunderstorm": "storm",
            "Moderate Rain": "rain",
            "Light Rain": "light_rain",
            "Drizzle": "light_rain",
            "Cloudy": "cloudy",
            "Overcast": "overcast"
        }
        weather_code = weather_code_map.get(weather_condition, "clear")
        weather_info = WEATHER_LABEL.get(weather_code, (weather_condition, "☀️"))
        weather_label = f"{weather_info[1]} {weather_info[0]}"

        # Carrier display name
        carrier_name = row.get("carrier_company", "Unknown").strip()

        # Risk score - compute from available fields
        risk_score = 20.0
        # Weather contribution
        weather_risk = {
            "storm": 40, "heavy_rain": 35, "fog": 25, "snow": 30,
            "rain": 20, "light_rain": 12, "overcast": 5, "cloudy": 3, "clear": 0
        }
        risk_score += weather_risk.get(weather_code, 5)
        # Traffic
        traffic_level = row.get("traffic_condition", "Moderate").lower()
        if traffic_level == "heavy":
            risk_score += 25
        elif traffic_level == "moderate":
            risk_score += 10
        # Delay
        delay_hours = _safe_float(row.get("cumulative_delay_hours", 0))
        risk_score += min(delay_hours * 5, 20)
        # Disruption occurred
        if _safe_float(row.get("disruption_occurred", 0)) == 1:
            risk_score += 15
        # Season
        if row.get("season", "").strip().lower() == "monsoon":
            risk_score += 10
        # Cap risk score to 0-100
        risk_score = round(max(10.0, min(100.0, risk_score)), 1)

        risk_level = (
            "critical" if risk_score >= 75 else
            "high"      if risk_score >= 50 else
            "medium"    if risk_score >= 25 else "low"
        )
        is_anomaly = (_safe_float(row.get("disruption_occurred", 0)) == 1) or (risk_score > 75)
        
        disruption_type = row.get("disruption_type", "None")
        is_delayed = delay_hours > 0
        status = "in_transit"
        if is_delayed:
            status = "delayed"
        elif disruption_type and disruption_type != "None":
            status = "delayed"

        risk_factors = []
        if weather_code in ("storm", "heavy_rain", "fog", "rain"):
            icon = WEATHER_LABEL.get(weather_code, ("", "⚠️"))[1]
            risk_factors.append(f"{icon} {weather_condition} affecting visibility")
        if traffic_level == "heavy":
            risk_factors.append("🚦 Heavy traffic congestion")
        if delay_hours > 0:
            risk_factors.append(f"⏰ Active delay: {delay_hours:.1f} hours")
        if disruption_type != "None":
            risk_factors.append(f"⚠️ Disruption: {disruption_type}")
        if not risk_factors:
            risk_factors.append("✅ No critical risk factors — standard monitoring")

        # Reroute options
        reroute_options = []
        if _safe_float(row.get("alternate_route_available", 0)) == 1 or risk_score > 60:
            reroute_options = _build_reroute_options(origin, destination, weather_code, 
                                                    0.5 if traffic_level == "heavy" else 0.2)

        planned_transit_hours = round(total_dist / 40, 1)  # 40 km/h average
        eta_hours = round(planned_transit_hours * (1 - progress) * (1 + risk_score / 200), 1)

        # Checkpoint timestamp for created_at
        checkpoint_ts = row.get("checkpoint_timestamp", "")
        try:
            created_at = datetime.strptime(checkpoint_ts.split(".")[0], "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            ).isoformat()
        except Exception:
            created_at = (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))).isoformat()

        shipment_value_inr = _safe_float(row.get("cargo_value_inr", 50000), 50000)
        cargo_type = row.get("cargo_type", "General").strip().title()
        vehicle_type = row.get("vehicle_type", "Truck").strip()
        avg_speed_kmph = _safe_float(row.get("avg_speed_kmph", 40), 40)
        cascading_risk_score = _safe_float(row.get("cascading_risk_score", 0.1), 0.1)
        alternate_route_available = int(_safe_float(row.get("alternate_route_available", 0)) == 1)

        return {
            "id": shipment_id, "shipment_id": shipment_id,
            "panel": "india",
            # Route
            "origin_city": origin, "origin_state": orig_state,
            "origin": f"{origin}, {orig_state}",
            "destination_city": destination, "destination_state": dest_state,
            "destination": f"{destination}, {dest_state}",
            "origin_lat": orig_coords[0], "origin_lng": orig_coords[1],
            "destination_lat": dest_coords[0], "destination_lng": dest_coords[1],
            "lat": round(cur_lat, 4), "lng": round(cur_lng, 4),
            # Carrier
            "carrier_company": carrier_name, "carrier": carrier_name,
            "carrier_id": row.get("driver_id", ""),
            # Trip
            "distance_km": round(total_dist, 1),
            "distance_covered_km": round(dist_cov_val, 1),
            "distance_remaining_km": round(dist_rem, 1),
            "planned_transit_hours": planned_transit_hours,
            "progress": progress,
            "eta_hours": eta_hours,
            "transport_mode": "road",
            # Weather
            "weather_condition": weather_label,
            "weather_code": weather_code,
            "wind_speed_kmh": 0.0,
            "visibility_km": 5.0 if weather_code in ("fog", "heavy_rain") else 10.0,
            # Traffic
            "traffic_congestion_level": (
                "Very High" if traffic_level == "heavy" else
                "High"      if traffic_level == "moderate" else
                "Medium"    if traffic_level == "light" else "Low"
            ),
            "segment_congestion_idx": 0.7 if traffic_level == "heavy" else 0.3,
            "port_congestion_idx": 0.0,
            # Disruption flags
            "road_closure_flag": 1 if disruption_type == "Road Closure" else 0,
            "strike_event_flag": 1 if disruption_type == "Strike" else 0,
            "traffic_incident_flag": 1 if disruption_type == "Accident" else 0,
            "customs_hold_flag": 0,
            "holiday_flag": 0,
            "maintenance_flag": 1 if disruption_type == "Vehicle Breakdown" else 0,
            "temp_breach_flag": 0,
            "border_crossing_flag": 0,
            "alternate_routes_avail": alternate_route_available,
            # Vehicle/driver
            "vehicle_type": vehicle_type, "vehicle_age_years": 3.0,
            "driver_experience_years": max(1.0, _safe_float(row.get("driver_experience_years", 5), 5)),
            "driver_rest_hours_prior": max(0.0, 8.0 - _safe_float(row.get("driver_hours_since_last_rest", 0), 0)),
            "night_driving_flag": int(_safe_float(row.get("is_night_travel", 0)) == 1),
            "vehicle_breakdown_flag": 1 if disruption_type == "Vehicle Breakdown" else 0,
            "accident_reported_flag": 1 if disruption_type == "Accident" else 0,
            # Route details
            "num_toll_plazas": int(row.get("leg_sequence_num", 1)) * 2,
            "num_state_border_crossings": 1 if orig_state != dest_state else 0,
            "eway_bill_verified": 1,
            "gps_route_deviation_km": 0.0,
            "checkpoint_delay_minutes": round(delay_hours * 60, 1),
            "origin_wh_congestion_pct": 30.0,
            "dest_wh_congestion_pct": 30.0,
            "upstream_shipment_delay_minutes": round(delay_hours * 60, 1),
            # Indian specific
            "order_type": "B2B",
            "priority_level": "Priority" if risk_score > 60 else "Scheduled-Freight",
            "is_monsoon_season": 1 if row.get("season", "").strip().lower() == "monsoon" else 0,
            "is_festival_season": 0,
            "fuel_price_per_litre": _safe_float(row.get("fuel_price_at_location_inr_per_liter", 104.0), 104.0),
            "shipment_value_inr": round(shipment_value_inr, 0),
            "cargo_type": cargo_type,
            # Risk
            "risk_score": risk_score, "risk_level": risk_level,
            "is_anomaly": is_anomaly,
            "delay_probability": round(min(risk_score / 100 * 1.1, 1.0), 3),
            "cascade_risk_score": round(cascading_risk_score, 3),
            "disruption_type": disruption_type,
            "disruption_flag": int(_safe_float(row.get("disruption_occurred", 0)) == 1),
            # Status
            "status": status, "is_delayed": is_delayed,
            "delay_duration_minutes": round(delay_hours * 60, 1),
            "delay_hours_current": delay_hours,
            "delay_severity": row.get("disruption_severity", "low"),
            "recommended_action": row.get("recommended_action", "no_action"),
            # Rerouting
            "alt_route_needed": alternate_route_available,
            "reroute_options": reroute_options,
            # Global compat
            "speed_kmh": avg_speed_kmph,
            "value_usd": int(round(shipment_value_inr / 83.0, 0)),  # rough INR to USD conversion
            "transit_days": round(planned_transit_hours / 24, 1),
            "top_risk_factors": risk_factors,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "created_at": created_at,
            # Historical data
            "route_avg_delay_7d": 0.5,
            "route_disruption_cnt_30d": int(cascading_risk_score * 10),
            "carrier_on_time_rate": 0.8,
            "seasonal_risk_score": 0.3 if row.get("season", "").strip().lower() == "monsoon" else 0.1,
            "same_lane_delay_ratio": 0.3,
        }

    def _load_indian_shipments_from_csv(self, csv_path: str, sample_size: int = 500) -> int:
        """
        Read supply_chain_1M.csv and convert rows to shipment dicts.
        Loads `sample_size` rows spread evenly across the file for variety.
        Only keeps rows where origin/destination city is known in CITY_COORDS.
        """
        # Count total lines quickly
        with open(csv_path, "r", encoding="utf-8") as f:
            total = sum(1 for _ in f) - 1  # minus header

        step = max(1, total // (sample_size * 3))  # read more, filter down
        loaded_count = 0

        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i % step != 0:
                    continue
                origin = row.get("origin_city", "").strip()
                destination = row.get("destination_city", "").strip()
                if origin not in CITY_COORDS or destination not in CITY_COORDS:
                    continue
                if origin == destination:
                    continue

                shipment = self._csv_row_to_shipment(row)
                self._shipments[shipment["id"]] = shipment
                loaded_count += 1
                if loaded_count >= sample_size:
                    break

        return loaded_count

    def _load_intl_shipments_from_csv(self, csv_path: str, sample_size: int = 150) -> int:
        """Read international_supply_chain_500k.csv and load sample shipments."""
        with open(csv_path, "r", encoding="utf-8") as f:
            total = sum(1 for _ in f) - 1

        step = max(1, total // (sample_size * 2))
        loaded_count = 0

        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i % step != 0:
                    continue
                try:
                    lat = float(row.get("current_lat", 0.0))
                    lng = float(row.get("current_lon", 0.0))
                    if lat == 0.0 and lng == 0.0:
                        continue
                except ValueError:
                    continue

                shipment = self._intl_csv_row_to_shipment(row)
                self._shipments[shipment["id"]] = shipment
                loaded_count += 1
                if loaded_count >= sample_size:
                    break
        return loaded_count

    def _intl_csv_row_to_shipment(self, row: dict) -> dict:
        """Convert one international CSV row to a global shipment dict."""
        shipment_id = row.get("shipment_id", f"SHP-{uuid.uuid4().hex[:6].upper()}")
        origin = f"{row.get('origin_port_name', 'Unknown Port')}, {row.get('origin_country', 'Unknown')}"
        destination = f"{row.get('destination_port_name', 'Unknown Port')}, {row.get('destination_country', 'Unknown')}"

        progress = _safe_float(row.get("voyage_progress_pct", 50)) / 100
        speed = _safe_float(row.get("actual_speed_kmh", 30))
        dist_km = _safe_float(row.get("total_distance_km", 5000))
        dist_cov = _safe_float(row.get("distance_covered_km", 2500))
        dist_rem = _safe_float(row.get("distance_remaining_km", 2500))

        risk_score = _safe_float(row.get("risk_score", 30))
        risk_level = (
            "critical" if risk_score >= 75 else
            "high"     if risk_score >= 50 else
            "medium"   if risk_score >= 25 else "low"
        )
        is_anomaly = str(row.get("disruption_flag", "0")) in ("1", "True", "true")

        status = "in-transit"
        delay_hrs = _safe_float(row.get("delay_hours_current", 0))
        if delay_hrs > 5:
            status = "delayed"
        if str(row.get("customs_hold_flag", "0")) in ("1", "True", "true"):
            status = "customs_hold"

        factors = []
        if _safe_float(row.get("wave_height_m", 0)) > 4.0:
            factors.append("🌊 High waves / rough seas")
        if _safe_float(row.get("panama_congestion_idx", 0)) > 0.7:
            factors.append("🚧 Panama Canal Congestion")
        if _safe_float(row.get("suez_congestion_idx", 0)) > 0.7:
            factors.append("🚧 Suez Canal Congestion")
        if str(row.get("port_strike_flag", "0")) in ("1", "True", "true"):
            factors.append("🪧 Active port strike")
        if not factors:
            factors.append("✅ standard monitoring — low risk")

        return {
            "id": shipment_id,
            "shipment_id": shipment_id,
            "panel": "global",
            "origin": origin,
            "destination": destination,
            "carrier": row.get("carrier_name", "Maersk"),
            "lat": _safe_float(row.get("current_lat", 0.0)),
            "lng": _safe_float(row.get("current_lon", 0.0)),
            "status": status,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "is_anomaly": is_anomaly,
            "speed_kmh": speed,
            "progress": progress,
            "cargo_type": row.get("cargo_type", "General Cargo"),
            "value_usd": int(round(_safe_float(row.get("seasonal_risk_score", 0.3)) * 80000 + 10000)),
            "eta_days": round(dist_rem / (speed * 24 + 1), 1),
            "top_risk_factors": factors[:3],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "distance_km": dist_km,
            "distance_covered_km": dist_cov,
            "distance_remaining_km": dist_rem,
            "transit_days": round(dist_km / (speed * 24 + 1), 1)
        }

    def _csv_row_to_shipment(self, row: dict) -> dict:
        """Convert one CSV row to a full shipment dict."""
        raw_id = row.get("shipment_id", f"IND-{uuid.uuid4().hex[:8].upper()}")
        # Clean the original ID and make a proper IND- prefixed one
        clean_id = raw_id.replace("SHP-", "").replace("IND-", "").replace("-", "")
        shipment_id = f"IND-{clean_id[:10].upper()}" if clean_id else f"IND-{uuid.uuid4().hex[:8].upper()}"

        origin = row.get("origin_city", "Mumbai").strip()
        destination = row.get("destination_city", "Delhi").strip()
        orig_coords = CITY_COORDS.get(origin, (19.076, 72.877))
        dest_coords = CITY_COORDS.get(destination, (28.613, 77.209))
        orig_state = CITY_STATE.get(origin, "India")
        dest_state = CITY_STATE.get(destination, "India")

        # Progress from distance covered vs total
        dist_cov = _safe_float(row.get("distance_covered_km", 0))
        dist_rem_csv = _safe_float(row.get("distance_remaining_km", 100), 100)
        total_dist_csv = dist_cov + dist_rem_csv
        progress = round(dist_cov / total_dist_csv, 3) if total_dist_csv > 0 else 0.5

        cur_lat = orig_coords[0] + (dest_coords[0] - orig_coords[0]) * progress
        cur_lng = orig_coords[1] + (dest_coords[1] - orig_coords[1]) * progress

        # Haversine-based accurate distances
        total_dist = round(_haversine_km(orig_coords[0], orig_coords[1],
                                          dest_coords[0], dest_coords[1]) * 1.25, 1)  # road factor ~1.25x
        dist_rem = round(_haversine_km(cur_lat, cur_lng,
                                        dest_coords[0], dest_coords[1]) * 1.25, 1)
        dist_cov = round(total_dist - dist_rem, 1)

        weather_code = str(row.get("weather_code", "clear")).lower().strip()
        weather_info = WEATHER_LABEL.get(weather_code, ("Clear", "☀️"))
        weather_label = f"{weather_info[1]} {weather_info[0]}"

        # Carrier display name
        carrier_raw = row.get("carrier_id", "Unknown")
        carrier_name = CARRIER_NAMES.get(carrier_raw, carrier_raw.split("-")[0].title())

        # Risk
        risk_score = _compute_risk_score(row)
        risk_level = (
            "critical" if risk_score >= 75 else
            "high"     if risk_score >= 50 else
            "medium"   if risk_score >= 25 else "low"
        )
        delay_h = _safe_float(row.get("delay_hours_current", 0))
        is_delayed = delay_h > 1.0 or str(row.get("delay_severity", "low")).lower() in ("high", "critical")
        status = _status_from_row(row)

        disruption_type = str(row.get("disruption_type", "none")).lower()
        is_anomaly = (
            disruption_type not in ("none", "no_action", "") and risk_score > 50
        ) or (risk_score > 75 and random.random() > 0.5)

        risk_factors = _build_risk_factors(row, weather_info[0])
        alt_needed = _is_flag_set(row.get("alt_route_needed", "0"))
        reroute_options = _build_reroute_options(origin, destination, weather_code,
                                                  _safe_float(row.get("segment_congestion_idx", 0))) if alt_needed or risk_score > 60 else []

        # Planned transit from segment_index heuristic
        segment_idx = int(row.get("segment_index", 1)) or 1
        planned_hrs = round(total_dist / 50, 1) if total_dist > 0 else 24.0
        eta_hours = round(planned_hrs * (1 - progress) * (1 + risk_score / 200), 1)

        # Snapshot time → created_at
        snap_ts = row.get("snapshot_timestamp", "")
        try:
            created_at = datetime.strptime(snap_ts, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc).isoformat()
        except Exception:
            created_at = (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))).isoformat()

        vehicle_age = _safe_float(row.get("vehicle_age_yrs", 3.0), 3.0)
        driver_hrs = _safe_float(row.get("driver_hours_elapsed", 4.0), 4.0)
        vis = _safe_float(row.get("visibility_km", 10), 10.0)
        wind = _safe_float(row.get("wind_speed_kmh", 10), 10.0)

        return {
            "id": shipment_id, "shipment_id": shipment_id,
            "panel": "india",
            # Route
            "origin_city": origin, "origin_state": orig_state,
            "origin": f"{origin}, {orig_state}",
            "destination_city": destination, "destination_state": dest_state,
            "destination": f"{destination}, {dest_state}",
            "origin_lat": orig_coords[0], "origin_lng": orig_coords[1],
            "destination_lat": dest_coords[0], "destination_lng": dest_coords[1],
            "lat": round(cur_lat, 4), "lng": round(cur_lng, 4),
            # Carrier
            "carrier_company": carrier_name, "carrier": carrier_name,
            "carrier_id": carrier_raw,
            # Trip
            "distance_km": round(total_dist, 1),
            "distance_covered_km": round(dist_cov, 1),
            "distance_remaining_km": round(dist_rem, 1),
            "planned_transit_hours": planned_hrs,
            "progress": progress,
            "eta_hours": eta_hours,
            "transport_mode": row.get("transport_mode", "road"),
            # Weather
            "weather_condition": weather_label,
            "weather_code": weather_code,
            "wind_speed_kmh": wind,
            "visibility_km": vis,
            # Traffic
            "traffic_congestion_level": (
                "Very High" if _safe_float(row.get("segment_congestion_idx", 0)) > 0.8 else
                "High"      if _safe_float(row.get("segment_congestion_idx", 0)) > 0.6 else
                "Medium"    if _safe_float(row.get("segment_congestion_idx", 0)) > 0.3 else "Low"
            ),
            "segment_congestion_idx": _safe_float(row.get("segment_congestion_idx", 0)),
            "port_congestion_idx": _safe_float(row.get("port_congestion_idx", 0)),
            # Disruption flags
            "road_closure_flag": int(_is_flag_set(row.get("road_closure_flag", "0"))),
            "strike_event_flag": int(str(row.get("strike_event_flag", "0")) in ("1", "True", "true")),
            "traffic_incident_flag": int(str(row.get("traffic_incident_flag", "0")) in ("1", "True", "true")),
            "customs_hold_flag": int(str(row.get("customs_hold_flag", "0")) in ("1", "True", "true")),
            "holiday_flag": int(str(row.get("holiday_flag", "0")) in ("1", "True", "true")),
            "maintenance_flag": int(str(row.get("maintenance_flag", "0")) in ("1", "True", "true")),
            "temp_breach_flag": int(str(row.get("temp_breach_flag", "0")) in ("1", "True", "true")),
            "border_crossing_flag": int(str(row.get("border_crossing_flag", "0")) in ("1", "True", "true")),
            "alternate_routes_avail": int(row.get("alternate_routes_avail", 0)),
            # Vehicle/driver
            "vehicle_type": "Tata 407", "vehicle_age_years": vehicle_age,
            "driver_experience_years": max(1.0, 10.0 - driver_hrs / 2),
            "driver_rest_hours_prior": max(0.0, 10.0 - driver_hrs),
            "night_driving_flag": int(row.get("is_night", 0) if "is_night" in row else 0),
            "vehicle_breakdown_flag": int(str(row.get("maintenance_flag", "0")) in ("1", "True", "true")),
            "accident_reported_flag": 0,
            # Route details
            "num_toll_plazas": int(_safe_float(row.get("segment_index", 5), 5) * 2),
            "num_state_border_crossings": int(_is_flag_set(row.get("border_crossing_flag", "0"))),
            "eway_bill_verified": 1,
            "gps_route_deviation_km": 0.0,
            "checkpoint_delay_minutes": round(delay_h * 60, 1),
            "origin_wh_congestion_pct": round(_safe_float(row.get("port_congestion_idx", 0.5), 0.5) * 100, 1),
            "dest_wh_congestion_pct": round(_safe_float(row.get("node_throughput_lag", 0)) * -50 + 50, 1),
            "upstream_shipment_delay_minutes": round(_safe_float(row.get("avg_delay_this_route", 0)) * 60, 1),
            # Indian specific
            "order_type": "B2B",
            "priority_level": "Priority" if risk_score > 60 else "Scheduled-Freight",
            "is_monsoon_season": int(_safe_float(row.get("seasonal_risk_score", 0)) > 0.3),
            "is_festival_season": int(_is_flag_set(row.get("holiday_flag", "0"))),
            "fuel_price_per_litre": 104.0,
            "shipment_value_inr": round(_safe_float(row.get("seasonal_risk_score", 0.3)) * 500000 + 50000, 0),
            "cargo_type": row.get("cargo_type", "General").strip().title(),
            # Risk
            "risk_score": risk_score, "risk_level": risk_level,
            "is_anomaly": is_anomaly,
            "delay_probability": round(min(risk_score / 100 * 1.1, 1.0), 3),
            "cascade_risk_score": round(_safe_float(row.get("route_disruption_cnt_30d", 0)) / 20, 3),
            "disruption_type": disruption_type,
            "disruption_flag": int(_is_flag_set(row.get("disruption_flag", "0"))),
            # Status
            "status": status, "is_delayed": is_delayed,
            "delay_duration_minutes": round(delay_h * 60, 1),
            "delay_hours_current": delay_h,
            "delay_severity": row.get("delay_severity", "low"),
            "recommended_action": row.get("recommended_action", "no_action"),
            # Rerouting
            "alt_route_needed": alt_needed,
            "reroute_options": reroute_options,
            # Global compat
            "speed_kmh": _safe_float(row.get("avg_speed_kmh", 40), 40.0),
            "value_usd": int(round(_safe_float(row.get("seasonal_risk_score", 0.3), 0.3) * 6000 + 600, 0)),
            "transit_days": round(planned_hrs / 24, 1),
            "top_risk_factors": risk_factors,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "created_at": created_at,
            # Historical data for analytics
            "route_avg_delay_7d": _safe_float(row.get("route_avg_delay_7d", 0)),
            "route_disruption_cnt_30d": int(_safe_float(row.get("route_disruption_cnt_30d", 0))),
            "carrier_on_time_rate": _safe_float(row.get("carrier_on_time_rate", 0.8), 0.8),
            "seasonal_risk_score": _safe_float(row.get("seasonal_risk_score", 0.3), 0.3),
            "same_lane_delay_ratio": _safe_float(row.get("same_lane_delay_ratio", 0.3), 0.3),
        }

    def _seed_alerts_from_high_risk(self) -> None:
        """Auto-generate alerts from high-risk CSV shipments."""
        high_risk = [s for s in self._shipments.values() if s["risk_score"] > 55]
        random.shuffle(high_risk)
        now = datetime.now(timezone.utc)
        for i, s in enumerate(high_risk[:20]):
            disruption = s.get("disruption_type", "none")
            weather = s.get("weather_code", "clear")
            flags = []
            if s.get("road_closure_flag"):
                flags.append("🚧 Road closure")
            if s.get("strike_event_flag"):
                flags.append("🪧 Strike event")
            if weather in ("storm", "heavy_rain", "fog"):
                icon = WEATHER_LABEL.get(weather, ("", "⚠️"))[1]
                flags.append(f"{icon} {WEATHER_LABEL.get(weather, (weather,))[0]} weather")
            if s.get("customs_hold_flag"):
                flags.append("🛃 Customs hold")
            if not flags:
                flags.append(f"Risk score {s['risk_score']:.0f}/100")

            msg = (
                f"⚠️ {s['id']} ({s['origin_city']} → {s['destination_city']}): "
                f"{', '.join(flags[:2])}. "
                f"Carrier: {s['carrier_company']} | {s['cargo_type']}"
            )
            self._alerts.append({
                "id": f"IND-ALT-{uuid.uuid4().hex[:6].upper()}",
                "shipment_id": s["id"],
                "panel": "india",
                "type": "anomaly_detected" if s["is_anomaly"] else (
                    "weather_warning" if weather in ("storm", "heavy_rain", "fog") else "high_risk_flag"
                ),
                "severity": "critical" if s["risk_score"] > 75 else "high",
                "message": msg,
                "risk_score": s["risk_score"],
                "delay_probability": s.get("delay_probability", 0.5),
                "cascade_risk": s.get("cascade_risk_score", 0.3),
                "top_risk_factors": s.get("top_risk_factors", []),
                "reroute_options": s.get("reroute_options", []),
                "alternate_routes": s.get("reroute_options", []),
                "weather_warning": weather in ("storm", "heavy_rain", "fog", "rain"),
                "weather_icon": WEATHER_LABEL.get(weather, ("", "☁️"))[1],
                "weather_label": WEATHER_LABEL.get(weather, (weather, ""))[0],
                "created_at": (now - timedelta(minutes=i * 5)).isoformat(),
            })

    def _seed_fallback_mock(self) -> None:
        """Minimal fallback if CSV is missing."""
        cities = [
            ("Mumbai", "Maharashtra", 19.076, 72.877),
            ("Delhi", "Delhi", 28.613, 77.209),
            ("Bangalore", "Karnataka", 12.971, 77.594),
            ("Chennai", "Tamil Nadu", 13.082, 80.270),
            ("Kolkata", "West Bengal", 22.572, 88.363),
        ]
        for i in range(10):
            orig = cities[i % len(cities)]
            dest = cities[(i + 2) % len(cities)]
            prog = round(0.1 + i * 0.08, 2)
            risk = round(20 + i * 7, 1)
            sid = f"IND-MOCK-{i:04d}"
            self._shipments[sid] = {
                "id": sid, "shipment_id": sid, "panel": "india",
                "origin_city": orig[0], "origin_state": orig[1],
                "origin": f"{orig[0]}, {orig[1]}",
                "destination_city": dest[0], "destination_state": dest[1],
                "destination": f"{dest[0]}, {dest[1]}",
                "origin_lat": orig[2], "origin_lng": orig[3],
                "destination_lat": dest[2], "destination_lng": dest[3],
                "lat": round(orig[2] + (dest[2]-orig[2])*prog, 4),
                "lng": round(orig[3] + (dest[3]-orig[3])*prog, 4),
                "carrier_company": "Delhivery", "carrier": "Delhivery",
                "cargo_type": "Electronics", "status": "in_transit",
                "risk_score": risk, "risk_level": "high" if risk > 65 else "medium",
                "is_anomaly": risk > 70, "delay_probability": round(risk/100, 2),
                "cascade_risk_score": 0.2, "progress": prog,
                "distance_km": 800.0, "planned_transit_hours": 20.0,
                "eta_hours": round(20*(1-prog), 1),
                "weather_condition": "☀️ Clear", "weather_code": "clear",
                "traffic_congestion_level": "Medium",
                "is_delayed": False, "delay_duration_minutes": 0,
                "vehicle_type": "Tata 407", "vehicle_age_years": 3.0,
                "driver_experience_years": 5.0, "driver_rest_hours_prior": 8.0,
                "night_driving_flag": 0, "num_toll_plazas": 8,
                "num_state_border_crossings": 1, "eway_bill_verified": 1,
                "gps_route_deviation_km": 0, "checkpoint_delay_minutes": 0,
                "origin_wh_congestion_pct": 40.0, "dest_wh_congestion_pct": 30.0,
                "upstream_shipment_delay_minutes": 0, "vehicle_breakdown_flag": 0,
                "accident_reported_flag": 0, "road_closure_flag": 0,
                "strike_event_flag": 0, "customs_hold_flag": 0,
                "order_type": "B2B", "priority_level": "Scheduled-Freight",
                "is_monsoon_season": 0, "is_festival_season": 0,
                "fuel_price_per_litre": 104.0, "shipment_value_inr": 100000,
                "speed_kmh": 50.0, "value_usd": 1200, "transit_days": 1.0,
                "top_risk_factors": ["✅ No critical risk factors — standard monitoring"],
                "reroute_options": [], "alt_route_needed": False,
                "carrier_on_time_rate": 0.8, "route_avg_delay_7d": 0.5,
                "route_disruption_cnt_30d": 1, "seasonal_risk_score": 0.2,
                "same_lane_delay_ratio": 0.3,
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

    @staticmethod
    def _mock_risk_factors(weather: str, traffic: str, is_delayed: bool) -> list:
        """Legacy helper kept for compatibility."""
        factors = []
        if weather in ("Rain", "Heavy Rain", "Storm", "Fog"):
            factors.append(f"Weather: {weather} conditions affecting road visibility")
        if traffic in ("High", "Very High"):
            factors.append("High traffic congestion on route")
        if is_delayed:
            factors.append("Active delay — shipment behind schedule")
        if not factors:
            factors.append("Standard monitoring — no critical factors")
        return factors
