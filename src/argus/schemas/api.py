"""Pydantic schemas for the ARGUS FastAPI v1 endpoints."""

from typing import Dict, List, Any, Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[str] = None



class HealthResponse(BaseModel):
    status: str = Field("healthy", description="System health status")
    uptime_seconds: float = Field(..., description="API server uptime in seconds")
    timestamp: str = Field(..., description="Current UTC ISO timestamp")
    models_loaded: Dict[str, bool] = Field(..., description="Dictionary of loaded model readiness")


class DomainInfo(BaseModel):
    domain_id: str = Field(..., description="Unique domain identifier (e.g. ciciot, nfton, iec104)")
    name: str = Field(..., description="Full descriptive name of domain")
    sample_size: int = Field(..., description="Number of sample rows in sample parquet")
    attack_ratio: float = Field(..., description="Attack sample proportion (0.0 - 1.0)")
    features: List[str] = Field(..., description="List of harmonized feature names")
    status: str = Field(default="verified", description="verified, partial, or planned")
    description: str = Field(..., description="Domain protocol and network description")


class DomainsResponse(BaseModel):
    domains: List[DomainInfo]


class ModelInfo(BaseModel):
    model_id: str
    name: str
    protocol_status: str = Field(..., description="Protocol classification: native, coral_aligned, dann_adapted, or diagnostic_only")
    threshold: float = Field(..., description="Decision threshold for binary classification")
    source_domain: str
    status: str = Field(default="verified", description="verified, partial, or planned")
    target_domain: str
    provenance: Dict[str, Any] = Field(..., description="Artifact provenance metadata")


class ModelsResponse(BaseModel):
    models: List[ModelInfo]


class ResultTableResponse(BaseModel):
    table_name: str
    source_file: str
    protocol_status: str
    diagnostic_only: bool = Field(False, description="Flag indicating if results are post-hoc diagnostic only")
    row_count: int
    data: List[Dict[str, Any]]


class FeatureInput(BaseModel):
    pkt_mean_to_max: float = Field(..., description="Ratio of mean packet size to max packet size")
    tcp_flag_density: float = Field(..., description="Density of TCP flags across connection")
    log_pkt_mean: float = Field(..., description="Logarithm of mean packet length")
    log_pkt_max: float = Field(..., description="Logarithm of max packet length")


class PredictRequest(BaseModel):
    features: FeatureInput
    model_name: str = Field("model_d2_coral", description="Target model for prediction")


class ModelPredictionDetail(BaseModel):
    probability: float
    label: int


class PredictResponse(BaseModel):
    model_name: str
    probability: float
    prediction: int = Field(..., description="Binary classification label (0=Benign, 1=Attack)")
    threshold: float
    features: Dict[str, float]


class StreamEventPayload(BaseModel):
    event_id: str
    timestamp: str
    domain: str
    features: Dict[str, float]
    true_label: int
    predictions: Dict[str, ModelPredictionDetail]


class FeatureShiftMetric(BaseModel):
    feature: str
    ks_statistic: float
    ks_pvalue: float
    psi_statistic: float
    shift_detected: bool


class ShiftResponse(BaseModel):
    target_domain: str
    reference_domain: str
    window_size: int
    ks_threshold: float
    psi_threshold: float
    domain_shift: bool = Field(..., description="Flag indicating overall domain shift across features")
    feature_shifts: List[FeatureShiftMetric]


class ExplainRequest(BaseModel):
    features: FeatureInput
    model_name: str = Field("model_d2_coral", description="Target model for SHAP attribution")


class ExplainResponse(BaseModel):
    model_name: str
    base_value: float
    shap_values: Dict[str, float]
    feature_values: Dict[str, float]
    top_feature: str
    top_feature_impact: float


class OnboardRequest(BaseModel):
    target_domain: str = Field("nfton", description="Target domain identifier for demo onboarding")
    adaptation_window_size: int = Field(5000, description="Size of adaptation window for CORAL transform")
    calibration_window_size: int = Field(2000, description="Size of calibration window for threshold selection")
    test_window_size: int = Field(3000, description="Size of test window for evaluation")


class OnboardResponse(BaseModel):
    target_domain: str
    demo_scale: bool = Field(True, description="Always true for demo-scale onboarding responses")
    coral_fitted: bool
    selected_threshold: float
    metrics: Dict[str, float] = Field(..., description="Evaluated test metrics: accuracy, f1, mcc, fpr, fnr")
    evaluated_test_size: int


class TestCaseItem(BaseModel):
    id: str
    name: str
    domain: str
    domain_name: str
    ground_truth_label: int
    ground_truth_class: str
    features: Dict[str, float]
    provenance: str

