"""Integration tests for all ARGUS API v1 endpoints."""

import os
import pytest
import pandas as pd
from scipy.stats import ks_2samp
from fastapi.testclient import TestClient

from argus.api.main import app
from argus.registry.model_registry import model_registry
from argus.data.manager import HARMONIZED_FEATURES

client = TestClient(app)


def test_get_health():
    """Verify health endpoint and confirmation that all required models are loaded."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models_loaded" in data

    # Verify registered model loading status
    models_status = data["models_loaded"]
    assert models_status.get("model_d2_coral") is True
    assert models_status.get("model_d1_baseline") is True
    assert models_status.get("model_d3_native") is True
    assert models_status.get("xgb_source") is True
    assert models_status.get("xgb_adapted") is True
    assert models_status.get("dann") is False


def test_get_domains():
    """Verify domain metadata endpoint returns correct attack ratios and harmonized features."""
    response = client.get("/api/v1/domains")
    assert response.status_code == 200
    data = response.json()
    assert "domains" in data
    assert len(data["domains"]) >= 3

    domain_map = {d["domain_id"]: d for d in data["domains"]}
    assert "ciciot" in domain_map
    assert "nfton" in domain_map
    assert "iec104" in domain_map

    # Remediation F-10: Verify empirical attack ratio constants reflect true dataset splits
    assert pytest.approx(domain_map["ciciot"]["attack_ratio"], abs=1e-3) == 0.9765
    assert pytest.approx(domain_map["nfton"]["attack_ratio"], abs=1e-3) == 0.7258
    assert pytest.approx(domain_map["iec104"]["attack_ratio"], abs=1e-3) == 0.2247
    for d in domain_map.values():
        assert d["features"] == HARMONIZED_FEATURES


def test_get_models():
    """Verify model metadata endpoint returns correct threshold, protocol_status, and verified status."""
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data

    model_map = {m["name"]: m for m in data["models"]}
    assert "model_d2_coral" in model_map
    assert "xgb_source" in model_map
    assert "dann" in model_map

    # Remediation F-01: Verify Clean CORAL uses the 0.99 threshold and coral_aligned protocol
    coral = model_map["model_d2_coral"]
    assert coral["threshold"] == 0.99
    assert coral["protocol_status"] == "coral_aligned"
    assert coral["status"] == "verified"

    # Verify DANN metadata reports unavailable with null threshold
    dann = model_map["dann"]
    assert dann["threshold"] is None
    assert dann["protocol_status"] == "dann_adapted"
    assert dann["status"] == "unavailable"


def test_predict_endpoint():
    """Verify predict endpoint: model_d2_coral uses tau=0.99; DANN raises 501 Not Implemented."""
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
    assert data["threshold"] == 0.99
    # Decision rule: prediction == 1 iff probability >= threshold
    assert data["prediction"] == (1 if data["probability"] >= 0.99 else 0)

    # Remediation F-13: DANN has no inference checkpoint; MUST raise 501 Not Implemented
    dann_payload = {
        "features": {
            "pkt_mean_to_max": 0.5,
            "tcp_flag_density": 1.0,
            "log_pkt_mean": 4.0,
            "log_pkt_max": 4.5
        },
        "model_name": "dann"
    }
    dann_response = client.post("/api/v1/predict", json=dann_payload)
    assert dann_response.status_code == 501
    assert "no verified checkpoint" in dann_response.json()["detail"].lower()

    # Direct unit assertion that model_registry.predict raises NotImplementedError
    with pytest.raises(NotImplementedError, match="no verified checkpoint"):
        model_registry.predict("dann", dann_payload["features"])


def test_shift_endpoint():
    """Verify distribution shift endpoint matches independent scipy.stats.ks_2samp recomputation."""
    # 1. Test D2 (NF-ToN) shift dynamically computed from samples
    response = client.get("/api/v1/shift?domain=nfton&window_size=100")
    assert response.status_code == 200
    data = response.json()
    assert data["target_domain"] == "nfton"
    assert "domain_shift" in data
    assert len(data["feature_shifts"]) == 4

    # Remediation F-06: Independent scipy recomputation on exact sample window
    df_src = pd.read_parquet("data/samples/ciciot.parquet").head(100)
    df_tgt = pd.read_parquet("data/samples/nfton.parquet").head(100)

    for f_metric in data["feature_shifts"]:
        col = f_metric["feature"]
        assert col in HARMONIZED_FEATURES
        expected_ks = ks_2samp(df_src[col].to_numpy(), df_tgt[col].to_numpy())
        assert pytest.approx(round(float(expected_ks.statistic), 4), abs=1e-4) == f_metric["ks_statistic"]
        assert pytest.approx(round(float(expected_ks.pvalue), 6), abs=1e-4) == f_metric["ks_pvalue"]
        assert f_metric["shift_detected"] is True

    # 2. Test D3 (IEC104) shift loaded from verified domain_shift_statistics.csv
    resp_d3 = client.get("/api/v1/shift?domain=iec104")
    assert resp_d3.status_code == 200
    data_d3 = resp_d3.json()
    assert data_d3["target_domain"] == "iec104"
    assert len(data_d3["feature_shifts"]) == 4
    # Check that D1->D3 KS stats match verified domain_shift_statistics.csv
    d3_map = {f["feature"]: f for f in data_d3["feature_shifts"]}
    assert pytest.approx(d3_map["pkt_mean_to_max"]["ks_statistic"], abs=1e-4) == 0.1475
    assert pytest.approx(d3_map["tcp_flag_density"]["ks_statistic"], abs=1e-4) == 0.3490
    assert pytest.approx(d3_map["log_pkt_mean"]["ks_statistic"], abs=1e-4) == 0.8341
    assert pytest.approx(d3_map["log_pkt_max"]["ks_statistic"], abs=1e-4) == 0.8340


def test_explain_endpoint():
    """Verify SHAP explainability endpoint returns genuine TreeExplainer feature attributions."""
    with TestClient(app) as test_client:
        payload = {
            "features": {
                "pkt_mean_to_max": 0.5,
                "tcp_flag_density": 1.0,
                "log_pkt_mean": 4.0,
                "log_pkt_max": 4.5
            },
            "model_name": "model_d2_coral"
        }
        response = test_client.post("/api/v1/explain", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "base_value" in data
        assert isinstance(data["base_value"], (int, float))
        assert "shap_values" in data

        # Remediation F-07: Verify real TreeExplainer SHAP values exist for all 4 harmonized features
        assert set(data["shap_values"].keys()) == set(HARMONIZED_FEATURES)
        for feat in HARMONIZED_FEATURES:
            assert isinstance(data["shap_values"][feat], (int, float))
            # Attributions must be real non-zero floats
            assert data["shap_values"][feat] != 0.0

        assert data["top_feature"] in HARMONIZED_FEATURES
        assert pytest.approx(data["top_feature_impact"], abs=1e-5) == data["shap_values"][data["top_feature"]]


def test_test_cases_endpoint():
    """Verify test-cases endpoint returns verified exemplar flows with exact feature coordinates."""
    response = client.get("/api/v1/data/test-cases")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    case_map = {c["id"]: c for c in data}

    assert "ciciot-benign" in case_map
    assert "ciciot-attack" in case_map
    assert "nfton-benign" in case_map
    assert "nfton-attack" in case_map

    # Check verified feature values extracted directly from source/target test sets
    ciciot_benign = case_map["ciciot-benign"]
    assert ciciot_benign["ground_truth_label"] == 0
    assert pytest.approx(ciciot_benign["features"]["pkt_mean_to_max"], abs=1e-5) == 0.149459

    ciciot_attack = case_map["ciciot-attack"]
    assert ciciot_attack["ground_truth_label"] == 1
    assert pytest.approx(ciciot_attack["features"]["pkt_mean_to_max"], abs=1e-5) == 0.997206

    nfton_benign = case_map["nfton-benign"]
    assert nfton_benign["ground_truth_label"] == 0
    assert pytest.approx(nfton_benign["features"]["pkt_mean_to_max"], abs=1e-5) == 0.904762
    assert pytest.approx(nfton_benign["features"]["tcp_flag_density"], abs=1e-5) == 3.0

    nfton_attack = case_map["nfton-attack"]
    assert nfton_attack["ground_truth_label"] == 1
    assert pytest.approx(nfton_attack["features"]["pkt_mean_to_max"], abs=1e-5) == 1.0
    assert pytest.approx(nfton_attack["features"]["tcp_flag_density"], abs=1e-5) == 1.0
    assert pytest.approx(nfton_attack["features"]["log_pkt_mean"], abs=1e-5) == 3.970292
    assert pytest.approx(nfton_attack["features"]["log_pkt_max"], abs=1e-5) == 3.970292


def test_samples_endpoint():
    """Verify samples endpoint returns genuine stratified flow samples from disk parquets."""
    response = client.get("/api/v1/data/samples")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Remediation F-12: Verify real sample features are within valid operational domain boundaries
    for s in data:
        assert "features" in s
        assert "ground_truth_label" in s
        feats = s["features"]
        assert set(feats.keys()) == set(HARMONIZED_FEATURES)
        assert 0.0 <= feats["pkt_mean_to_max"] <= 1.0
        assert feats["tcp_flag_density"] >= 0.0
        assert feats["log_pkt_mean"] > 0.0
        assert feats["log_pkt_max"] >= feats["log_pkt_mean"]
