from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import pandas as pd
from pydantic import BaseModel, Field

class RawChunk(BaseModel):
    """Raw chunk of data loaded from a file."""
    file_path: str
    chunk_index: int
    data: pd.DataFrame
    row_count: int

    class Config:
        arbitrary_types_allowed = True

class ValidatedChunk(BaseModel):
    """Chunk of data after schema validation."""
    raw_chunk: RawChunk
    is_valid: bool
    missing_columns: List[str] = Field(default_factory=list)
    type_mismatches: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class CleanedChunk(BaseModel):
    """Chunk of data after cleaning (handling NaNs, infs, duplicates)."""
    validated_chunk: ValidatedChunk
    data: pd.DataFrame
    nulls_filled: int = 0
    infs_replaced: int = 0
    duplicates_removed: int = 0
    
    class Config:
        arbitrary_types_allowed = True

class NormalizedChunk(BaseModel):
    """Chunk of data after normalization."""
    cleaned_chunk: CleanedChunk
    data: pd.DataFrame
    method: str
    parameters: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class ExtractedFeatures(BaseModel):
    """Final feature statistics extracted from the normalized data."""
    normalized_chunk: NormalizedChunk
    feature_names: List[str]
    statistics: Dict[str, Dict[str, float]]
    
    class Config:
        arbitrary_types_allowed = True

@dataclass
class PipelineConfig:
    """Configuration for the Data Intelligence pipeline."""
    chunk_size: int = 10000
    normalization_method: str = "min_max"
    drop_labels: bool = True
    drop_ips: bool = True
    max_chunks: Optional[int] = None


# ------------------------------------------------------------------
# Single-flow processing schemas
# ------------------------------------------------------------------

class FlowInput(BaseModel):
    """A single raw network flow record for feature extraction.

    Accepts either:
    - Pre-computed harmonized features (pkt_mean_to_max, tcp_flag_density,
      log_pkt_mean, log_pkt_max) — passed through with validation only.
    - Raw network telemetry columns (e.g. Pkt Len Mean, Pkt Len Max, TCP flags)
      — harmonized features are computed via ``extract_four_features()``.
    """
    correlation_id: Optional[str] = Field(default=None, description="Pipeline correlation ID")
    event_id: Optional[str] = Field(default=None, description="Unique event identifier")
    source_domain: str = Field(default="unknown", description="Source domain (e.g. nfton, ciciot)")
    fields: Dict[str, Any] = Field(..., description="Raw flow fields or pre-computed features")


class FlowValidationError(BaseModel):
    """Structured error when a flow cannot be processed."""
    correlation_id: Optional[str] = None
    event_id: Optional[str] = None
    error: str
    error_type: str
    received_fields: List[str] = Field(default_factory=list)
    required_fields: List[str] = Field(default_factory=list)


class FlowResult(BaseModel):
    """Structured DIA output for a single processed network flow.

    Contains exactly the feature vector consumed by the Threat Analysis Agent
    (``FeatureEventInput.features``).
    """
    correlation_id: Optional[str] = None
    event_id: Optional[str] = None
    source_domain: str = "unknown"
    status: str = Field(..., description="'success' or 'error'")
    features: Dict[str, float] = Field(
        default_factory=dict,
        description="The 4 harmonized features: pkt_mean_to_max, tcp_flag_density, log_pkt_mean, log_pkt_max",
    )
    feature_source: str = Field(
        default="unknown",
        description="'pre_computed' if features were passed in, 'extracted' if computed from raw telemetry",
    )
    input_field_count: int = Field(default=0, description="Number of fields received")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal issues")
    processing_duration_ms: float = Field(default=0.0, description="Processing time in ms")
    error: Optional[FlowValidationError] = None


