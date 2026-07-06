from django.urls import path
from .views import DelayPredictionView, RouteRecommendationView

urlpatterns = [
    path("predict-delay/", DelayPredictionView.as_view(), name="predict-delay"),
    path("recommend-route/", RouteRecommendationView.as_view(), name="recommend-route"),
]
