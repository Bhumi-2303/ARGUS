"""Internal data models and schemas for Explainability Agent."""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ExplainabilityInput(BaseModel):
    """Schema for incoming Explainability request."""
    event_id: str = Field(..., description="Unique event ID")
    correlation_id: Optional[str] = Field(default=None, description="Pipeline trace correlation ID")
    features: Dict[str, float] = Field(..., description="Feature vector used in Threat Analysis")
    model_version: str = Field(..., description="The model used by Threat Analysis")


class FeatureAttribution(BaseModel):
    """Single feature's attribution data."""
    feature_name: str
    feature_value: float
    shap_value: float
    is_top_contributor: bool = False


class ExplainabilityResult(BaseModel):
    """Combined output of the Explainability pipeline."""
    status: str = Field(..., description="'available' or 'unavailable'")
    reason: Optional[str] = Field(default=None, description="Reason if status is unavailable")
    
    event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    model_version: Optional[str] = None
    
    base_value: Optional[float] = None
    shap_values: Dict[str, float] = Field(default_factory=dict)
    top_feature: Optional[str] = None
    top_feature_impact: Optional[float] = None
    latency_ms: float = Field(default=0.0, description="SHAP computation latency")
