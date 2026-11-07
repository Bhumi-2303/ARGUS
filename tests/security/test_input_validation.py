"""Hypothesis-based property and fuzz testing for ARGUS input validation and quarantine engine."""

import math
import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings, HealthCheck, strategies as st

from argus.security.validation import (
    HarmonizedFlowInput,
    TelemetryValidator,
    ValidationConfig,
    ValidationStatus,
    SecurityDecision,
    AlertTier,
    BatchSizeExceededError,
    PayloadSizeExceededError,
    sanitize_inference_output,
)


# Strategy for generating malicious, edge-case, or non-finite floating-point numbers
fuzz_floats = st.one_of(
    st.floats(allow_nan=True, allow_infinity=True),
    st.sampled_from([float("nan"), float("inf"), float("-inf"), 0.0, -0.0, 1.0, -1.0]),
    st.floats(min_value=-1e10, max_value=-1e-5),  # strictly negative
    st.floats(min_value=1e5, max_value=1e30),  # huge out-of-bounds
)

# Strategy for valid bounded harmonized features
valid_harmonized_strategy = st.fixed_dictionaries(
    {
        "pkt_mean_to_max": st.floats(
            min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
        ),
        "tcp_flag_density": st.floats(
            min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False
        ),
        "log_pkt_mean": st.floats(
            min_value=0.0, max_value=6.0, allow_nan=False, allow_infinity=False
        ),
        "log_pkt_max": st.floats(
            min_value=6.0, max_value=12.0, allow_nan=False, allow_infinity=False
        ),
    }
)


class TestPydanticSchemaValidation:
    """Verifies strict Pydantic parsing of single flow records."""

    def test_valid_record_passes(self):
        flow = HarmonizedFlowInput(
            pkt_mean_to_max=0.85,
            tcp_flag_density=2.0,
            log_pkt_mean=4.2,
            log_pkt_max=5.5,
        )
        assert flow.pkt_mean_to_max == 0.85

    @pytest.mark.parametrize(
        "kwargs",
        [
            {
                "pkt_mean_to_max": 1.5,
                "tcp_flag_density": 0,
                "log_pkt_mean": 2,
                "log_pkt_max": 3,
            },  # ratio > 1.0
            {
                "pkt_mean_to_max": -0.1,
                "tcp_flag_density": 0,
                "log_pkt_mean": 2,
                "log_pkt_max": 3,
            },  # negative ratio
            {
                "pkt_mean_to_max": float("nan"),
                "tcp_flag_density": 0,
                "log_pkt_mean": 2,
                "log_pkt_max": 3,
            },
            {
                "pkt_mean_to_max": float("inf"),
                "tcp_flag_density": 0,
                "log_pkt_mean": 2,
                "log_pkt_max": 3,
            },
            {
                "pkt_mean_to_max": 0.5,
                "tcp_flag_density": 15.0,
                "log_pkt_mean": 2,
                "log_pkt_max": 3,
            },  # flag > 10.0
            {
                "pkt_mean_to_max": 0.5,
                "tcp_flag_density": 1.0,
                "log_pkt_mean": 5.0,
                "log_pkt_max": 3.0,
            },  # mean > max
        ],
    )
    def test_invalid_records_raise_validation_error(self, kwargs):
        with pytest.raises(Exception):
            HarmonizedFlowInput(**kwargs)


class TestBatchValidationFuzzing:
    """Fuzz testing with Hypothesis to ensure no exceptions escape and invalid rows fail closed."""

    @given(
        pkt_mean_to_max=fuzz_floats,
        tcp_flag_density=fuzz_floats,
        log_pkt_mean=fuzz_floats,
        log_pkt_max=fuzz_floats,
    )
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_harmonized_features(
        self,
        pkt_mean_to_max: float,
        tcp_flag_density: float,
        log_pkt_mean: float,
        log_pkt_max: float,
    ):
        validator = TelemetryValidator()
        df = pd.DataFrame(
            [
                {
                    "pkt_mean_to_max": pkt_mean_to_max,
                    "tcp_flag_density": tcp_flag_density,
                    "log_pkt_mean": log_pkt_mean,
                    "log_pkt_max": log_pkt_max,
                }
            ]
        )

        # Invariant 1: No unhandled exception must escape
        result = validator.validate_and_sanitize_harmonized(df)

        # Invariant 2: Output clean_features must NEVER contain NaN or Inf
        assert not result.clean_features.isna().any().any()
        assert not np.isinf(result.clean_features.to_numpy()).any()

        # Invariant 3: If input had any invalid attribute, row MUST be quarantined
        is_nan_inf = any(
            math.isnan(v) or math.isinf(v)
            for v in [pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max]
        )
        is_negative = any(
            v < 0
            for v in [pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max]
            if not math.isnan(v)
        )
        is_out_of_bounds = (
            (pkt_mean_to_max > 1.0)
            or (tcp_flag_density > 10.0)
            or (log_pkt_mean > 12.0)
            or (log_pkt_max > 12.0)
        )
        is_invariant_breached = (
            (not math.isnan(log_pkt_mean))
            and (not math.isnan(log_pkt_max))
            and (log_pkt_mean > log_pkt_max + 1e-6)
        )

        if is_nan_inf or is_negative or is_out_of_bounds or is_invariant_breached:
            assert result.quarantine_mask[0] is True or result.quarantine_mask[0] == 1
            assert (
                result.validation_status.iloc[0] == ValidationStatus.INVALID_FLAG_FOR_REVIEW.value
            )

            # Invariant 4: Fail Closed — never classify invalid row as Benign
            sanitized = sanitize_inference_output(
                event_id="test-fuzz",
                model_name="xgb_adapted",
                raw_probability=0.1,  # even if model would score benign
                threshold=0.5,
                is_valid=False,
                quarantine_reason=result.rejection_reasons[0],
            )
            assert sanitized.decision != SecurityDecision.BENIGN
            assert sanitized.decision == SecurityDecision.QUARANTINE
            assert sanitized.status == ValidationStatus.INVALID_FLAG_FOR_REVIEW

    @given(
        pkt_len_mean=fuzz_floats,
        pkt_len_max=fuzz_floats,
        duration=fuzz_floats,
        header_len=fuzz_floats,
    )
    @settings(max_examples=150, suppress_health_check=[HealthCheck.too_slow])
    def test_fuzz_raw_telemetry_extraction(
        self,
        pkt_len_mean: float,
        pkt_len_max: float,
        duration: float,
        header_len: float,
    ):
        validator = TelemetryValidator()
        df = pd.DataFrame(
            [
                {
                    "Pkt Len Mean": pkt_len_mean,
                    "Pkt Len Max": pkt_len_max,
                    "Duration": duration,
                    "Header_Length": header_len,
                    "SYN Flag Cnt": 1,
                }
            ]
        )

        result = validator.extract_and_validate_from_raw(df)

        # Output sanitized features must be purely finite
        assert not result.clean_features.isna().any().any()
        assert not np.isinf(result.clean_features.to_numpy()).any()

        # Zero division case: max_len == 0 or negative
        if pkt_len_max <= 0 or math.isnan(pkt_len_max) or math.isinf(pkt_len_max):
            assert bool(result.quarantine_mask[0]) is True
            assert (
                result.validation_status.iloc[0] == ValidationStatus.INVALID_FLAG_FOR_REVIEW.value
            )


class TestSecurityCapacityAndPolicy:
    """Verifies batch limits, payload sizes, and probability masking."""

    def test_exceeding_batch_size_raises(self):
        config = ValidationConfig()
        config.max_batch_size = 5
        validator = TelemetryValidator(config=config)
        large_df = pd.DataFrame(
            {
                "pkt_mean_to_max": [0.5] * 10,
                "tcp_flag_density": [1.0] * 10,
                "log_pkt_mean": [3.0] * 10,
                "log_pkt_max": [4.0] * 10,
            }
        )
        with pytest.raises(BatchSizeExceededError):
            validator.validate_and_sanitize_harmonized(large_df)

    def test_exceeding_payload_size_raises(self):
        config = ValidationConfig()
        config.max_payload_bytes = 100
        validator = TelemetryValidator(config=config)
        huge_bytes = b"X" * 101
        with pytest.raises(PayloadSizeExceededError):
            validator.check_payload_size(huge_bytes)

    def test_raw_probabilities_strictly_masked(self):
        resp = sanitize_inference_output(
            event_id="evt-100",
            model_name="model_d2_coral",
            raw_probability=0.987654321,
            threshold=0.85,
            is_valid=True,
        )
        dump = resp.model_dump()

        # Assert no raw probabilities or scores are exposed externally
        assert "probability" not in dump
        assert "raw_probability" not in dump
        assert "score" not in dump
        assert "logit" not in dump
        assert resp.decision == SecurityDecision.ATTACK
        assert resp.tier == AlertTier.TIER_1_HIGH_CONFIDENCE

    def test_benign_verdict_labeled_unverified(self):
        resp = sanitize_inference_output(
            event_id="evt-200",
            model_name="model_d2_coral",
            raw_probability=0.25,
            threshold=0.85,
            is_valid=True,
        )
        assert resp.decision == SecurityDecision.BENIGN
        # CRITICAL POLICY: benign traffic is labeled 'unverified', never 'safe'
        assert resp.tier == AlertTier.TIER_UNVERIFIED_BENIGN

    def test_missing_columns_fails_closed(self):
        validator = TelemetryValidator()
        incomplete_df = pd.DataFrame({"random_col": [1, 2, 3]})
        result = validator.validate_and_sanitize_harmonized(incomplete_df)

        assert result.quarantine_count == 3
        assert (result.validation_status == ValidationStatus.INVALID_FLAG_FOR_REVIEW.value).all()
