import os
from typing import Any, List
from argus.core.base_agent import BaseAgent
from argus.core.enums import BlackboardSection
from argus.schemas.messages import FeatureEvent
from argus.agents.data_intelligence.pipeline import DataPipeline
from argus.agents.data_intelligence.schemas import PipelineConfig


class DataIntelligenceAgent(BaseAgent):
    """
    Data Intelligence Agent
    
    Responsibilities in production:
    - Ingests raw smart grid data (SCADA, IoT).
    - Normalizes data into a standard schema.
    - Correlates events across different sensors.
    """
    
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
