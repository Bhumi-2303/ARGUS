"""Critical Asset Analyzer tool for Risk Prediction Agent."""
from typing import Any, Dict
import structlog

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.risk_prediction.models.schemas import (
    RiskAnalysisInput, CriticalityResult, AssetPriority
)

class CriticalAssetAnalyzer(BaseTool):
    """Analyzes the knowledge context to determine the priority of affected assets."""

    def __init__(self):
        super().__init__(
            tool_id="rp_critical_asset_analyzer",
            name="Critical Asset Analyzer",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Evaluates asset criticality based on knowledge graph context.",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.critical_asset_analyzer")

        # Heuristic mapping for rule-based analysis (future: graph ML)
        self._critical_types = {"ics_controller", "scada_server", "historian"}
        self._high_types = {"hmi", "engineering_workstation"}

    async def initialize(self) -> None:
        """Initialize the analyzer."""
        self.logger.info("critical_asset_analyzer_initialized")

    async def validate(self, input_data: RiskAnalysisInput) -> bool:
        """Validate input."""
        if not input_data or not input_data.knowledge_event:
            return False
        return True

    async def execute(self, input_data: RiskAnalysisInput) -> CriticalityResult:
        """Calculate asset criticality."""
        if not await self.validate(input_data):
            raise ValueError("Invalid input for CriticalAssetAnalyzer")

        knowledge = input_data.knowledge_event
        affected = knowledge.affected_assets
        asset_types = knowledge.asset_types
        
        if not affected:
            return CriticalityResult(
                asset_priority=None,
                critical_assets=[],
                reasoning="No affected assets identified in knowledge context; criticality unavailable."
            )
            
        highest_priority = AssetPriority.LOW
        critical_assets = []
        
        # Simple rule-based evaluation based on asset types
        for asset in affected:
            atype = asset_types.get(asset, "unknown").lower()
            
            if atype in self._critical_types:
                highest_priority = AssetPriority.CRITICAL
                critical_assets.append(asset)
            elif atype in self._high_types and highest_priority != AssetPriority.CRITICAL:
                highest_priority = AssetPriority.HIGH
                critical_assets.append(asset)
            elif highest_priority in (AssetPriority.LOW, AssetPriority.MEDIUM):
                if highest_priority == AssetPriority.LOW:
                    highest_priority = AssetPriority.MEDIUM
                critical_assets.append(asset)

        reasoning = f"Evaluated {len(affected)} assets. Determined highest priority is {highest_priority.value.upper()} based on types."

        self.logger.info("asset_criticality_calculated", priority=highest_priority.value)
        return CriticalityResult(
            asset_priority=highest_priority,
            critical_assets=critical_assets,
            reasoning=reasoning
        )

    async def shutdown(self) -> None:
        """Clean up."""
        pass
