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

