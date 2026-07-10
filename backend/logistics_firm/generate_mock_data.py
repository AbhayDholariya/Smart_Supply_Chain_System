#!/usr/bin/env python
# backend/generate_mock_data.py
"""
Generate mock shipment and alert data for testing without Firebase
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import random
from datetime import datetime, timedelta, timezone

# Mock data storage (in-memory for testing)
MOCK_DATA = {
    "shipments": [],
    "alerts": []
}

def generate_mock_shipments(count=5):
    """Generate realistic mock shipment data"""
    carriers = ["Maersk", "MSC", "CMA-CGM", "COSCO", "Evergreen"]
    origins = ["Mumbai", "Shanghai", "Shenzhen", "Dubai", "Singapore"]
    destinations = ["Rotterdam", "Los Angeles", "Hamburg", "Antwerp", "Port Said"]
    statuses = ["in-transit", "at-port", "delayed", "on-schedule"]
    cargo_types = ["Electronics", "Chemicals", "Textiles", "Machinery", "Containers"]
    
    shipments = []
    for i in range(count):
        shipment = {
            "id": f"SHP-{4420 + i}",
            "origin": random.choice(origins),
            "destination": random.choice(destinations),
            "carrier": random.choice(carriers),
            "lat": round(random.uniform(-60, 60), 2),
            "lng": round(random.uniform(-180, 180), 2),
            "status": random.choice(statuses),
            "risk_score": round(random.uniform(10, 95), 1),
            "risk_level": random.choice(["low", "medium", "high", "critical"]),
            "is_anomaly": random.choice([True, False]),
            "speed_kmh": round(random.uniform(15, 40), 1),
            "progress": round(random.uniform(0.1, 0.95), 2),
            "cargo_type": random.choice(cargo_types),
            "value_usd": random.randint(50000, 500000),
            "eta_days": round(random.uniform(3, 30), 1),
            "top_risk_factors": random.sample(
                ["weather", "congestion", "piracy", "mechanical_issue", "port_delay"],
                k=random.randint(1, 3)
            ),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        shipments.append(shipment)
    
    return shipments

def generate_mock_alerts(count=3):
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
    shipments = generate_mock_shipments(10)  # Get some shipments for reference
    
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

def display_mock_data():
    """Display mock data in formatted JSON"""
    print("\n" + "="*80)
    print("📊 MOCK DATA GENERATED FOR TESTING")
    print("="*80)
    
    # Generate data
    shipments = generate_mock_shipments(5)
    alerts = generate_mock_alerts(3)
    
    # Display shipments
    print("\n🚢 SHIPMENTS (GET /shipments/live)")
    print("-" * 80)
    print(json.dumps(shipments, indent=2))
    
    # Display alerts
    print("\n⚠️  ALERTS (GET /alerts?hours=24)")
    print("-" * 80)
    print(json.dumps(alerts, indent=2))
    
    print("\n" + "="*80)
    print("✅ This is what your API should return!")
    print("="*80 + "\n")

def export_mock_data():
    """Export mock data as JSON file"""
    shipments = generate_mock_shipments(10)
    alerts = generate_mock_alerts(5)
    
    data = {
        "shipments": shipments,
        "alerts": alerts,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "note": "Mock data for testing without Firebase"
    }
    
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mock_data.json")
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Mock data exported to: {output_file}")

if __name__ == "__main__":
    display_mock_data()
    export_mock_data()
