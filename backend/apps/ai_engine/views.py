from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .predictor import predict_delay_risk, recommend_route


class DelayPredictionView(APIView):
    """POST shipment features → delay risk score."""
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        risk = predict_delay_risk(request.data)
        return Response({"delay_risk_score": risk})


class RouteRecommendationView(APIView):
    """POST origin/destination → optimized route suggestion."""
    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        origin = request.data.get("origin", "")
        destination = request.data.get("destination", "")
        avoid_tolls = request.data.get("avoid_tolls", False)
        result = recommend_route(origin, destination, avoid_tolls)
        return Response(result)
