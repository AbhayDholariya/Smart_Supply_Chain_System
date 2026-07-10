#!/usr/bin/env python
# backend/run_and_show_apis.py
"""
Start FastAPI server on localhost:6000 and display all available APIs
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def display_apis():
    """Display all available APIs"""
    
    apis = {
        "🔵 HEALTH CHECK": {
            "endpoint": "GET /health",
            "description": "Check API server status",
            "url": "http://localhost:6000/health",
            "response": {"status": "healthy", "timestamp": "2026-04-25T..."}
        },
        
        "📦 SHIPMENTS": {
            "endpoint": "GET /shipments/live",
            "description": "Get all active shipments with position, risk score, and ETA",
            "url": "http://localhost:6000/shipments/live",
            "query_params": "None",
            "response": {
                "type": "List[ShipmentResponse]",
                "sample": {
                    "id": "SHP-4421",
                    "origin": "Mumbai",
                    "destination": "Rotterdam",
                    "carrier": "Maersk",
                    "lat": 12.34,
                    "lng": 56.78,
                    "status": "in-transit",
                    "risk_score": 42.5,
                    "risk_level": "medium",
                    "is_anomaly": False,
                    "speed_kmh": 28.5,
                    "progress": 0.75,
                    "cargo_type": "Electronics",
                    "value_usd": 125000,
                    "eta_days": 5.2,
                    "top_risk_factors": ["weather", "congestion"]
                }
            }
        },
        
        "⚠️  ALERTS": {
            "endpoint": "GET /alerts",
            "description": "Get recent disruption alerts",
            "url": "http://localhost:6000/alerts",
            "query_params": {
                "hours": "int (default: 1) - Last N hours to fetch alerts from"
            },
            "example_url": "http://localhost:6000/alerts?hours=24",
            "response": {
                "type": "List[AlertResponse]",
                "sample": {
                    "id": "ALT-ABC123",
                    "shipment_id": "SHP-4421",
                    "type": "high_risk_flag",
                    "severity": "high",
                    "message": "Unusual dwell time detected at port",
                    "risk_score": 78.5,
                    "alternate_routes": [
                        {
                            "rank": 1,
                            "path": ["Mumbai", "Singapore", "Rotterdam"],
                            "total_cost_usd": 4500,
                            "transit_days": 22,
                            "composite_risk": 35.2
                        }
                    ],
                    "created_at": "2026-04-25T..."
                }
            }
        },
        
        "🛣️  REROUTE": {
            "endpoint": "POST /reroute/{shipment_id}",
            "description": "Get alternate routes for a high-risk shipment",
            "url": "http://localhost:6000/reroute/SHP-4421",
            "method": "POST",
            "request_body": {
                "reason": "str (optional) - Reason for reroute",
                "priority": "str (optional) - 'normal' or 'urgent'"
            },
            "example_payload": {
                "reason": "Suez Canal disruption",
                "priority": "urgent"
            },
            "response": {
                "type": "RerouteResponse",
                "sample": {
                    "shipment_id": "SHP-4421",
                    "current_risk_score": 78.5,
                    "routes": [
                        {
                            "rank": 1,
                            "path": ["Mumbai", "Cape Town", "Rotterdam"],
                            "total_cost_usd": 5200,
                            "transit_days": 28,
                            "composite_risk": 42.1,
                            "savings_vs_original": {
                                "cost_reduction": -700,
                                "time_increase": 10,
                                "risk_reduction": 36.4
                            }
                        }
                    ],
                    "recommended_route_idx": 0,
                    "analysis": "Route via Cape of Good Hope recommended..."
                }
            }
        },
        
        "📊 ANALYSIS (ML)": {
            "endpoint": "POST /analyze",
            "description": "Run ML analysis on shipment features (anomaly + risk scoring)",
            "url": "http://localhost:5001/analyze",
            "note": "Flask AI service on port 5001",
            "request_body": {
                "shipment_id": "str",
                "origin": "str",
                "destination": "str",
                "carrier": "str",
                "lat": "float",
                "lng": "float",
                "speed_kmh": "float",
                "dwell_time_hours": "float",
                "hours_stationary": "float",
                "weather_severity": "float",
                "transit_countries": "list[str]",
                "stops_count": "int",
                "on_time_rate": "float",
                "distance_km": "float",
                "transit_days": "float",
                "speed_variance": "float"
            },
            "response": {
                "risk_score": "float (0-100)",
                "risk_level": "str (low/medium/high/critical)",
                "is_anomaly": "bool",
                "anomaly_score": "float (0-1)",
                "component_scores": "dict",
                "top_risk_factors": "list[str]",
                "recommended_action": "str"
            }
        },
        
        "🔔 WEBHOOK": {
            "endpoint": "POST /webhook/risk-update",
            "description": "Receive AI analysis results from Cloud Functions",
            "url": "http://localhost:6000/webhook/risk-update",
            "internal": "True - Called by Cloud Functions bridge",
            "request_body": {
                "shipment_id": "str",
                "risk_score": "float",
                "risk_level": "str",
                "is_anomaly": "bool",
                "anomaly_score": "float",
                "top_risk_factors": "list[str]",
                "recommended_action": "str"
            }
        },
        
        "🔗 WEBSOCKET": {
            "endpoint": "WS /ws/{topic}",
            "description": "Real-time WebSocket for live updates",
            "url": "ws://localhost:6000/ws/all",
            "supported_topics": [
                "all - All events",
                "shipments - Shipment updates only",
                "alerts - Alert events only",
                "shipment:SHP-4421 - Specific shipment updates"
            ],
            "events": [
                "initial_state - Sent on connection",
                "shipments_updated - When shipment status changes",
                "risk_updated - When risk score changes",
                "reroute_recommendation - When alternate routes computed",
                "auto_reroute_computed - Auto-reroute triggered"
            ]
        },
        
        "📚 DOCUMENTATION": {
            "endpoint": "GET /docs",
            "description": "Interactive API documentation (Swagger UI)",
            "url": "http://localhost:6000/docs"
        },
        
        "🔍 OPENAPI": {
            "endpoint": "GET /openapi.json",
            "description": "OpenAPI schema JSON",
            "url": "http://localhost:6000/openapi.json"
        }
    }
    
    print("\n" + "="*80)
    print("🚀 SUPPLY CHAIN AI - API ENDPOINTS")
    print("="*80)
    print(f"\n🌐 Server: http://localhost:6000")
    print(f"📡 WebSocket: ws://localhost:6000")
    print(f"🔥 Flask AI (ML): http://localhost:5001")
    
    for category, details in apis.items():
        print(f"\n{'─'*80}")
        print(f"\n{category}")
        print(f"{'─'*80}")
        
        # Print endpoint info
        if "endpoint" in details:
            print(f"\n📍 {details['endpoint']}")
        if "description" in details:
            print(f"   {details['description']}")
        
        if "url" in details:
            print(f"\n🔗 URL: {details['url']}")
        if "example_url" in details:
            print(f"   Example: {details['example_url']}")
        
        if "query_params" in details and details["query_params"] != "None":
            print(f"\n📋 Query Parameters:")
            if isinstance(details["query_params"], dict):
                for param, desc in details["query_params"].items():
                    print(f"   • {param}: {desc}")
            else:
                print(f"   {details['query_params']}")
        
        if "request_body" in details:
            print(f"\n📤 Request Body:")
            if isinstance(details["request_body"], dict):
                for field, dtype in details["request_body"].items():
                    print(f"   • {field}: {dtype}")
            else:
                print(f"   {details['request_body']}")
        
        if "response" in details:
            print(f"\n📥 Response:")
            if isinstance(details["response"], dict):
                if "type" in details["response"]:
                    print(f"   Type: {details['response']['type']}")
                if "sample" in details["response"]:
                    print(f"   Sample: {json.dumps(details['response']['sample'], indent=6)}")
            else:
                print(f"   {details['response']}")
        
        if "supported_topics" in details:
            print(f"\n📍 Supported Topics:")
            for topic in details["supported_topics"]:
                print(f"   • {topic}")
        
        if "events" in details:
            print(f"\n📨 Events:")
            for event in details["events"]:
                print(f"   • {event}")
        
        if "internal" in details:
            print(f"\n⚙️  Internal: {details['internal']}")
        
        if "note" in details:
            print(f"\n💡 {details['note']}")
    
    print(f"\n{'='*80}")
    print("✨ To test endpoints, use curl, Postman, or visit http://localhost:6000/docs")
    print("="*80 + "\n")


def main():
    print("\n" + "="*80)
    print("Starting Supply Chain AI Backend on localhost:6000...")
    print("="*80 + "\n")
    
    # Display all APIs
    display_apis()
    
    # Start the FastAPI server
    print("\n🚀 Starting FastAPI server...\n")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "backend.fastapi_backend_main:app",
            "--host", "0.0.0.0",
            "--port", "6000",
            "--reload"
        ], cwd=project_root)
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
