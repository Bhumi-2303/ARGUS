"""Internal data models and schemas for Threat Analysis Agent."""
from enum import StrEnum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ModelType(StrEnum):
    """Supported ML model types."""
    XGBOOST = "xgboost"
    ISOLATION_FOREST = "isolation_forest"
    RANDOM_FOREST = "random_forest"


class ThreatLevel(StrEnum):
    """Normalized threat level classification."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class InferenceResult(BaseModel):
    """Output from the Inference Engine tool."""
    prediction: Any = Field(..., description="Raw model prediction")
    probabilities: Optional[List[float]] = Field(default=None, description="Class probabilities if available")
    raw_output: Any = Field(..., description="Raw model output payload")
    model_type: ModelType = Field(..., description="Type of model used")
    latency_ms: float = Field(..., description="Inference latency in milliseconds")


class ConfidenceResult(BaseModel):
    """Output from the Confidence Calculator tool."""
    confidence_score: float = Field(..., description="Normalized confidence 0.0 to 1.0")
    threat_level: ThreatLevel = Field(..., description="Mapped threat level")
    threshold_used: float = Field(..., description="Threshold used for mapping")


class Evidence(BaseModel):
    """A single piece of evidence collected by the Evidence Collector tool."""
    type: str = Field(..., description="Type of evidence (e.g., 'feature_importance', 'anomaly')")
    description: str = Field(..., description="Human readable description")
    importance: float = Field(..., description="Importance score or deviation amount")
    value: Any = Field(default=None, description="Actual feature value")


class FeatureEventInput(BaseModel):
    """Schema for incoming FEATURE_EVENT payloads."""
    event_id: str = Field(..., description="Unique event ID")
    correlation_id: Optional[str] = Field(default=None, description="Pipeline trace correlation ID")
    source: str = Field(..., description="Source of the features")
    features: Dict[str, float] = Field(..., description="Feature vector")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    model_version: Optional[str] = Field(default=None, description="Target model requested")


class ThreatAnalysisResult(BaseModel):
    """Combined output of the entire reasoning/execution pipeline."""
    source_event_id: str
    correlation_id: Optional[str] = None
    threat_level: ThreatLevel
    confidence: float
    evidence: List[Evidence] = Field(default_factory=list)
    gemini_analysis: Optional[str] = None
    recommended_actions: List[str] = Field(default_factory=list)
    model_version: str
    protocol_status: str
    latency_ms: float = Field(default=0.0, description="Model inference latency")

