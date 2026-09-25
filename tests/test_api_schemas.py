"""Unit tests for ARGUS API Pydantic schemas."""

import pytest
from pydantic import ValidationError
from argus.schemas.api import (
    FeatureInput, PredictRequest, PredictResponse,
    HealthResponse, DomainsResponse, ModelsResponse,
    ResultTableResponse, ShiftResponse, ExplainResponse, OnboardResponse
)


def test_feature_input_schema():
    feat = FeatureInput(
        pkt_mean_to_max=0.5,
        tcp_flag_density=1.0,
        log_pkt_mean=4.0,
        log_pkt_max=4.5
    )
    assert feat.pkt_mean_to_max == 0.5
    assert feat.tcp_flag_density == 1.0


def test_predict_request_schema_validation():
    req = PredictRequest(
        features=FeatureInput(
            pkt_mean_to_max=0.8,
            tcp_flag_density=0.0,
            log_pkt_mean=3.5,
            log_pkt_max=3.8
        ),
        model_name="model_d2_coral"
    )
    assert req.model_name == "model_d2_coral"
    assert req.features.log_pkt_mean == 3.5

    # Invalid feature type
    with pytest.raises(ValidationError):
        PredictRequest(
            features={
                "pkt_mean_to_max": "invalid_float",
                "tcp_flag_density": 0.0,
                "log_pkt_mean": 3.5,
                "log_pkt_max": 3.8
            }
        )


def test_onboard_response_demo_scale_flag():
    resp = OnboardResponse(
        target_domain="nfton",
        demo_scale=True,
        coral_fitted=True,
        selected_threshold=0.99,
        metrics={"accuracy": 0.95, "f1_score": 0.94, "mcc": 0.91, "fpr": 0.02, "fnr": 0.03},
        evaluated_test_size=3000
    )
    assert resp.demo_scale is True
    assert resp.metrics["f1_score"] == 0.94
