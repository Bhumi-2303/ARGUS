import numpy as np
from typing import Any
from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.data_intelligence.schemas import CleanedChunk, NormalizedChunk, PipelineConfig

class NormalizerTool(BaseTool):
    """Normalizes numeric data using min-max or z-score scaling."""

    def __init__(self):
        super().__init__(
            tool_id="tool-normalizer-01",
            name="normalizer",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Normalizes dataframe columns.",
            required_permissions=["data:write"]
        )

    async def initialize(self) -> None:
        pass

    async def validate(self, **kwargs: Any) -> bool:
        return "cleaned_chunk" in kwargs and "config" in kwargs

    async def execute(self, **kwargs: Any) -> NormalizedChunk:
        cleaned_chunk: CleanedChunk = kwargs["cleaned_chunk"]
        config: PipelineConfig = kwargs["config"]
        
        df = cleaned_chunk.data.copy()
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        parameters = {}
        
        if config.normalization_method == "min_max":
            for col in numeric_cols:
                c_min = float(df[col].min())
                c_max = float(df[col].max())
                parameters[col] = {"min": c_min, "max": c_max}
                if c_max > c_min:
                    df[col] = (df[col] - c_min) / (c_max - c_min)
                else:
                    df[col] = 0.0
                    
        elif config.normalization_method == "z_score":
            for col in numeric_cols:
                c_mean = float(df[col].mean())
                c_std = float(df[col].std())
                parameters[col] = {"mean": c_mean, "std": c_std}
                if c_std > 0:
                    df[col] = (df[col] - c_mean) / c_std
                else:
                    df[col] = 0.0

        return NormalizedChunk(
            cleaned_chunk=cleaned_chunk,
            data=df,
            method=config.normalization_method,
            parameters=parameters
        )

    async def shutdown(self) -> None:
        pass

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {
                "cleaned_chunk": {"type": "object"},
                "config": {"type": "object"}
            },
            "required": ["cleaned_chunk", "config"]
        }
        return md
