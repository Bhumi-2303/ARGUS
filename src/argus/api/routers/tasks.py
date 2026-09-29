"""Task router."""
from fastapi import APIRouter, HTTPException, status
from argus.schemas.tasks import TaskDefinition, TaskCompletion
from argus.schemas.api import APIResponse

router = APIRouter()

@router.post("/", response_model=APIResponse[str])
async def create_task(task: TaskDefinition):
    """Submit a new task to the orchestrator."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Async task submission not implemented in demo.")

@router.get("/{task_id}", response_model=APIResponse[TaskCompletion])
async def get_task(task_id: str):
    """Get the status/result of a task."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Async task tracking not implemented in demo.")
