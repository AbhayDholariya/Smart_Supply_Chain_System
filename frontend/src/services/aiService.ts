import apiClient from "./apiClient";

export const aiService = {
  predictDelay: (features: {
    distance_km: number;
    weather_severity: number;
    traffic_index: number;
    supplier_performance_score: number;
  }) => apiClient.post<{ delay_risk_score: number }>("/ai/predict-delay/", features),

  recommendRoute: (payload: {
    origin: string;
    destination: string;
    avoid_tolls?: boolean;
  }) => apiClient.post<{ recommended_route: string; estimated_duration_min: number | null; total_distance_km: number | null }>("/ai/recommend-route/", payload),
};
