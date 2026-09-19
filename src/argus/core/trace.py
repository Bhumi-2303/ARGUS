from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class TraceStep(BaseModel):
    """Represents a single step in the execution trace."""
    stage: str = Field(..., description="Stage name (e.g. DETECTED, RISK_ASSESSED)")
    component: str = Field(..., description="Name of the component executing the stage")
    status: str = Field(..., description="Status: SUCCESS, FAILED, TIMEOUT, PARTIAL")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    input_reference: Optional[str] = None
    output_reference: Optional[str] = None
    model_version: Optional[str] = None
    policy_version: Optional[str] = None
    error: Optional[str] = None

class ExecutionTrace(BaseModel):
    """Full execution trace of an event through the pipeline."""
    event_id: str
    steps: List[TraceStep] = Field(default_factory=list)
    
    def add_step(self, step: TraceStep):
        self.steps.append(step)
