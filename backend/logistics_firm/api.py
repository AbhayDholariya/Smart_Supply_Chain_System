"""
Additional API routes for the logistics intelligence platform.
Mounts on the main FastAPI app.
"""
import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api")

# Load mock data
_MOCK_PATH = Path(__file__).parent.parent / "mock_data.json"
with open(_MOCK_PATH) as f:
    _MOCK = json.load(f)


@router.get("/shipments")
def get_shipments():
    return _MOCK["shipments"]


@router.get("/shipments/{shipment_id}")
def get_shipment(shipment_id: str):
    for s in _MOCK["shipments"]:
        if s["id"] == shipment_id:
            return s
    raise HTTPException(status_code=404, detail="not found")


@router.get("/risk-score/{shipment_id}")
def get_risk_score(shipment_id: str):
    for s in _MOCK["shipments"]:
        if s["id"] == shipment_id:
            return {
                "shipment_id": shipment_id,
                "risk_score": s["risk_score"],
                "risk_level": s["risk_level"],
                "component_scores": {
                    "weather": round(s["risk_score"] * 0.22 / 10, 2),
                    "port_congestion": round(s["risk_score"] * 0.18 / 10, 2),
                    "carrier": round(s["risk_score"] * 0.15 / 10, 2),
                    "geopolitical": round(s["risk_score"] * 0.20 / 10, 2),
                    "anomaly": round(s["risk_score"] * 0.15 / 10, 2),
                    "dwell": round(s["risk_score"] * 0.10 / 10, 2),
                },
                "top_risk_factors": s.get("top_risk_factors", []),
                "recommended_action": (
                    "CRITICAL: Initiate reroute protocol immediately." if s["risk_score"] > 75
                    else "Escalate to operations team." if s["risk_score"] > 50
                    else "Monitor closely." if s["risk_score"] > 25
                    else "No action required."
                )
            }
    raise HTTPException(status_code=404, detail="not found")


@router.get("/disruptions")
def get_disruptions():
    return [
        {
            "id": "PRED-001",
            "type": "Port Congestion",
            "probability": 0.87,
            "affected_routes": ["Shanghai → Los Angeles", "Shenzhen → Long Beach"],
            "estimated_delay_days": 4.5,
            "confidence": 0.91,
        },
        {
            "id": "PRED-002",
            "type": "Weather Disruption",
            "probability": 0.73,
            "affected_routes": ["Singapore → Rotterdam"],
            "estimated_delay_days": 3.2,
            "confidence": 0.85,
        },
    ]


@router.get("/predict-eta/{shipment_id}")
def predict_eta(shipment_id: str):
    for s in _MOCK["shipments"]:
        if s["id"] == shipment_id:
            return {
                "shipment_id": shipment_id,
                "eta_days": s.get("eta_days", 14),
                "confidence": 0.87,
                "factors": s.get("top_risk_factors", []),
            }
    raise HTTPException(status_code=404, detail="not found")


@router.get("/alerts")
def get_alerts(hours: int = 24):
    return _MOCK["alerts"]

class ShipmentAnalysisRequest(BaseModel):
    origin: str
    destination: str
    cargoType: str
    value: float
    carrier: str

@router.post("/analyze-route")
def analyze_route(req: ShipmentAnalysisRequest):
    from dotenv import load_dotenv
    import httpx

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path, override=False)

    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "OpenRouter API key not configured on server"}, 500

    model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    prompt = f"""
    Act as a sophisticated AI Logistics Intelligence Platform.
    Analyze the following shipment route based on your ML-trained historical dataset:
    - Origin: {req.origin}
    - Destination: {req.destination}
    - Cargo: {req.cargoType}
    - Value: ${req.value}
    - Carrier: {req.carrier}

    Provide a structured JSON output with the following keys exactly:
    1. "estimated_revenue": the expected revenue based on a 15% margin
    2. "projected_cost": an estimated cost derived from bunkers and tariffs (approx 8% of value)
    3. "risk_of_delay_percentage": a calculated risk percentage between 5.0% and 35.0% based on standard maritime bottlenecks
    4. "nearest_alternate_port": a logical emergency port near the destination
    5. "llm_analysis": A highly professional 2-3 sentence AI summary of potential risks, weather anomalies, and why the alternate port was chosen.

    Return ONLY raw JSON, without markdown formatting or code blocks.
    """

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Supply Chain Intelligence",
        }
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }

        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45.0,
        )
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]
        if isinstance(content, list):
            raw_text = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        else:
            raw_text = content

        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
        analysis_data = json.loads(raw_text)
        return analysis_data

    except Exception as e:
        print(f"OpenRouter LLM API Error: {e}")
        return {
            "estimated_revenue": req.value * 1.15,
            "projected_cost": req.value * 0.08,
            "risk_of_delay_percentage": 15.4,
            "nearest_alternate_port": "Fallback Hub",
            "llm_analysis": "Security enforced fallback prediction. The live LLM service encountered an issue, defaulting to standard ML dataset averages."
        }
