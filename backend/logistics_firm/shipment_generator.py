# backend/shipment_generator.py
"""
Simulates real-time shipment GPS updates every 5 seconds.
Writes to Firestore -> triggers Cloud Function -> risk re-scored.
"""

import asyncio
import random
import math
import uuid
from datetime import datetime, timezone
from typing import Optional

from backend.logistics_firm.firebase_client import FirebaseClient

# ─── Realistic shipping lane waypoints ────────────────────────────────────
SHIPPING_LANES = {
    "Mumbai-Rotterdam": {
        "origin": "Mumbai", "destination": "Rotterdam",
        "waypoints": [
            (19.08, 72.88),   # Mumbai
            (6.93,  79.84),   # Colombo
            (12.02, 44.03),   # Gulf of Aden
            (21.48, 39.17),   # Jeddah
            (30.0,  32.57),   # Suez Canal
            (31.26, 32.30),   # Port Said
            (36.89, 20.00),   # Mediterranean
            (51.92, 4.48),    # Rotterdam
        ],
        "transit_countries": ["India", "Sri Lanka", "Yemen", "Egypt", "Netherlands"],
        "avg_speed_kmh": 28,
        "carriers": ["Maersk", "MSC", "CMA-CGM"],
    },
    "Shanghai-Los-Angeles": {
        "origin": "Shanghai", "destination": "Los Angeles",
        "waypoints": [
            (31.23, 121.47),  # Shanghai
            (1.29,  103.85),  # Singapore
            (20.00, 140.00),  # Philippine Sea
            (33.72, -118.27), # Los Angeles
        ],
        "transit_countries": ["China", "Singapore", "USA"],
        "avg_speed_kmh": 32,
        "carriers": ["COSCO", "Evergreen", "Maersk"],
    },
    "Dubai-Hamburg": {
        "origin": "Dubai", "destination": "Hamburg",
        "waypoints": [
            (25.20, 55.27),   # Dubai
            (21.48, 39.17),   # Jeddah
            (30.0,  32.57),   # Suez
            (36.89, 20.00),   # Mediterranean
            (53.55, 9.99),    # Hamburg
        ],
        "transit_countries": ["UAE", "Saudi Arabia", "Egypt", "Germany"],
        "avg_speed_kmh": 26,
        "carriers": ["Hapag-Lloyd", "MSC"],
    },
}

STATUS_PROGRESSION = [
    "pending_departure",
    "in_transit",
    "in_transit",
    "in_transit",
    "at_port",
    "customs_hold",
    "in_transit",
    "in_transit",
    "arrived",
]


class ShipmentGenerator:
    """
    Generates N synthetic shipments and pushes live GPS updates to Firestore.
    Each shipment follows a predefined lane with interpolated GPS coordinates.
    """

    def __init__(self, n_shipments: int = 15, update_interval: float = 5.0) -> None:
        self.n_shipments = n_shipments
        self.update_interval = update_interval
        self.firebase = FirebaseClient()
        self.shipments: dict[str, dict] = {}
        self._running = False

    def _create_shipment(self, idx: int) -> dict:
        lane_name = random.choice(list(SHIPPING_LANES.keys()))
        lane = SHIPPING_LANES[lane_name]
        carrier = random.choice(lane["carriers"])
        shipment_id = f"SHP-{4400 + idx}"

        return {
            "id": shipment_id,
            "lane_name": lane_name,
            "origin": lane["origin"],
            "destination": lane["destination"],
            "carrier": carrier,
            "transit_countries": lane["transit_countries"],
            "waypoints": lane["waypoints"],
            "avg_speed_kmh": lane["avg_speed_kmh"],
            "waypoint_idx": 0,
            "progress": random.uniform(0.0, 0.85),  # start mid-journey
            "status_idx": random.randint(1, 4),
            "cargo_type": random.choice(["Electronics", "Pharmaceuticals", "Automotive", "Textiles", "Chemicals"]),
            "value_usd": random.randint(50_000, 5_000_000),
            "weight_tonnes": random.uniform(5, 28),
            "container_count": random.randint(1, 40),
        }

    def _interpolate_position(self, shipment: dict) -> tuple[float, float]:
        waypoints = shipment["waypoints"]
        progress = shipment["progress"]
        n = len(waypoints) - 1

        segment = min(int(progress * n), n - 1)
        local_t = (progress * n) - segment

        lat1, lng1 = waypoints[segment]
        lat2, lng2 = waypoints[segment + 1]

        lat = lat1 + (lat2 - lat1) * local_t
        lng = lng1 + (lng2 - lng1) * local_t

        # Add small GPS noise
        lat += random.gauss(0, 0.02)
        lng += random.gauss(0, 0.02)
        return round(lat, 6), round(lng, 6)

    def _advance_shipment(self, shipment: dict) -> dict:
        speed = shipment["avg_speed_kmh"]

        # Simulate events
        event_roll = random.random()
        if event_roll < 0.02:   # 2% chance: stopped
            actual_speed = random.uniform(0, 0.5)
        elif event_roll < 0.05: # 3% chance: slow (congestion)
            actual_speed = speed * random.uniform(0.3, 0.6)
        else:
            actual_speed = speed * random.uniform(0.85, 1.15)

        # Advance progress (proportional to speed + interval)
        total_distance = 11000  # approximate km per lane (simplified)
        progress_increment = (actual_speed * self.update_interval / 3600) / total_distance
        shipment["progress"] = min(shipment["progress"] + progress_increment, 1.0)

        # Status update
        status_idx = min(int(shipment["progress"] * len(STATUS_PROGRESSION)), len(STATUS_PROGRESSION) - 1)
        current_status = STATUS_PROGRESSION[status_idx]

        lat, lng = self._interpolate_position(shipment)

        # Dwell time (increases at ports)
        dwell = 0.0
        if current_status in ("at_port", "customs_hold"):
            dwell = random.uniform(12, 72)

        hours_stationary = 0.0
        if actual_speed < 1.0:
            hours_stationary = random.uniform(0.5, 18)

        weather_severity = self._get_weather_severity(lat, lng)

        return {
            "lat": lat,
            "lng": lng,
            "status": current_status,
            "speed_kmh": round(actual_speed, 2),
            "dwell_time_hours": round(dwell, 2),
            "hours_stationary": round(hours_stationary, 2),
            "weather_severity": round(weather_severity, 2),
            "stops_count": shipment.get("stops_count", 0),
            "on_time_rate": 0.87,
            "distance_km": total_distance,
            "transit_days": round(shipment["progress"] * 25, 2),
            "speed_variance": round(abs(actual_speed - speed) / speed * 10, 2) if speed > 0 else 0,
            "progress": round(shipment["progress"], 4),
        }

    @staticmethod
    def _get_weather_severity(lat: float, lng: float) -> float:
        """Simulate weather based on geographic zone."""
        # Cyclone belt: Bay of Bengal / Arabian Sea
        if 5 < lat < 25 and 55 < lng < 100:
            return random.triangular(2.0, 9.0, 5.5)
        # Red Sea / Gulf of Aden (conflicts + weather)
        if 10 < lat < 30 and 35 < lng < 55:
            return random.triangular(3.0, 8.0, 5.0)
        # North Atlantic
        if lat > 45 and -20 < lng < 10:
            return random.triangular(1.0, 7.0, 3.5)
        return random.triangular(0.5, 4.0, 1.5)

    async def _push_update(self, shipment_id: str, update_data: dict, base: dict) -> None:
        """Write full shipment document to Firestore."""
        payload = {
            "origin": base["origin"],
            "destination": base["destination"],
            "carrier": base["carrier"],
            "transit_countries": base["transit_countries"],
            "cargo_type": base["cargo_type"],
            "value_usd": base["value_usd"],
            "weight_tonnes": base["weight_tonnes"],
            "container_count": base["container_count"],
            **update_data,
        }
        self.firebase.upsert_shipment(shipment_id, payload)

    async def run(self) -> None:
        """Main loop: generate shipments and push updates every 5 seconds."""
        print(f"[Generator] Creating {self.n_shipments} shipments...")
        for i in range(self.n_shipments):
            self.shipments[f"SHP-{4400 + i}"] = self._create_shipment(i)

        self._running = True
        print(f"[Generator] Starting live updates every {self.update_interval}s...")

        iteration = 0
        while self._running:
            for shipment_id, shipment in self.shipments.items():
                if shipment["progress"] >= 1.0:
                    # Reset completed shipment
                    self.shipments[shipment_id] = self._create_shipment(
                        int(shipment_id.split("-")[1]) - 4400
                    )
                    continue

                update = self._advance_shipment(shipment)
                self.shipments[shipment_id].update(update)

                await self._push_update(shipment_id, update, shipment)

            iteration += 1
            if iteration % 12 == 0:
                print(f"[Generator] Iteration {iteration} — {len(self.shipments)} active shipments")

            await asyncio.sleep(self.update_interval)

    def stop(self) -> None:
        self._running = False
        print("[Generator] Stopped.")


async def main():
    gen = ShipmentGenerator(n_shipments=15, update_interval=5.0)
    try:
        await gen.run()
    except KeyboardInterrupt:
        gen.stop()


if __name__ == "__main__":
    asyncio.run(main())
