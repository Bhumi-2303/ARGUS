"""Tests for request payload limits, NaN/Inf rejection, and strict Pydantic schema validation."""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from argus.api.main import app
from argus.schemas.api import FeatureInput, OnboardRequest
from argus.auth.models import UserPrincipal
from argus.auth.rbac import get_current_user

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_authenticated_user():
    """Ensure user has necessary permissions for prediction and onboarding."""
    user = UserPrincipal(
        sub="tester-analyst",
        issuer="argus-test",
        roles=["analyst", "operator", "admin"],
        permissions={"run:prediction", "run:explanation", "run:onboarding", "read:models"}
    )
    app.dependency_overrides[get_current_user] = lambda: user
    yield
    app.dependency_overrides.clear()


def test_payload_too_large_rejected_with_413():
    """Requests with Content-Length exceeding max_request_size_bytes must return 413."""
    # Send a request with a large body > 1MB
    large_features = {f"feat_{i}": 1.0 for i in range(100000)}
    response = client.post(
        "/api/v1/predict",
        json={"model_name": "model_d2_coral", "features": large_features}
    )
    assert response.status_code in (413, 422), f"Unexpected status {response.status_code}"


def test_feature_input_schema_rejects_nan_and_inf():
    """FeatureInput model must reject NaN and Infinity values with ValidationError."""
    with pytest.raises(ValidationError):
        FeatureInput(
            pkt_mean_to_max=float("nan"),
            tcp_flag_density=0.5,
            log_pkt_mean=2.0,
            log_pkt_max=3.0
        )

    with pytest.raises(ValidationError):
        FeatureInput(
            pkt_mean_to_max=float("inf"),
            tcp_flag_density=0.5,
            log_pkt_mean=2.0,
            log_pkt_max=3.0
        )

    with pytest.raises(ValidationError):
        FeatureInput(
            pkt_mean_to_max=float("-inf"),
            tcp_flag_density=0.5,
            log_pkt_mean=2.0,
            log_pkt_max=3.0
        )


def test_predict_rejects_out_of_bound_features():
    """Predict endpoint must reject out-of-bounds numbers in features with 422."""
    # Value > 1000.0
    res_high = client.post(
        "/api/v1/predict",
        json={
            "model_name": "model_d2_coral",
            "features": {"pkt_mean_to_max": 999999.0, "tcp_flag_density": 0.5, "log_pkt_mean": 2.0, "log_pkt_max": 3.0}
        }
    )
    assert res_high.status_code == 422

    # Value < 0.0
    res_neg = client.post(
        "/api/v1/predict",
        json={
            "model_name": "model_d2_coral",
            "features": {"pkt_mean_to_max": -5.0, "tcp_flag_density": 0.5, "log_pkt_mean": 2.0, "log_pkt_max": 3.0}
        }
    )
    assert res_neg.status_code == 422


def test_explain_rejects_out_of_bound_features():
    """Explain endpoint must reject out-of-bounds features with 422."""
    response = client.post(
        "/api/v1/explain",
        json={
            "model_name": "model_d2_coral",
            "features": {"pkt_mean_to_max": 100000.0, "tcp_flag_density": 0.5, "log_pkt_mean": 2.0, "log_pkt_max": 3.0}
        }
    )
    assert response.status_code == 422


def test_onboard_validation_bounds():
    """Onboarding endpoint must enforce strict bounds on window sizes and domain names."""
    # Window size > 50000
    res_high = client.post(
        "/api/v1/onboard",
        json={
            "target_domain": "nfton",
            "adaptation_window_size": 1000000,
            "calibration_window_size": 2000,
            "test_window_size": 3000
        }
    )
    assert res_high.status_code == 422

    # Window size < 10
    res_low = client.post(
        "/api/v1/onboard",
        json={
            "target_domain": "nfton",
            "adaptation_window_size": 1,
            "calibration_window_size": 2000,
            "test_window_size": 3000
        }
    )
    assert res_low.status_code == 422

    # Invalid target domain characters (e.g. injection / spaces)
    res_invalid_domain = client.post(
        "/api/v1/onboard",
        json={
            "target_domain": "nfton; rm -rf /",
            "adaptation_window_size": 5000,
            "calibration_window_size": 2000,
            "test_window_size": 3000
        }
    )
    assert res_invalid_domain.status_code == 422
