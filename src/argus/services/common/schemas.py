"""Shared Pydantic schemas used across ARGUS microservices."""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

class FlowRecord(BaseModel):
    """4-tuple flow record for SCADA telemetry."""
    pkt_mean_to_max: float = Field(..., description="Ratio of mean packet length to max packet length [0,1]")
    tcp_flag_density: float = Field(..., description="TCP flag multiplicity count")
    log_pkt_mean: float = Field(..., description="Log-transformed mean packet length")
    log_pkt_max: float = Field(..., description="Log-transformed max packet length")

    model_config = {
        "json_schema_extra": {
            "example": {
                "pkt_mean_to_max": 0.95,
                "tcp_flag_density": 1.0,
                "log_pkt_mean": 4.2,
                "log_pkt_max": 4.3
            }
        }
    }

class AgentMessage(BaseModel):
    """Shared message schema for agent-to-agent communication."""
    message_id: str = Field(..., description="Unique message identifier")
    event_id: str = Field(..., description="Unique event identifier linking a full request trace")
    sender: str = Field(..., description="Agent ID of the sender")
    receiver: str = Field(..., description="Agent ID of the receiver")
    message_type: str = Field(..., description="Type of message (e.g. 'request', 'response', 'review_request')")
    payload: Dict[str, Any] = Field(..., description="The main data being passed")
    confidence: Optional[float] = Field(None, description="Confidence score if applicable")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Reasoning or evidence for the payload")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trace_id: str = Field(..., description="Trace ID for observability")
