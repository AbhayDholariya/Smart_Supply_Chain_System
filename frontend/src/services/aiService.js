import apiClient from "./apiClient";

export const aiService = {
  predictDelay: (features) => apiClient.post("/ai/predict-delay/", features),

  recommendRoute: (payload) => apiClient.post("/ai/recommend-route/", payload),
};
