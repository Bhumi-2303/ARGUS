"""ARGUS Security Input Validation and Sanitization Module.

Enforces strict input validation, numerical safety, feature bounding,
batch capping, payload limits, and fail-closed quarantine policies.
External callers receive only high-level decision and risk tiers, never raw model probabilities.
"""

from dataclasses import dataclass
from enum import Enum
import math
from pathlib import Path
from typing import Any, List, Optional, Union
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator
import structlog
import yaml

logger = structlog.get_logger("argus.security.validation")

# Default Bounds Configuration Path
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "feature_bounds.yaml"


class ValidationStatus(str, Enum):
    """Row-level validation and quarantine status codes."""

    VALID = "VALID"
    INVALID_FLAG_FOR_REVIEW = "INVALID_FLAG_FOR_REVIEW"


class SecurityDecision(str, Enum):
    """External security classification verdicts (fail-closed)."""

    BENIGN = "BENIGN"
    ATTACK = "ATTACK"
    QUARANTINE = "QUARANTINE"


class AlertTier(str, Enum):
    """Operational alert tiers hiding internal floating-point model scores."""

    TIER_1_HIGH_CONFIDENCE = "TIER_1_HIGH_CONFIDENCE"
    TIER_2_SUSPICIOUS = "TIER_2_SUSPICIOUS"
    TIER_UNVERIFIED_BENIGN = "TIER_UNVERIFIED_BENIGN"
    TIER_REVIEW = "TIER_REVIEW"


class ValidationException(Exception):
    """Base exception for security input validation failures."""


class BatchSizeExceededError(ValidationException):
    """Raised when submitted batch exceeds configured capacity."""


class PayloadSizeExceededError(ValidationException):
    """Raised when request byte payload exceeds security threshold."""


@dataclass(frozen=True)
class FeatureBound:
    """Defines plausible mathematical and physical bounds for a single metric."""

    min_val: float
    max_val: float
    dtype: str = "float64"
    allow_null: bool = False
    description: str = ""


class ValidationConfig:
    """Loads and caches versioned feature bounds and capacity limits."""

    _instance: Optional["ValidationConfig"] = None

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
        if not path.exists():
            # Robust fallback defaults if config file is not yet deployed
            self.version = "1.0.0-fallback"
            self.max_batch_size = 50000
            self.max_payload_bytes = 1048576  # 1 MB
            self.harmonized_bounds = {
                "pkt_mean_to_max": FeatureBound(0.0, 1.0, description="Mean-to-max packet ratio"),
                "tcp_flag_density": FeatureBound(
                    0.0, 10.0, description="TCP control flags density"
                ),
                "log_pkt_mean": FeatureBound(0.0, 12.0, description="Log packet length mean (+1)"),
                "log_pkt_max": FeatureBound(0.0, 12.0, description="Log packet length max (+1)"),
            }
            self.raw_bounds = {
                "Pkt Len Mean": FeatureBound(0.0, 65535.0),
                "Pkt Len Max": FeatureBound(0.0, 65535.0),
                "Duration": FeatureBound(0.0, 86400.0),
                "Header_Length": FeatureBound(0.0, 65535.0),
                "Rate": FeatureBound(0.0, 1e9),
                "Size": FeatureBound(0.0, 1e9),
            }
            return

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.version = str(data.get("version", "1.0.0"))
        limits = data.get("limits", {})
        self.max_batch_size = int(limits.get("max_batch_size", 50000))
        self.max_payload_bytes = int(limits.get("max_payload_bytes", 1048576))

        self.harmonized_bounds = {}
        for feat, spec in data.get("harmonized_features", {}).items():
            self.harmonized_bounds[feat] = FeatureBound(
                min_val=float(spec.get("min", 0.0)),
                max_val=float(spec.get("max", 1.0)),
                dtype=str(spec.get("dtype", "float64")),
                allow_null=bool(spec.get("allow_null", False)),
                description=str(spec.get("description", "")),
            )

        self.raw_bounds = {}
        for feat, spec in data.get("raw_inputs", {}).items():
            self.raw_bounds[feat] = FeatureBound(
                min_val=float(spec.get("min", 0.0)),
                max_val=float(spec.get("max", 1e9)),
                dtype=str(spec.get("dtype", "float64")),
                allow_null=bool(spec.get("allow_null", False)),
                description=str(spec.get("description", "")),
            )

    @classmethod
    def get_default(cls) -> "ValidationConfig":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# ==============================================================================
# 1. Pydantic Strict Schemas for Single Flow Records
# ==============================================================================


class HarmonizedFlowInput(BaseModel):
    """Strict schema for the canonical 4 harmonized statistical features."""

    pkt_mean_to_max: float = Field(
        ...,
        ge=0.0,
        le=1.0 + 1e-9,
        allow_inf_nan=False,
        description="Ratio of packet mean to max length [0.0, 1.0]",
    )
    tcp_flag_density: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        allow_inf_nan=False,
        description="TCP flag count density [0.0, 10.0]",
    )
    log_pkt_mean: float = Field(
        ...,
        ge=0.0,
        le=12.0,
        allow_inf_nan=False,
        description="Natural log of packet length mean (+1) [0.0, 12.0]",
    )
    log_pkt_max: float = Field(
        ...,
        ge=0.0,
        le=12.0,
        allow_inf_nan=False,
        description="Natural log of packet length max (+1) [0.0, 12.0]",
    )

    @field_validator("log_pkt_max")
    @classmethod
    def validate_log_mean_less_than_max(cls, v: float, info: Any) -> float:
        """Inherent network invariant: mean packet length cannot exceed maximum packet length."""
        mean_val = info.data.get("log_pkt_mean")
        if mean_val is not None and v < (mean_val - 1e-6):
            raise ValueError(
                f"Physical invariant violation: log_pkt_max ({v:.4f}) must be >= log_pkt_mean ({mean_val:.4f})."
            )
        return v


class RawTelemetryInput(BaseModel):
    """Strict schema for raw telemetry inputs used for feature extraction."""

    model_config = {"extra": "allow"}

    pkt_len_mean: Optional[float] = Field(
        None, ge=0.0, le=65535.0, allow_inf_nan=False, alias="Pkt Len Mean"
    )
    pkt_len_max: Optional[float] = Field(
        None, ge=0.0, le=65535.0, allow_inf_nan=False, alias="Pkt Len Max"
    )
    header_length: Optional[float] = Field(
        None, ge=0.0, le=65535.0, allow_inf_nan=False, alias="Header_Length"
    )
    duration: Optional[float] = Field(
        None, ge=0.0, le=86400.0, allow_inf_nan=False, alias="Duration"
    )
    rate: Optional[float] = Field(None, ge=0.0, le=1e9, allow_inf_nan=False, alias="Rate")
    size: Optional[float] = Field(None, ge=0.0, le=1e9, allow_inf_nan=False, alias="Size")


# ==============================================================================
# 2. DataFrame Batch Validator & Quarantine Engine
# ==============================================================================


@dataclass
class ValidationResult:
    """Outcome of validating and sanitizing a telemetry batch."""

    clean_features: pd.DataFrame
    quarantine_mask: np.ndarray  # True indicates row failed validation
    validation_status: pd.Series  # "VALID" or "INVALID_FLAG_FOR_REVIEW"
    rejection_reasons: List[Optional[str]]
    total_rows: int
    quarantine_count: int

    @property
    def all_valid(self) -> bool:
        return self.quarantine_count == 0


class TelemetryValidator:
    """Validates raw and harmonized network flow telemetry batches with fail-closed quarantine."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig.get_default()

    def check_payload_size(self, raw_bytes: bytes) -> None:
        """Enforce request byte size limit."""
        size = len(raw_bytes)
        if size > self.config.max_payload_bytes:
            raise PayloadSizeExceededError(
                f"Payload size {size} bytes exceeds maximum authorized limit of {self.config.max_payload_bytes} bytes."
            )

    def validate_and_sanitize_harmonized(self, df: pd.DataFrame) -> ValidationResult:
        """Validates a DataFrame already containing the 4 harmonized features.

        Fails closed on any row with NaN, Inf, negatives, out-of-bounds, or invariant breaches.
        """
        n_rows = len(df)
        if n_rows > self.config.max_batch_size:
            raise BatchSizeExceededError(
                f"Batch size {n_rows} exceeds maximum permitted threshold of {self.config.max_batch_size} rows."
            )

        if n_rows == 0:
            return ValidationResult(
                clean_features=pd.DataFrame(
                    columns=["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
                ),
                quarantine_mask=np.zeros(0, dtype=bool),
                validation_status=pd.Series(dtype=str),
                rejection_reasons=[],
                total_rows=0,
                quarantine_count=0,
            )

        quarantine_mask = np.zeros(n_rows, dtype=bool)
        rejection_reasons: List[Optional[str]] = [None] * n_rows

        expected_features = ["pkt_mean_to_max", "tcp_flag_density", "log_pkt_mean", "log_pkt_max"]
        missing_cols = [c for c in expected_features if c not in df.columns]
        if missing_cols:
            # If required columns are absent, fail closed on ALL rows
            quarantine_mask[:] = True
            for i in range(n_rows):
                rejection_reasons[i] = f"Missing required columns: {missing_cols}"
            clean = pd.DataFrame(0.0, index=df.index, columns=expected_features)
            status_series = pd.Series(
                ValidationStatus.INVALID_FLAG_FOR_REVIEW.value, index=df.index
            )
            return ValidationResult(
                clean_features=clean,
                quarantine_mask=quarantine_mask,
                validation_status=status_series,
                rejection_reasons=rejection_reasons,
                total_rows=n_rows,
                quarantine_count=n_rows,
            )

        clean = df[expected_features].copy()

        # Step 1: Type check & non-finite (NaN / Inf) detection
        for feat in expected_features:
            col_vals = clean[feat]
            # Check numeric dtype
            if not pd.api.types.is_numeric_dtype(col_vals):
                for i in range(n_rows):
                    if not quarantine_mask[i]:
                        quarantine_mask[i] = True
                        rejection_reasons[i] = f"Column '{feat}' has non-numeric dtype."
                continue

            arr = col_vals.to_numpy(dtype=float, na_value=np.nan)
            invalid_finite = np.isnan(arr) | np.isinf(arr)
            for idx in np.where(invalid_finite)[0]:
                if not quarantine_mask[idx]:
                    quarantine_mask[idx] = True
                    rejection_reasons[idx] = f"Non-finite value in '{feat}'."

        # Step 2: Bound checks against versioned specification
        for feat in expected_features:
            spec = self.config.harmonized_bounds[feat]
            arr = clean[feat].to_numpy(dtype=float, na_value=np.nan)
            tol = 1e-9 if feat == "pkt_mean_to_max" else 0.0
            out_of_bounds = (arr < (spec.min_val - tol)) | (arr > (spec.max_val + tol))
            for idx in np.where(out_of_bounds)[0]:
                if not quarantine_mask[idx]:
                    quarantine_mask[idx] = True
                    rejection_reasons[idx] = (
                        f"Value {arr[idx]} in '{feat}' out of bounds [{spec.min_val}, {spec.max_val}]."
                    )

        # Step 3: Physical & mathematical network invariants
        # Invariant A: log_pkt_mean <= log_pkt_max
        mean_arr = clean["log_pkt_mean"].to_numpy(dtype=float, na_value=np.nan)
        max_arr = clean["log_pkt_max"].to_numpy(dtype=float, na_value=np.nan)
        mean_greater = mean_arr > (max_arr + 1e-6)
        for idx in np.where(mean_greater)[0]:
            if not quarantine_mask[idx]:
                quarantine_mask[idx] = True
                rejection_reasons[idx] = (
                    f"Invariant breach: log_pkt_mean ({mean_arr[idx]:.4f}) > log_pkt_max ({max_arr[idx]:.4f})."
                )

        # Invariant B: pkt_mean_to_max <= 1.0 (mean length cannot exceed max length) with 1e-9 tolerance
        ratio_arr = clean["pkt_mean_to_max"].to_numpy(dtype=float, na_value=np.nan)
        ratio_invalid = ratio_arr > (1.0 + 1e-9)
        for idx in np.where(ratio_invalid)[0]:
            if not quarantine_mask[idx]:
                quarantine_mask[idx] = True
                rejection_reasons[idx] = (
                    f"Invariant breach: pkt_mean_to_max ({ratio_arr[idx]:.4f}) > 1.0."
                )

        status_list = [
            ValidationStatus.INVALID_FLAG_FOR_REVIEW.value if q else ValidationStatus.VALID.value
            for q in quarantine_mask
        ]
        status_series = pd.Series(status_list, index=df.index, name="validation_status")

        # Sanitize clean dataframe so no NaNs or Infs leak downstream to ML inference
        clean = clean.fillna(0.0)
        clean = clean.replace([np.inf, -np.inf], 0.0)
        clean["pkt_mean_to_max"] = np.clip(clean["pkt_mean_to_max"], 0.0, 1.0)

        return ValidationResult(
            clean_features=clean,
            quarantine_mask=quarantine_mask,
            validation_status=status_series,
            rejection_reasons=rejection_reasons,
            total_rows=n_rows,
            quarantine_count=int(np.sum(quarantine_mask)),
        )

    def extract_and_validate_from_raw(self, df: pd.DataFrame) -> ValidationResult:
        """Calculates the 4 features with zero-division handling and fail-closed quarantine."""
        n_rows = len(df)
        if n_rows > self.config.max_batch_size:
            raise BatchSizeExceededError(
                f"Batch size {n_rows} exceeds maximum permitted threshold of {self.config.max_batch_size} rows."
            )

        if n_rows == 0:
            return self.validate_and_sanitize_harmonized(df)

        quarantine_mask = np.zeros(n_rows, dtype=bool)
        rejection_reasons: List[Optional[str]] = [None] * n_rows

        out = pd.DataFrame(index=df.index)

        # Feature 1: pkt_mean_to_max
        if "pkt_mean_to_max" in df.columns:
            out["pkt_mean_to_max"] = df["pkt_mean_to_max"]
        elif "Pkt Len Max" in df.columns and "Pkt Len Mean" in df.columns:
            max_len = pd.to_numeric(df["Pkt Len Max"], errors="coerce").to_numpy(dtype=float)
            mean_len = pd.to_numeric(df["Pkt Len Mean"], errors="coerce").to_numpy(dtype=float)

            # Division safety: sanitize arrays before ufunc to avoid runtime divide-by-zero warnings
            max_len_clean = np.nan_to_num(max_len, nan=0.0, posinf=0.0, neginf=0.0)
            mean_len_clean = np.nan_to_num(mean_len, nan=0.0, posinf=0.0, neginf=0.0)
            valid_div = (
                (max_len_clean > 0)
                & (~np.isnan(max_len))
                & (~np.isnan(mean_len))
                & (~np.isinf(max_len))
                & (~np.isinf(mean_len))
            )
            ratio = np.zeros(n_rows, dtype=float)
            np.divide(mean_len_clean, max_len_clean, out=ratio, where=valid_div)

            # Identify zero division or undefined states
            zero_or_nan = (~valid_div) | np.isnan(ratio) | np.isinf(ratio)
            for idx in np.where(zero_or_nan)[0]:
                quarantine_mask[idx] = True
                rejection_reasons[idx] = "Zero division or NaN in packet length ratio calculation."

            out["pkt_mean_to_max"] = ratio
        elif "Header_Length" in df.columns and "Duration" in df.columns:
            hdr_len = pd.to_numeric(df["Header_Length"], errors="coerce").to_numpy(dtype=float)
            dur = pd.to_numeric(df["Duration"], errors="coerce").to_numpy(dtype=float)
            hdr_clean = np.nan_to_num(hdr_len, nan=0.0, posinf=0.0, neginf=0.0)
            dur_clean = np.nan_to_num(dur, nan=0.0, posinf=0.0, neginf=0.0)
            valid_div = (
                (hdr_clean > 0)
                & (~np.isnan(hdr_len))
                & (~np.isnan(dur))
                & (~np.isinf(hdr_len))
                & (~np.isinf(dur))
            )
            ratio = np.zeros(n_rows, dtype=float)
            np.divide(dur_clean, hdr_clean, out=ratio, where=valid_div)
            zero_or_nan = (~valid_div) | np.isnan(ratio) | np.isinf(ratio)
            for idx in np.where(zero_or_nan)[0]:
                quarantine_mask[idx] = True
                rejection_reasons[idx] = (
                    "Zero division or NaN in header/duration ratio calculation."
                )
            out["pkt_mean_to_max"] = ratio
        else:
            out["pkt_mean_to_max"] = 0.0
            quarantine_mask[:] = True
            for i in range(n_rows):
                if not rejection_reasons[i]:
                    rejection_reasons[i] = "Missing telemetry columns for pkt_mean_to_max."

        # Feature 2: tcp_flag_density
        if "tcp_flag_density" in df.columns:
            out["tcp_flag_density"] = pd.to_numeric(df["tcp_flag_density"], errors="coerce").fillna(
                0.0
            )
        else:
            flag_cols = [c for c in df.columns if "flag" in c.lower()]
            if flag_cols:
                flag_df = df[flag_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
                out["tcp_flag_density"] = flag_df.sum(axis=1)
            else:
                out["tcp_flag_density"] = 0.0

        # Feature 3: log_pkt_mean
        if "log_pkt_mean" in df.columns:
            out["log_pkt_mean"] = pd.to_numeric(df["log_pkt_mean"], errors="coerce")
        elif "Pkt Len Mean" in df.columns:
            vals = pd.to_numeric(df["Pkt Len Mean"], errors="coerce").to_numpy(dtype=float)
            neg_or_nan = (vals < 0) | np.isnan(vals) | np.isinf(vals)
            for idx in np.where(neg_or_nan)[0]:
                quarantine_mask[idx] = True
                rejection_reasons[idx] = "Negative or non-finite Pkt Len Mean."
            safe_vals = np.clip(np.nan_to_num(vals, nan=0.0, posinf=65535.0, neginf=0.0), 0, None)
            out["log_pkt_mean"] = np.log1p(safe_vals)
        elif "Rate" in df.columns:
            vals = pd.to_numeric(df["Rate"], errors="coerce").to_numpy(dtype=float)
            neg_or_nan = (vals < 0) | np.isnan(vals) | np.isinf(vals)
            for idx in np.where(neg_or_nan)[0]:
                quarantine_mask[idx] = True
                rejection_reasons[idx] = "Negative or non-finite Rate."
            safe_vals = np.clip(np.nan_to_num(vals, nan=0.0, posinf=1e9, neginf=0.0), 0, None)
            out["log_pkt_mean"] = np.log1p(safe_vals)
        else:
            out["log_pkt_mean"] = 0.0
            quarantine_mask[:] = True
            for i in range(n_rows):
                if not rejection_reasons[i]:
                    rejection_reasons[i] = "Missing telemetry columns for log_pkt_mean."

        # Feature 4: log_pkt_max
        if "log_pkt_max" in df.columns:
            out["log_pkt_max"] = pd.to_numeric(df["log_pkt_max"], errors="coerce")
        elif "Pkt Len Max" in df.columns:
            vals = pd.to_numeric(df["Pkt Len Max"], errors="coerce").to_numpy(dtype=float)
            neg_or_nan = (vals < 0) | np.isnan(vals) | np.isinf(vals)
            for idx in np.where(neg_or_nan)[0]:
                quarantine_mask[idx] = True
                rejection_reasons[idx] = "Negative or non-finite Pkt Len Max."
            safe_vals = np.clip(np.nan_to_num(vals, nan=0.0, posinf=65535.0, neginf=0.0), 0, None)
            out["log_pkt_max"] = np.log1p(safe_vals)
        elif "Size" in df.columns:
            vals = pd.to_numeric(df["Size"], errors="coerce").to_numpy(dtype=float)
            neg_or_nan = (vals < 0) | np.isnan(vals) | np.isinf(vals)
            for idx in np.where(neg_or_nan)[0]:
                quarantine_mask[idx] = True
                rejection_reasons[idx] = "Negative or non-finite Size."
            safe_vals = np.clip(np.nan_to_num(vals, nan=0.0, posinf=1e9, neginf=0.0), 0, None)
            out["log_pkt_max"] = np.log1p(safe_vals)
        else:
            out["log_pkt_max"] = 0.0
            quarantine_mask[:] = True
            for i in range(n_rows):
                if not rejection_reasons[i]:
                    rejection_reasons[i] = "Missing telemetry columns for log_pkt_max."

        # Run harmonized boundary validation on extracted values
        res = self.validate_and_sanitize_harmonized(out)
        combined_mask = quarantine_mask | res.quarantine_mask
        for idx in range(n_rows):
            if combined_mask[idx] and not rejection_reasons[idx]:
                rejection_reasons[idx] = res.rejection_reasons[idx]

        status_list = [
            ValidationStatus.INVALID_FLAG_FOR_REVIEW.value if q else ValidationStatus.VALID.value
            for q in combined_mask
        ]
        status_series = pd.Series(status_list, index=df.index, name="validation_status")

        return ValidationResult(
            clean_features=res.clean_features,
            quarantine_mask=combined_mask,
            validation_status=status_series,
            rejection_reasons=rejection_reasons,
            total_rows=n_rows,
            quarantine_count=int(np.sum(combined_mask)),
        )


# ==============================================================================
# 3. External Response Sanitizer (Hides Raw Probabilities, Returns Decision & Tier)
# ==============================================================================


class ExternalInferenceResponse(BaseModel):
    """External response schema strictly omitting internal raw probabilities and logit scores."""

    event_id: str = Field(..., description="Unique event or request correlation ID")
    model_name: str = Field(..., description="Evaluating model identifier")
    decision: SecurityDecision = Field(..., description="Operational decision verdict")
    tier: AlertTier = Field(..., description="Operational severity and alerting tier")
    status: ValidationStatus = Field(
        ValidationStatus.VALID, description="Input validation and integrity status"
    )
    quarantine_reason: Optional[str] = Field(
        None, description="Reason if input was flagged for review"
    )


def sanitize_inference_output(
    event_id: str,
    model_name: str,
    raw_probability: float,
    threshold: float,
    is_valid: bool = True,
    quarantine_reason: Optional[str] = None,
) -> ExternalInferenceResponse:
    """Transforms raw internal model scoring into a fail-closed external response.

    Rules:
    - Never return raw probabilities to external callers.
    - If is_valid is False (invalid row): FAIL CLOSED -> Decision: QUARANTINE,
      Tier: TIER_REVIEW, Status: INVALID_FLAG_FOR_REVIEW. NEVER classified as BENIGN.
    - If valid:
        - If prob >= threshold: ATTACK (TIER_1_HIGH_CONFIDENCE if prob >= 0.90 else TIER_2_SUSPICIOUS)
        - If prob < threshold: BENIGN (TIER_UNVERIFIED_BENIGN - explicitly unverified, never 'safe')
    """
    if not is_valid or math.isnan(raw_probability) or math.isinf(raw_probability):
        return ExternalInferenceResponse(
            event_id=event_id,
            model_name=model_name,
            decision=SecurityDecision.QUARANTINE,
            tier=AlertTier.TIER_REVIEW,
            status=ValidationStatus.INVALID_FLAG_FOR_REVIEW,
            quarantine_reason=quarantine_reason or "Input failed validation checks.",
        )

    if raw_probability >= threshold:
        tier = (
            AlertTier.TIER_1_HIGH_CONFIDENCE
            if raw_probability >= 0.90
            else AlertTier.TIER_2_SUSPICIOUS
        )
        return ExternalInferenceResponse(
            event_id=event_id,
            model_name=model_name,
            decision=SecurityDecision.ATTACK,
            tier=tier,
            status=ValidationStatus.VALID,
            quarantine_reason=None,
        )

    return ExternalInferenceResponse(
        event_id=event_id,
        model_name=model_name,
        decision=SecurityDecision.BENIGN,
        tier=AlertTier.TIER_UNVERIFIED_BENIGN,
        status=ValidationStatus.VALID,
        quarantine_reason=None,
    )
