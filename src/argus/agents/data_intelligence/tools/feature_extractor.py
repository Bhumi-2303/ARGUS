import numpy as np
import pandas as pd
from typing import Any
from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.data_intelligence.schemas import NormalizedChunk, ExtractedFeatures

class FeatureExtractorTool(BaseTool):
    """Extracts statistical features from the normalized dataset."""

    def __init__(self):
        super().__init__(
            tool_id="tool-feature-extractor-01",
            name="feature_extractor",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Extracts basic statistical features.",
            required_permissions=["data:read"]
        )

    async def initialize(self) -> None:
        pass

    async def validate(self, **kwargs: Any) -> bool:
        return "normalized_chunk" in kwargs

    async def execute(self, **kwargs: Any) -> ExtractedFeatures:
        normalized_chunk: NormalizedChunk = kwargs["normalized_chunk"]
        
        df = normalized_chunk.data
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        statistics = {}
        
        for col in numeric_cols:
            series = df[col]
            statistics[col] = {
                "min": float(series.min()) if not series.empty else 0.0,
                "max": float(series.max()) if not series.empty else 0.0,
                "mean": float(series.mean()) if not series.empty else 0.0,
                "std": float(series.std()) if not series.empty and len(series) > 1 else 0.0,
                "median": float(series.median()) if not series.empty else 0.0,
                "null_count": int(series.isna().sum()),
                "zero_count": int((series == 0).sum())
            }
            
        return ExtractedFeatures(
            normalized_chunk=normalized_chunk,
            feature_names=numeric_cols,
            statistics=statistics
        )

    async def shutdown(self) -> None:
        pass

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {
                "normalized_chunk": {"type": "object"}
            },
            "required": ["normalized_chunk"]
        }
        return md
