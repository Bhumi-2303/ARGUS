"""Integration tests for all ARGUS API v1 endpoints."""

import pytest
from fastapi.testclient import TestClient

from argus.api.main import app

client = TestClient(app)


def test_get_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models_loaded" in data


def test_get_domains():
    response = client.get("/api/v1/domains")
    assert response.status_code == 200
    data = response.json()
    assert "domains" in data
    assert len(data["domains"]) >= 3
    domain_ids = [d["domain_id"] for d in data["domains"]]
    assert "ciciot" in domain_ids
    assert "nfton" in domain_ids
    assert "iec104" in domain_ids


def test_get_models():
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    model_names = [m["name"] for m in data["models"]]
    assert "model_d2_coral" in model_names
    assert "xgb_source" in model_names


def test_predict_endpoint():
    payload = {
        "features": {
            "pkt_mean_to_max": 0.5,
            "tcp_flag_density": 1.0,
            "log_pkt_mean": 4.0,
            "log_pkt_max": 4.5
        },
        "model_name": "model_d2_coral"
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "probability" in data
    assert "prediction" in data
    assert data["prediction"] in (0, 1)


def test_shift_endpoint():
    response = client.get("/api/v1/shift?domain=nfton&window_size=100")
    assert response.status_code == 200
    data = response.json()
    assert data["target_domain"] == "nfton"
    assert "domain_shift" in data
    assert len(data["feature_shifts"]) == 4


def test_explain_endpoint():
    payload = {
        "features": {
            "pkt_mean_to_max": 0.5,
            "tcp_flag_density": 1.0,
            "log_pkt_mean": 4.0,
            "log_pkt_max": 4.5
        },
        "model_name": "model_d2_coral"
    }
    response = client.post("/api/v1/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "base_value" in data
    assert "shap_values" in data
    assert "top_feature" in data


def test_test_cases_endpoint():
    response = client.get("/api/v1/data/test-cases")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    case_ids = [c["id"] for c in data]
    assert "ciciot-benign" in case_ids
    assert "ciciot-attack" in case_ids
    assert "nfton-benign" in case_ids
    assert "nfton-attack" in case_ids
    for c in data:
        assert "features" in c
        assert "ground_truth_label" in c
        assert c["ground_truth_label"] in (0, 1)


def test_samples_endpoint():
    response = client.get("/api/v1/data/samples")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    for s in data:
        assert "features" in s
        assert "ground_truth_label" in s

