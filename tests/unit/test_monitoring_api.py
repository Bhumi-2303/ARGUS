import os
from fastapi.testclient import TestClient
from argus.api.main import app
from argus.security.auth import create_access_token

client = TestClient(app)

def get_auth_headers():
    token = create_access_token("testuser", "VIEWER")
    return {"Authorization": f"Bearer {token}"}

def test_get_registry():
    response = client.get("/api/v1/monitoring/registry", headers=get_auth_headers())
    if os.path.exists("artifacts/models/registry.yaml"):
        assert response.status_code == 200

def test_get_drift():
    if os.path.exists("artifacts/models/registry.yaml"):
        response = client.get("/api/v1/monitoring/drift/model_d2_coral", headers=get_auth_headers())
        assert response.status_code == 200
        data = response.json()
        assert "feature_drift_score" in data
        assert "warning_state" in data
        assert "prediction_distribution" in data
