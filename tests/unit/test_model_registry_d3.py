"""Unit and integration tests for P0-1: D3 native model feature schema validation.

Verifies:
- Native D3 model inference receives exact 73-feature schema.
- Input validation rejects missing features, dimension mismatches, unexpected extra features, and non-finite values.
- Existing 4-feature models remain fully functional.
- End-to-end API integration through /api/v1/predict with RBAC.
"""

import pytest
import numpy as np
from httpx import AsyncClient, ASGITransport

from argus.registry.model_registry import (
    ModelRegistry,
    HARMONIZED_FEATURES,
    D3_NATIVE_FEATURES,
    model_registry,
)
from argus.api.main import app
from tests.security.test_adversarial_verification import create_token, valid_rsa_key


@pytest.fixture(scope="module")
def registry():
    """Ensure registry is initialized with loaded models."""
    reg = ModelRegistry(".")
    reg.load_all()
    return reg


@pytest.fixture
def valid_d3_features():
    """Construct a valid 73-feature input dictionary for model_d3_native."""
    return {feat: 0.5 for feat in D3_NATIVE_FEATURES}


@pytest.fixture
def valid_4_features():
    """Construct a valid 4-feature harmonized input dictionary."""
    return {
        "pkt_mean_to_max": 0.5,
        "tcp_flag_density": 1.0,
        "log_pkt_mean": 4.0,
        "log_pkt_max": 4.5,
    }


# ===========================================================================
# 1. VALID INPUT TESTS
# ===========================================================================

def test_valid_native_d3_input_succeeds(registry, valid_d3_features):
    """Native D3 prediction succeeds with all 73 features."""
    prob, label, threshold = registry.predict("model_d3_native", valid_d3_features)
    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0
    assert label in (0, 1)
    assert threshold == 0.50
    assert label == (1 if prob >= threshold else 0)


def test_d3_features_with_spaces_normalized(registry, valid_d3_features):
    """Input dictionary using spaces instead of underscores aligns correctly."""
    spaced_features = {k.replace("_", " "): v for k, v in valid_d3_features.items()}
    prob, label, threshold = registry.predict("model_d3_native", spaced_features)
    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0


def test_d3_feature_ordering_invariance(registry, valid_d3_features):
    """Dictionary insertion order does not affect schema alignment or predictions."""
    reversed_features = {k: valid_d3_features[k] for k in reversed(list(valid_d3_features.keys()))}
    prob_rev, label_rev, _ = registry.predict("model_d3_native", reversed_features)
    prob_orig, label_orig, _ = registry.predict("model_d3_native", valid_d3_features)
    assert prob_rev == pytest.approx(prob_orig, abs=1e-6)
    assert label_rev == label_orig


# ===========================================================================
# 2. FEATURE MISMATCH & REJECTION TESTS
# ===========================================================================

def test_native_d3_input_with_four_features_rejected(registry, valid_4_features):
    """Passing 4 harmonized features to model_d3_native raises clear ValueError."""
    with pytest.raises(ValueError) as excinfo:
        registry.predict("model_d3_native", valid_4_features)
    err = str(excinfo.value)
    assert "model_d3_native" in err
    assert "requires 73 features" in err
    assert "missing" in err.lower()


def test_native_d3_input_with_72_features_rejected(registry, valid_d3_features):
    """Omitting even a single feature (72/73) raises clear validation error."""
    missing_key = D3_NATIVE_FEATURES[-1]
    features_72 = {k: v for k, v in valid_d3_features.items() if k != missing_key}
    with pytest.raises(ValueError) as excinfo:
        registry.predict("model_d3_native", features_72)
    err = str(excinfo.value)
    assert "model_d3_native" in err
    assert missing_key in err


def test_native_d3_missing_specific_feature_named(registry, valid_d3_features):
    """Error message explicitly names missing features."""
    features_missing = dict(valid_d3_features)
    del features_missing["Flow_Duration"]
    del features_missing["Tot_Fwd_Pkts"]
    with pytest.raises(ValueError) as excinfo:
        registry.predict("model_d3_native", features_missing)
    err = str(excinfo.value)
    assert "Flow_Duration" in err
    assert "Tot_Fwd_Pkts" in err


def test_unexpected_extra_features_rejected(registry, valid_d3_features):
    """Unexpected extra features are explicitly rejected to prevent schema corruption."""
    extra_features = dict(valid_d3_features)
    extra_features["unauthorized_column"] = 123.45
    with pytest.raises(ValueError) as excinfo:
        registry.predict("model_d3_native", extra_features)
    err = str(excinfo.value)
    assert "unexpected feature" in err.lower()
    assert "unauthorized_column" in err


# ===========================================================================
# 3. NON-FINITE VALUE TESTS (NaN / INF)
# ===========================================================================

def test_native_d3_rejects_nan(registry, valid_d3_features):
    """NaN value in any feature raises ValueError."""
    nan_features = dict(valid_d3_features)
    nan_features["Flow_Duration"] = float("nan")
    with pytest.raises(ValueError) as excinfo:
        registry.predict("model_d3_native", nan_features)
    assert "invalid non-finite value" in str(excinfo.value)


def test_native_d3_rejects_positive_inf(registry, valid_d3_features):
    """Positive infinity in any feature raises ValueError."""
    inf_features = dict(valid_d3_features)
    inf_features["Flow_Byts/s"] = float("inf")
    with pytest.raises(ValueError) as excinfo:
        registry.predict("model_d3_native", inf_features)
    assert "invalid non-finite value" in str(excinfo.value)


def test_native_d3_rejects_negative_inf(registry, valid_d3_features):
    """Negative infinity in any feature raises ValueError."""
    ninf_features = dict(valid_d3_features)
    ninf_features["log_pkt_mean"] = float("-inf")
    with pytest.raises(ValueError) as excinfo:
        registry.predict("model_d3_native", ninf_features)
    assert "invalid non-finite value" in str(excinfo.value)


# ===========================================================================
# 4. BACKWARD COMPATIBILITY: EXISTING 4-FEATURE MODELS
# ===========================================================================

@pytest.mark.parametrize("model_name,expected_tau", [
    ("model_d1_baseline", 0.50),
    ("model_d2_coral", 0.99),
    ("xgb_source", 0.50),
    ("xgb_adapted", 0.99),
])
def test_existing_four_feature_models_remain_functional(registry, valid_4_features, model_name, expected_tau):
    """All 4-feature models continue predicting normally with 4 harmonized features."""
    prob, label, threshold = registry.predict(model_name, valid_4_features)
    assert isinstance(prob, float)
    assert 0.0 <= prob <= 1.0
    assert threshold == expected_tau
    assert label == (1 if prob >= threshold else 0)


def test_four_feature_models_reject_73_features(registry, valid_d3_features):
    """4-feature models reject unexpected 73-feature dictionaries."""
    with pytest.raises(ValueError) as excinfo:
        registry.predict("model_d2_coral", valid_d3_features)
    assert "unexpected feature" in str(excinfo.value).lower()


def test_unavailable_model_dann_raises_not_implemented(registry, valid_4_features):
    """Requesting unverified model 'dann' raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        registry.predict("dann", valid_4_features)


# ===========================================================================
# 5. BATCH PREDICTION TESTS
# ===========================================================================

def test_predict_batch_native_d3_succeeds(registry):
    """Batch prediction on (N, 73) matrix succeeds for model_d3_native."""
    batch_73 = np.ones((5, 73), dtype=np.float32) * 0.2
    preds = registry.predict_batch("model_d3_native", batch_73)
    assert isinstance(preds, np.ndarray)
    assert len(preds) == 5
    assert all(0.0 <= p <= 1.0 for p in preds)


def test_predict_batch_dimension_mismatch_rejected(registry):
    """Batch prediction with wrong column count raises clear ValueError."""
    batch_4 = np.ones((5, 4), dtype=np.float32)
    with pytest.raises(ValueError) as excinfo:
        registry.predict_batch("model_d3_native", batch_4)
    assert "expects 73 features" in str(excinfo.value)

    batch_73 = np.ones((5, 73), dtype=np.float32)
    with pytest.raises(ValueError) as excinfo:
        registry.predict_batch("model_d2_coral", batch_73)
    assert "expects 4 features" in str(excinfo.value)


# ===========================================================================
# 6. SHAP EXPLAINABILITY TESTS
# ===========================================================================

def test_explain_native_d3_generates_all_73_attributions(registry, valid_d3_features):
    """TreeExplainer on model_d3_native returns all 73 feature SHAP values."""
    base_val, shap_dict, top_feat, top_impact = registry.explain("model_d3_native", valid_d3_features)
    assert isinstance(base_val, float)
    assert len(shap_dict) == 73
    assert top_feat in D3_NATIVE_FEATURES
    assert isinstance(top_impact, float)
    assert shap_dict[top_feat] == top_impact


# ===========================================================================
# 7. END-TO-END API INTEGRATION TESTS
# ===========================================================================

@pytest.mark.asyncio
async def test_api_predict_native_d3_with_73_features_succeeds(valid_d3_features):
    """End-to-end HTTP request: /api/v1/predict with 73 features succeeds for model_d3_native."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "model_name": "model_d3_native",
            "features": valid_d3_features,
        }
        res = await client.post(
            "/api/v1/predict",
            json=payload,
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["model_name"] == "model_d3_native"
        assert "probability" in data
        assert "prediction" in data
        assert data["threshold"] == 0.50


@pytest.mark.asyncio
async def test_api_predict_native_d3_with_four_features_returns_400(valid_4_features):
    """End-to-end HTTP request: /api/v1/predict with 4 features fails with 400 for model_d3_native."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "model_name": "model_d3_native",
            "features": valid_4_features,
        }
        res = await client.post(
            "/api/v1/predict",
            json=payload,
        )
        assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
        data = res.json()
        assert "detail" in data
        assert "model_d3_native" in data["detail"]
        assert "requires 73 features" in data["detail"]
