"""Agent registry implementation."""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
import structlog

from argus.schemas.agents import AgentRegistration, AgentHealthReport
from argus.core.enums import AgentStatus

logger = structlog.get_logger("argus.registry")

class AgentRegistry:
    """Manages discovery and lifecycle of agents."""
    
    def __init__(self):
        self._agents: Dict[str, AgentRegistration] = {}
        self._health: Dict[str, AgentHealthReport] = {}
        self._load: Dict[str, int] = {}
        self._lock = asyncio.Lock()
        
    async def register(self, agent: AgentRegistration) -> None:
        """Register a new agent."""
        async with self._lock:
            self._agents[agent.agent_id] = agent
            self._load[agent.agent_id] = 0
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
                
    async def update_load(self, agent_id: str, current_tasks: int) -> None:
        """Update the current load (number of tasks) for an agent."""
        async with self._lock:
            if agent_id in self._agents:
                self._load[agent_id] = current_tasks
                
    async def check_heartbeats(self, timeout_seconds: int = 60) -> None:
        """Check for agents that haven't sent a heartbeat recently."""
        now = datetime.now(timezone.utc)
        async with self._lock:
            for agent_id, health in self._health.items():
                if health.status != AgentStatus.ERROR:
                    delta = (now - health.last_heartbeat).total_seconds()
                    if delta > timeout_seconds:
                        logger.error("agent_heartbeat_timeout", agent_id=agent_id, timeout_seconds=timeout_seconds)
                        health.status = AgentStatus.ERROR
                        health.error_message = f"Heartbeat timeout (last seen {delta}s ago)"
