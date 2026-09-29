"""Playbook Selector tool for Decision Support Agent."""
import structlog
from typing import List

from argus.core.base_tool import BaseTool
from argus.core.enums import ToolCategory
from argus.agents.decision_support.models.schemas import DecisionAnalysisInput, Playbook

class PlaybookSelector(BaseTool):
    """Selects applicable response playbooks based on the risk event."""

    def __init__(self):
        super().__init__(
            tool_id="ds_playbook_selector",
            name="Playbook Selector",
            version="1.0.0",
            category=ToolCategory.UTILITY,
            description="Selects applicable standard operating procedures (SOPs).",
            required_permissions=[]
        )
        self.logger = structlog.get_logger("argus.tool.playbook_selector")

    async def initialize(self) -> None:
        """Initialize the selector."""
        self.logger.info("playbook_selector_initialized")

    async def validate(self, input_data: DecisionAnalysisInput) -> bool:
        """Validate inputs."""
        if not input_data or not input_data.risk_event:
            return False
        return True

    async def execute(self, input_data: DecisionAnalysisInput) -> List[Playbook]:
        """Select applicable playbooks."""
        if not await self.validate(input_data):
            raise ValueError("Invalid input for PlaybookSelector")

        severity = input_data.risk_event.severity.upper() if input_data.risk_event.severity else "UNKNOWN"
        assets = input_data.knowledge_event.affected_assets
        vulns = input_data.knowledge_event.known_vulnerabilities

        playbooks = []
        
        # Rule 1: High/Critical severity requires containment
        if severity in ("HIGH", "CRITICAL"):
            playbooks.append(Playbook(
                playbook_id="SOP-CONTAIN-01",
                name="Critical Network Containment",
                description="Standard operating procedure for isolating compromised critical assets.",
                applicable_assets=assets
            ))
            
        # Rule 2: Presence of vulnerabilities requires patching/mitigation
        if vulns:
            playbooks.append(Playbook(
                playbook_id="SOP-PATCH-02",
                name="Vulnerability Mitigation",
                description="Emergency procedure for applying patches or compensating controls.",
                applicable_assets=assets
            ))
            
        # Fallback playbook
        if not playbooks:
            playbooks.append(Playbook(
                playbook_id="SOP-MONITOR-01",
                name="Enhanced Monitoring",
                description="Procedure for increasing telemetry and alerting thresholds.",
                applicable_assets=assets
            ))

        self.logger.info("playbooks_selected", count=len(playbooks))
        return playbooks

    async def shutdown(self) -> None:
        """Clean up."""
        pass
