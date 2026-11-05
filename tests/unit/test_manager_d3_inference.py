"""Regression tests for manager-level D3 inference and error propagation.

Verifies:
- data_manager.simulate_onboard() with model_d3_native requires all 73 native features.
- Missing features raise explicit ValueError rather than silently appending zero.
- Non-finite numbers (NaN/Inf) raise explicit ValueError rather than silently appending zero.
- Complete 73-feature datasets evaluate correctly on model_d3_native.
- Default nfton evaluation on model_d2_coral continues functioning.
- End-to-end /api/v1/onboard endpoint handles validation errors cleanly with HTTP 400.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch
from pathlib import Path
from httpx import AsyncClient, ASGITransport

from argus.data.manager import data_manager
from argus.registry.model_registry import D3_NATIVE_FEATURES, HARMONIZED_FEATURES
from argus.api.main import app
from tests.security.test_adversarial_verification import create_token, valid_rsa_key


@pytest.fixture
def sample_73_df():
    """Create a DataFrame with all 73 native D3 features and ground-truth labels."""
    rows = []
    for i in range(25):
        row = {feat: float((i + 1) * 0.05) for feat in D3_NATIVE_FEATURES}
        row["label"] = 1 if i % 2 == 0 else 0
        rows.append(row)
    return pd.DataFrame(rows)


@pytest.fixture
def sample_4_df():
    """Create a DataFrame with only the 4 harmonized features and labels."""
    rows = []
    for i in range(25):
        row = {feat: float((i + 1) * 0.1) for feat in HARMONIZED_FEATURES}
        row["label"] = 1 if i % 2 == 0 else 0
        rows.append(row)
    return pd.DataFrame(rows)


def test_manager_d3_with_73_features_succeeds(sample_73_df):
    """Manager-level inference on model_d3_native succeeds when all 73 features are present."""
    with patch("pandas.read_parquet", return_value=sample_73_df), \
         patch.object(Path, "exists", return_value=True):
        res = data_manager.simulate_onboard(target_domain="iec104", test_size=20)
        assert res["target_domain"] == "iec104"
        assert res["selected_threshold"] == 0.50
        assert "metrics" in res
        metrics = res["metrics"]
        assert "accuracy" in metrics
        assert "f1_score" in metrics
        assert "mcc" in metrics
        assert isinstance(metrics["accuracy"], float)


def test_manager_d3_missing_features_raises_explicit_value_error(sample_4_df):
    """Manager-level inference on model_d3_native with missing features raises ValueError.

    Crucially, it does NOT swallow the error and convert all predictions into zero.
    """
    with patch("pandas.read_parquet", return_value=sample_4_df), \
         patch.object(Path, "exists", return_value=True):
        with pytest.raises(ValueError) as excinfo:
            data_manager.simulate_onboard(target_domain="iec104", test_size=20)
        err = str(excinfo.value)
        assert "model_d3_native" in err
        assert "missing" in err.lower()
        assert "required feature" in err.lower()


def test_manager_d3_nan_values_raise_explicit_value_error(sample_73_df):
    """Manager-level inference on model_d3_native with NaN values raises ValueError."""
    corrupted_df = sample_73_df.copy()
    corrupted_df.loc[0, "Flow_Duration"] = np.nan

    with patch("pandas.read_parquet", return_value=corrupted_df), \
         patch.object(Path, "exists", return_value=True):
        with pytest.raises(ValueError) as excinfo:
            data_manager.simulate_onboard(target_domain="iec104", test_size=20)
        err = str(excinfo.value)
        assert "invalid non-finite value" in err.lower()
        assert "nan" in err.lower()


def test_manager_nfton_coral_succeeds():
    """Manager-level inference for nfton using model_d2_coral succeeds with real sample data."""
    res = data_manager.simulate_onboard(target_domain="nfton", test_size=30)
    assert res["target_domain"] == "nfton"
    assert res["selected_threshold"] == 0.99
    assert res["coral_fitted"] is True
    assert "metrics" in res
    assert res["evaluated_test_size"] >= 10


@pytest.mark.asyncio
async def test_api_onboard_propagates_missing_features_as_http_400(sample_4_df):
    """End-to-end: API /api/v1/onboard with missing features returns HTTP 400 Bad Request."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with patch("pandas.read_parquet", return_value=sample_4_df), \
             patch.object(Path, "exists", return_value=True):
            payload = {
                "target_domain": "iec104",
                "adaptation_window_size": 100,
                "calibration_window_size": 50,
                "test_window_size": 25,
            }
            res = await client.post("/api/v1/onboard", json=payload)
            assert res.status_code == 400, f"Expected 400, got {res.status_code}: {res.text}"
            data = res.json()
            assert "detail" in data
            assert "missing" in data["detail"].lower()
            assert "model_d3_native" in data["detail"]
