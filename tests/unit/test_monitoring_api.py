import pytest
from fastapi.testclient import TestClient
from argus.api.main import app
import os

client = TestClient(app)

def test_get_registry():
    response = client.get("/api/v1/monitoring/registry")
    if os.path.exists("artifacts/models/registry.yaml"):
        assert response.status_code == 200
        assert "models" in response.json()
    else:
        assert response.status_code == 404

def test_get_drift():
    if os.path.exists("artifacts/models/registry.yaml"):
        response = client.get("/api/v1/monitoring/drift/model_d2_coral")
        assert response.status_code == 200
        data = response.json()
        assert "feature_drift_score" in data
        assert "warning_state" in data
        assert "prediction_distribution" in data
