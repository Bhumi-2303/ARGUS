"""Task router."""
from fastapi import APIRouter, Depends
from typing import List
from argus.schemas.tasks import TaskDefinition, TaskCompletion
from argus.schemas.api import APIResponse

router = APIRouter()

@router.post("/", response_model=APIResponse[str])
async def create_task(task: TaskDefinition):
    """Submit a new task to the orchestrator."""
    return APIResponse(data="task-id-placeholder")

@router.get("/{task_id}", response_model=APIResponse[TaskCompletion])
async def get_task(task_id: str):
    """Get the status/result of a task."""
    return APIResponse(data=None)
