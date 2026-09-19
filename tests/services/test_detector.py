#!/usr/bin/env python3
"""
Test script for verifying ARGUS FastAPI service endpoints.
"""

from fastapi.testclient import TestClient
from argus.services.detector.main import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        print("Health check response:", response.status_code, response.json())
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["model_loaded"] is True

def test_predict_array():
    with TestClient(app) as client:
        payload = [
            {
                "pkt_mean_to_max": 0.95,
                "tcp_flag_density": 1.0,
                "log_pkt_mean": 4.2,
                "log_pkt_max": 4.3
            },
            {
                "pkt_mean_to_max": 0.05,
                "tcp_flag_density": 0.0,
                "log_pkt_mean": 1.0,
                "log_pkt_max": 1.2
            }
        ]
        response = client.post("/predict", json=payload)
        print("Predict response status:", response.status_code)
        data = response.json()
        print("Predict response data:", data)
        assert response.status_code == 200
        assert "predictions" in data
        assert len(data["predictions"]) == 2
        for item in data["predictions"]:
            assert "prediction" in item
            assert "probability" in item
            assert "threshold" in item
            assert "shap_values" in item
            assert len(item["shap_values"]) == 4

if __name__ == "__main__":
    test_health()
    test_predict_array()
    print("\n[✓] All API endpoint tests passed successfully!")
