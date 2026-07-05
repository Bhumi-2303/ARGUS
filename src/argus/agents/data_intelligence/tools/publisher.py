import time
import uuid
from datetime import datetime, timezone
from typing import Any
from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory, TaskPriority
from argus.schemas.messages import FeatureEvent
from argus.agents.data_intelligence.schemas import ExtractedFeatures

class PublisherTool(BaseTool):
    """Builds FeatureEvent messages from extracted features."""

    def __init__(self):
        super().__init__(
            tool_id="tool-publisher-01",
            name="publisher",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Builds FeatureEvent messages for publication.",
            required_permissions=["data:write"]
        )

    async def initialize(self) -> None:
        pass

    async def validate(self, **kwargs: Any) -> bool:
        return "extracted_features" in kwargs and "agent_id" in kwargs and "start_time" in kwargs

    async def execute(self, **kwargs: Any) -> FeatureEvent:
        features: ExtractedFeatures = kwargs["extracted_features"]
        agent_id: str = kwargs["agent_id"]
        start_time: float = kwargs["start_time"]
        
        processing_duration = (time.time() - start_time) * 1000.0
        cleaned = features.normalized_chunk.cleaned_chunk
        raw = cleaned.validated_chunk.raw_chunk
        
        return FeatureEvent(
            request_id=str(uuid.uuid4()),
            trace_id=str(uuid.uuid4()),
            agent_id=agent_id,
            timestamp=datetime.now(timezone.utc),
            priority=TaskPriority.HIGH,
            event_type="FEATURE_EVENT",
            source_file=raw.file_path,
            chunk_index=raw.chunk_index,
            records_processed=raw.row_count,
            records_dropped=cleaned.duplicates_removed,
            feature_names=features.feature_names,
            feature_stats=features.statistics,
            normalization_method=features.normalized_chunk.method,
            processing_duration_ms=processing_duration
        )

    async def shutdown(self) -> None:
        pass

    def metadata(self) -> dict:
        md = super().metadata()
        md["parameters_schema"] = {
            "type": "object",
            "properties": {
                "extracted_features": {"type": "object"},
                "agent_id": {"type": "string"},
                "start_time": {"type": "number"}
            },
            "required": ["extracted_features", "agent_id", "start_time"]
        }
        return md
