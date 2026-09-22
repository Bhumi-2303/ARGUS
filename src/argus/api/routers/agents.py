"""Agent router."""
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from argus.schemas.agents import AgentHealthReport, AgentRegistration
from argus.schemas.api import APIResponse

router = APIRouter()

@router.get("/", response_model=APIResponse[List[AgentRegistration]])
async def list_agents():
    """List all registered agents."""
    return APIResponse(data=[])

@router.get("/{agent_id}/health", response_model=APIResponse[AgentHealthReport])
async def get_agent_health(agent_id: str):
    """Get the health status of a specific agent."""
    return APIResponse(data=None)
