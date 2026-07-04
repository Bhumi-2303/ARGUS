"""Main orchestrator implementation."""
import asyncio
import uuid
from typing import Dict, Any, Optional
import structlog

from argus.core.interfaces import IRegistry, IMessageBus
from argus.core.enums import TaskStatus, MessageType
from argus.schemas.tasks import TaskDefinition, TaskProgress, TaskCompletion
from argus.schemas.messages import TaskRequest, TaskResult
from argus.orchestrator.scheduler import PriorityScheduler
from argus.orchestrator.router import TaskRouter
from argus.orchestrator.dependency import DependencyResolver

logger = structlog.get_logger("argus.orchestrator")

class Orchestrator:
    """Manages task scheduling, routing, and lifecycle."""
    
    def __init__(self, registry: IRegistry, message_bus: IMessageBus):
        self.registry = registry
        self.bus = message_bus
        self.scheduler = PriorityScheduler()
        self.router = TaskRouter()
        self.dependency_resolver = DependencyResolver()
        
        self.tasks: Dict[str, Dict[str, Any]] = {} # task_id -> task details
        self._running = False
        self._loop_task: Optional[asyncio.Task] = None
        
    async def start(self) -> None:
        """Start the orchestrator."""
        self._running = True
        
        # Subscribe to relevant topics
        await self.bus.subscribe("task_results", self._handle_task_result)
        await self.bus.subscribe("task_progress", self._handle_task_progress)
        
        self._loop_task = asyncio.create_task(self._processing_loop())
        logger.info("orchestrator_started")
        
    async def stop(self) -> None:
        """Stop the orchestrator."""
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        logger.info("orchestrator_stopped")
        
    async def submit_task(self, task_def: TaskDefinition) -> str:
        """Submit a new task for execution."""
        task_id = str(uuid.uuid4())
        
        self.tasks[task_id] = {
            "definition": task_def,
            "status": TaskStatus.PENDING,
            "assigned_to": None,
            "result": None,
            "error": None
        }
        
        self.dependency_resolver.add_task(task_id, task_def.dependencies)
        
        if self.dependency_resolver.can_execute(task_id):
            self.scheduler.enqueue(task_id, task_def)
            self.tasks[task_id]["status"] = TaskStatus.SCHEDULED
            logger.info("task_scheduled", task_id=task_id)
        else:
            logger.info("task_pending_dependencies", task_id=task_id)
            
        return task_id
        
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or scheduled task."""
        if task_id not in self.tasks:
            return False
            
        task_info = self.tasks[task_id]
        if task_info["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False
            
        task_info["status"] = TaskStatus.CANCELLED
        self.scheduler.remove(task_id)
        logger.info("task_cancelled", task_id=task_id)
        return True
        
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task."""
        return self.tasks.get(task_id)
        
    async def _processing_loop(self) -> None:
        """Background loop to process scheduled tasks."""
        while self._running:
            try:
                if not self.scheduler.is_empty():
                    # Attempt to route the highest priority task
                    task_id, task_def = self.scheduler.peek()
                    
                    agent_id = await self.router.route(task_def, self.registry)
                    
                    if agent_id:
                        # We found an agent, dequeue and assign
                        self.scheduler.dequeue()
                        
                        self.tasks[task_id]["assigned_to"] = agent_id
                        self.tasks[task_id]["status"] = TaskStatus.RUNNING
                        
                        # Send task to agent
                        request = TaskRequest(
                            request_id=task_id,
                            trace_id=task_id,
                            agent_id="orchestrator",
                            priority=task_def.priority,
                            task_type=task_def.task_type,
                            payload=task_def.payload
                        )
                        await self.bus.publish(f"agent.{agent_id}.tasks", request)
                        logger.info("task_routed", task_id=task_id, agent_id=agent_id)
                    else:
                        # No capable agent available right now. Could implement backoff here.
                        pass
                        
            except Exception as e:
                logger.error("orchestrator_loop_error", error=str(e))
                
            await asyncio.sleep(1.0) # Check every second
            
    async def _handle_task_result(self, result: TaskCompletion) -> None:
        """Handle a completed task result from an agent."""
        task_id = result.task_id
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = result.status
            self.tasks[task_id]["result"] = result.result
            self.tasks[task_id]["error"] = result.error
            
            if result.status == TaskStatus.COMPLETED:
                self.dependency_resolver.mark_complete(task_id)
                self._check_pending_tasks()
                
            logger.info("task_completed", task_id=task_id, status=result.status)
            
    async def _handle_task_progress(self, progress: TaskProgress) -> None:
        """Handle progress updates from agents."""
        task_id = progress.task_id
        if task_id in self.tasks:
            # Could store progress history
            logger.debug("task_progress", task_id=task_id, pct=progress.progress_pct)
            
    def _check_pending_tasks(self) -> None:
        """Check if any pending tasks can now be scheduled."""
        for task_id, task_info in self.tasks.items():
            if task_info["status"] == TaskStatus.PENDING:
                if self.dependency_resolver.can_execute(task_id):
                    self.scheduler.enqueue(task_id, task_info["definition"])
                    task_info["status"] = TaskStatus.SCHEDULED
                    logger.info("task_scheduled_after_dependencies", task_id=task_id)
