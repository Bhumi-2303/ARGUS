import os
import math
import time
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from argus.core.base_agent import BaseAgent
from argus.core.enums import BlackboardSection
from argus.schemas.messages import FeatureEvent
from argus.agents.data_intelligence.pipeline import DataPipeline
from argus.agents.data_intelligence.schemas import (
    PipelineConfig, FlowInput, FlowResult, FlowValidationError,
)
from argus.features.extractor import extract_four_features, FEATURE_NAMES
from argus.registry.model_registry import HARMONIZED_FEATURES


class DataIntelligenceAgent(BaseAgent):
    """
    Data Intelligence Agent
    
    Responsibilities in production:
    - Ingests raw smart grid data (SCADA, IoT).
    - Normalizes data into a standard schema.
    - Correlates events across different sensors.
    """
    
    def __init__(self, **kwargs):
        kwargs.setdefault("agent_id", "agent_data_intelligence")
        kwargs.setdefault("name", "Data Intelligence Agent")
        kwargs.setdefault("version", "1.0.0")
        kwargs.setdefault("description", "Ingests and processes network flow data.")
        kwargs.setdefault("capabilities", ["data_ingestion", "feature_extraction"])
        kwargs.setdefault("permissions", ["read:flow"])
        kwargs.setdefault("tools", [])
        super().__init__(**kwargs)

    async def initialize(self) -> None:
        self.logger.info("initializing_data_intelligence_agent")
        self.pipeline = DataPipeline(agent_id=str(self.agent_id))
        await self.pipeline.initialize()
        
    async def validate(self, input_data: Any) -> bool:
        self.logger.debug("validating_input")
        if not isinstance(input_data, dict):
            return False
        if "file_path" not in input_data:
            return False
        file_path = input_data["file_path"]
        if not os.path.exists(file_path):
            return False
        if not file_path.endswith((".csv", ".parquet")):
            return False
        return True
        
    async def reason(self, context: Any) -> Any:
        self.logger.debug("reasoning")
        config_params = context.get("pipeline_config", {}) if isinstance(context, dict) else {}
        file_path = context.get("file_path", "") if isinstance(context, dict) else ""
        return {
            "config": PipelineConfig(
                chunk_size=config_params.get("chunk_size", 10000),
                normalization_method=config_params.get("normalization_method", "min_max"),
                drop_labels=config_params.get("drop_labels", True),
                drop_ips=config_params.get("drop_ips", True),
                max_chunks=config_params.get("max_chunks")
            ),

            "file_path": file_path
        }
        
    async def plan(self, reasoning: Any) -> Any:
        self.logger.debug("planning")
        return {
            "stages": ["load", "validate", "clean", "normalize", "extract", "publish"],
            "config": reasoning["config"],
            "file_path": reasoning["file_path"]
        }
        
    async def execute(self, plan: Any) -> Any:
        self.logger.debug("executing_plan")
        config: PipelineConfig = plan["config"]
        file_path: str = plan["file_path"]
        
        events = []
        async for event in self.pipeline.process_file(file_path, config):
            events.append(event)
            
        return events

        
    async def call_tools(self, tool_requests: List[Any]) -> List[Any]:
        # Tools are orchestrated by the pipeline internally for this specific agent.
        return []
        
    async def update_memory(self, result: Any) -> None:
        if self.working_memory:
            await self.working_memory.set(f"latest_result_{self.agent_id}", result)
        
    async def publish(self, result: Any) -> None:
        self.logger.info("publishing_results", result_count=len(result))
        for event in result:
            # Write to blackboard
            if self.blackboard:
                await self.blackboard.write(
                    BlackboardSection.DATA_RESULTS,
                    key=f"feature_event_{event.request_id}",
                    value=event.model_dump(),
                    agent_id=str(self.agent_id)
                )
            # Publish to message bus
            if self.message_bus:
                await self.message_bus.publish("events.feature", event)
        
    async def health(self) -> Any:
        return {
            "status": "healthy",
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_response_time": self.avg_response_time
        }
        
    async def shutdown(self) -> None:
        self.logger.info("shutting_down_data_intelligence_agent")
        await self.pipeline.shutdown()

    # ------------------------------------------------------------------
    # Single-flow processing
    # ------------------------------------------------------------------

    async def process_flow(self, flow_input: FlowInput) -> FlowResult:
        """Process a single network flow and return the 4 harmonized features.

        This method accepts either:
        - A dict with the 4 pre-computed harmonized features
        - A dict with raw network telemetry columns (e.g. CICIoT/NF-ToN format)

        In both cases the features are validated before returning.  Nothing is
        fabricated: if a feature cannot be computed from the input fields, an
        error is returned.

        The output ``FlowResult.features`` is directly usable as
        ``FeatureEventInput.features`` by the Threat Analysis Agent.
        """
        start = time.monotonic()
        corr_id = flow_input.correlation_id
        evt_id = flow_input.event_id
        fields = flow_input.fields
        warnings: List[str] = []

        # ----------------------------------------------------------
        # Determine if the input already has pre-computed features
        # ----------------------------------------------------------
        has_precomputed = all(f in fields for f in HARMONIZED_FEATURES)

        if has_precomputed:
            # ---- Pre-computed path: validate directly ----
            features: Dict[str, float] = {}
            for fname in HARMONIZED_FEATURES:
                raw_val = fields[fname]
                # Coerce to float
                try:
                    val = float(raw_val)
                except (TypeError, ValueError):
                    return self._flow_error(
                        corr_id, evt_id, fields,
                        f"Feature '{fname}' cannot be converted to float: {raw_val!r}",
                        "type_error",
                    )
                if math.isnan(val) or math.isinf(val):
                    return self._flow_error(
                        corr_id, evt_id, fields,
                        f"Feature '{fname}' has non-finite value: {val}",
                        "value_error",
                    )
                features[fname] = val

            feature_source = "pre_computed"

        else:
            # ---- Raw telemetry path: extract via features/extractor.py ----
            # Convert the fields dict into a single-row DataFrame
            try:
                df = pd.DataFrame([fields])
            except Exception as exc:
                return self._flow_error(
                    corr_id, evt_id, fields,
                    f"Cannot construct DataFrame from input fields: {exc}",
                    "input_error",
                )

            # Use the existing extractor
            extracted_df = extract_four_features(df)

            # Check that extraction produced actual values, not zeros from fallback
            features = {}
            for fname in FEATURE_NAMES:
                val = float(extracted_df[fname].iloc[0])
                if math.isnan(val) or math.isinf(val):
                    return self._flow_error(
                        corr_id, evt_id, fields,
                        f"Extracted feature '{fname}' is non-finite ({val}). "
                        f"Check that input fields contain the required raw columns.",
                        "extraction_error",
                    )
                features[fname] = val

            # Warn if all extracted features are zero (likely missing source columns)
            if all(v == 0.0 for v in features.values()):
                # Check which source columns were present
                known_sources = {"Pkt Len Mean", "Pkt Len Max", "Header_Length",
                                 "Duration", "Rate", "Size"}
                flag_cols = [c for c in df.columns if "flag" in c.lower()]
                present = known_sources.intersection(set(df.columns))
                if not present and not flag_cols:
                    return self._flow_error(
                        corr_id, evt_id, fields,
                        "No recognizable raw telemetry columns found. "
                        "Expected either the 4 harmonized features "
                        f"({HARMONIZED_FEATURES}) or raw columns like "
                        "'Pkt Len Mean', 'Pkt Len Max', TCP flag columns, etc.",
                        "missing_fields",
                    )
                warnings.append(
                    "All extracted features are 0.0 — the input may not "
                    "contain meaningful telemetry data."
                )

            feature_source = "extracted"

        elapsed_ms = (time.monotonic() - start) * 1000.0
        self.logger.info(
            "flow_processed",
            correlation_id=corr_id,
            feature_source=feature_source,
            duration_ms=f"{elapsed_ms:.2f}",
        )

        return FlowResult(
            correlation_id=corr_id,
            event_id=evt_id,
            source_domain=flow_input.source_domain,
            status="success",
            features=features,
            feature_source=feature_source,
            input_field_count=len(fields),
            warnings=warnings,
            processing_duration_ms=round(elapsed_ms, 3),
        )

    @staticmethod
    def _flow_error(
        corr_id: Optional[str],
        evt_id: Optional[str],
        fields: Dict[str, Any],
        error_msg: str,
        error_type: str,
    ) -> FlowResult:
        """Build an error FlowResult without fabricating any feature data."""
        return FlowResult(
            correlation_id=corr_id,
            event_id=evt_id,
            status="error",
            features={},
            feature_source="none",
            input_field_count=len(fields),
            error=FlowValidationError(
                correlation_id=corr_id,
                event_id=evt_id,
                error=error_msg,
                error_type=error_type,
                received_fields=list(fields.keys()),
                required_fields=list(HARMONIZED_FEATURES),
            ),
        )
