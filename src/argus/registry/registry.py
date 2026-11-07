"""Agent registry implementation for discovery, health monitoring, and lifecycle tracking."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional
import structlog

from argus.core.enums import AgentStatus
from argus.schemas.agents import AgentHealthReport, AgentRegistration

logger = structlog.get_logger("argus.registry")


class AgentRegistry:
    """Manages discovery and lifecycle of agents."""

    def __init__(self):
        self._agents: Dict[str, AgentRegistration] = {}
        self._health: Dict[str, AgentHealthReport] = {}
        self._load: Dict[str, int] = {}
        self._lock_obj: Optional[asyncio.Lock] = None

    @property
    def _lock(self) -> asyncio.Lock:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None
        if self._lock_obj is None or (
            current_loop and getattr(self._lock_obj, "_loop", None) not in (None, current_loop)
        ):
            self._lock_obj = asyncio.Lock()
        return self._lock_obj

    async def register(self, agent: AgentRegistration) -> None:
        """Register a new agent."""
        async with self._lock:
            self._agents[agent.agent_id] = agent
            self._load[agent.agent_id] = 0
            if agent.agent_id not in self._health:
                self._health[agent.agent_id] = AgentHealthReport(
                    agent_id=agent.agent_id,
                    status=getattr(agent, "status", AgentStatus.READY),
                    uptime=0.0,
                    tasks_completed=0,
                    tasks_failed=0,
                    memory_usage_mb=0.0,
                    last_heartbeat=datetime.now(timezone.utc),
                )
            logger.info("agent_registered", agent_id=agent.agent_id, name=agent.name)

    async def deregister(self, agent_id: str) -> None:
        """Deregister an agent."""
        async with self._lock:
            if agent_id in self._agents:
                del self._agents[agent_id]
                self._health.pop(agent_id, None)
                self._load.pop(agent_id, None)
                logger.info("agent_deregistered", agent_id=agent_id)

    async def get(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get agent registration by ID."""
        async with self._lock:
            return self._agents.get(agent_id)

    async def get_all(self) -> List[AgentRegistration]:
        """Get all registered agents."""
        async with self._lock:
            return list(self._agents.values())

    async def find_by_capability(self, capability: str) -> List[str]:
        """Find IDs of all agents with a specific capability."""
        async with self._lock:
            return [
                agent.agent_id
                for agent in self._agents.values()
                if capability in agent.capabilities
            ]

    async def update_health(self, agent_id: str, health: AgentHealthReport) -> None:
        """Update the health status of an agent."""
        async with self._lock:
            if agent_id in self._agents:
                self._health[agent_id] = health
                logger.debug("health_updated", agent_id=agent_id, status=health.status)

    async def get_health(self, agent_id: str) -> Optional[AgentHealthReport]:
        """Get the current health report of an agent."""
        async with self._lock:
            return self._health.get(agent_id)

    async def update_load(self, agent_id: str, current_tasks: int) -> None:
        """Update the current load (number of tasks) for an agent."""
        async with self._lock:
            if agent_id in self._agents:
                self._load[agent_id] = current_tasks

    async def get_load(self, agent_id: str) -> int:
        """Get the current task count for an agent."""
        async with self._lock:
            return self._load.get(agent_id, 0)

    async def check_heartbeats(self, timeout_seconds: int = 60) -> None:
        """Check for agents that haven't sent a heartbeat recently."""
        now = datetime.now(timezone.utc)
        async with self._lock:
            for agent_id, health in self._health.items():
                if health.status != AgentStatus.ERROR:
                    delta = (now - health.last_heartbeat).total_seconds()
                    if delta > timeout_seconds:
                        logger.error(
                            "agent_heartbeat_timeout",
                            agent_id=agent_id,
                            timeout_seconds=timeout_seconds,
                        )
                        health.status = AgentStatus.ERROR
                        health.error_message = f"Heartbeat timeout (last seen {delta:.1f}s ago)"

    async def discover_builtin_agents(self) -> List[AgentRegistration]:
        """Register the standard ARGUS 6-agent autonomous pipeline definitions."""
        builtin_definitions = [
            AgentRegistration(
                agent_id="agent_dia",
                name="Data Intelligence Agent",
                version="1.0.0",
                description="Normalizes raw telemetry into 4 harmonized flow features",
                capabilities=["telemetry_normalization", "feature_extraction"],
                permissions=["read:telemetry"],
                tools=["feature_extractor", "protocol_validator"],
                status=AgentStatus.READY,
            ),
            AgentRegistration(
                agent_id="agent_taa",
                name="Threat Analysis Agent",
                version="1.0.0",
                description="Executes LightGBM / XGBoost cross-domain threat inference",
                capabilities=["threat_detection", "classification"],
                permissions=["run:prediction"],
                tools=["model_inference", "threshold_calibrator"],
                status=AgentStatus.READY,
            ),
            AgentRegistration(
                agent_id="agent_ea",
                name="Explainability Agent",
                version="1.0.0",
                description="Generates local TreeSHAP attribution and feature rankings",
                capabilities=["shap_attribution", "explainability"],
                permissions=["run:explanation"],
                tools=["tree_shap_explainer"],
                status=AgentStatus.READY,
            ),
            AgentRegistration(
                agent_id="agent_kca",
                name="Knowledge Context Agent",
                version="1.0.0",
                description="Correlates alerts with ICS asset topologies and MITRE ATT&CK",
                capabilities=["threat_enrichment", "mitre_correlation"],
                permissions=["read:topology"],
                tools=["topology_query", "cve_matcher"],
                status=AgentStatus.READY,
            ),
            AgentRegistration(
                agent_id="agent_rpa",
                name="Risk Prediction Agent",
                version="1.0.0",
                description="Calculates asset impact, risk scores, and severity tiers",
                capabilities=["risk_scoring", "impact_analysis"],
                permissions=["calculate:risk"],
                tools=["asset_criticality_evaluator"],
                status=AgentStatus.READY,
            ),
            AgentRegistration(
                agent_id="agent_dsa",
                name="Decision Support Agent",
                version="1.0.0",
                description="Synthesizes response plans and generates HITL approval requirements",
                capabilities=["action_recommendation", "hitl_approval_dispatch"],
                permissions=["approve:response", "write:decisions"],
                tools=["approval_generator", "sop_matcher"],
                status=AgentStatus.READY,
            ),
        ]

        for reg in builtin_definitions:
            await self.register(reg)

        return builtin_definitions

    async def clear(self) -> None:
        """Clear all registered agents and health entries."""
        async with self._lock:
            self._agents.clear()
            self._health.clear()
            self._load.clear()
