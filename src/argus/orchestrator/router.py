"""Task router to find capable agents."""
from typing import Optional
import structlog
from argus.schemas.tasks import TaskDefinition
from argus.core.interfaces import IRegistry
from argus.core.exceptions import RoutingError

logger = structlog.get_logger("argus.orchestrator.router")

class TaskRouter:
    """Routes tasks to capable agents."""
    
    async def route(self, task: TaskDefinition, registry: IRegistry) -> Optional[str]:
        """Find the best agent for a given task."""
        if not task.required_capabilities:
            logger.warning("task_no_capabilities_required", task_type=task.task_type)
            return None
            
        capable_agents = []
        for cap in task.required_capabilities:
            agents = await registry.find_by_capability(cap)
            if not agents:
                logger.error("no_agent_for_capability", capability=cap)
                return None
                
            if not capable_agents:
                capable_agents = list(agents)
            else:
                # Find intersection of agents that have ALL required capabilities
                capable_agents = [a for a in capable_agents if a in agents]
                
        if not capable_agents:
            logger.error("no_agent_meets_all_requirements", requirements=task.required_capabilities)
            return None
            
        # Basic load balancing: select the first available agent (could be enhanced to check actual load)
        # Assuming registry returns agent IDs
        selected_agent = capable_agents[0]
        logger.debug("task_routed", task_type=task.task_type, agent_id=selected_agent)
        return selected_agent
