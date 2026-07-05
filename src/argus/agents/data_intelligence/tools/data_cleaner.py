import numpy as np
from typing import Any
from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.data_intelligence.schemas import ValidatedChunk, CleanedChunk, PipelineConfig

class DataCleanerTool(BaseTool):
    """Cleans data chunk by handling NaNs, infs, and dropping unwanted columns."""

    def __init__(self):
        super().__init__(
            tool_id="tool-data-cleaner-01",
            name="data_cleaner",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Cleans dataframe by handling NaNs, infs, and dropping unneeded columns.",
            required_permissions=["data:write"]
        )

    async def initialize(self) -> None:
        pass

    async def validate(self, **kwargs: Any) -> bool:
        return "validated_chunk" in kwargs and "config" in kwargs

    async def execute(self, **kwargs: Any) -> CleanedChunk:
        validated_chunk: ValidatedChunk = kwargs["validated_chunk"]
        config: PipelineConfig = kwargs["config"]
        
        df = validated_chunk.raw_chunk.data.copy()
        
        initial_rows = len(df)
        
        # Remove exact duplicates
        df = df.drop_duplicates()
        duplicates_removed = initial_rows - len(df)
        
        # Handle infs
        # Replace inf with NaN first, so we can fill them in the next step
        infs_replaced = 0
        import pandas as pd
        if df.isin([np.inf, -np.inf]).any().any():
            infs_replaced = int((df == np.inf).sum().sum() + (df == -np.inf).sum().sum())
            df = df.replace([np.inf, -np.inf], np.nan)
        
        # Handle NaNs
        nulls_filled = int(df.isna().sum().sum())
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        string_cols = df.select_dtypes(exclude=[np.number]).columns
        
        if len(numeric_cols) > 0:
            df[numeric_cols] = df[numeric_cols].fillna(0)
        if len(string_cols) > 0:
            df[string_cols] = df[string_cols].fillna("unknown")

        # Drop columns
        cols_to_drop = []
        if config.drop_labels:
            cols_to_drop.extend(["Label", "Attack"])
        if config.drop_ips:
            cols_to_drop.extend(["IPV4_SRC_ADDR", "IPV4_DST_ADDR"])
            
        cols_to_drop = [c for c in cols_to_drop if c in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)

        return CleanedChunk(
            validated_chunk=validated_chunk,
            data=df,
            nulls_filled=nulls_filled,
            infs_replaced=infs_replaced,
            duplicates_removed=duplicates_removed
        )

    async def shutdown(self) -> None:
        pass

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {
                "validated_chunk": {"type": "object"},
                "config": {"type": "object"}
            },
            "required": ["validated_chunk", "config"]
        }
        return md
