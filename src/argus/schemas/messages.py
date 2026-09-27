"""Message schemas for inter-component communication."""
from typing import Any, Dict, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from argus.core.enums import MessageType, TaskPriority


class BaseMessage(BaseModel):
    """Base class for all messages in the system."""
    request_id: str = Field(..., description="Unique request identifier")
    trace_id: str = Field(..., description="Distributed trace ID")
    agent_id: str = Field(..., description="Source agent identifier")
    timestamp: datetime = Field(..., description="UTC timestamp")
    priority: TaskPriority = Field(..., description="Message priority")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    signature: Optional[str] = Field(default=None, description="HMAC signature")
    version: str = Field(default="1.0.0", description="Protocol version")
    implementation_status: str = Field(default="verified", description="Status of the logic: verified or not_implemented")


class AgentMessage(BaseMessage):
    """Message sent between agents (via orchestrator/blackboard)."""
    target_agent_id: Optional[str] = Field(default=None, description="Optional target agent")


class EventMessage(BaseMessage):
    """System event broadcast message."""
    event_type: str = Field(..., description="Type of event")


class FeatureEvent(EventMessage):
    """Standardized feature event produced by the Data Intelligence Agent.
    
    This is the ONLY message type the DIA publishes. Downstream agents
    (Threat Analysis, Risk Prediction) consume these events.
    """
    source_file: str = Field(..., description="Origin CSV/Parquet filename")
    chunk_index: int = Field(..., description="Chunk sequence number within the file")
    records_processed: int = Field(..., description="Number of records in this chunk")
    records_dropped: int = Field(default=0, description="Records dropped during cleaning")
    feature_names: List[str] = Field(..., description="Ordered list of feature column names")
    feature_stats: Dict[str, Any] = Field(
        default_factory=dict,
        description="Per-feature statistics (min, max, mean, std, nulls)"
    )
    normalization_method: str = Field(
        default="min_max",
        description="Normalization method applied (min_max or z_score)"
    )
    processing_duration_ms: float = Field(..., description="Pipeline processing time in ms")


class ThreatEvent(EventMessage):
    """Event detailing a detected threat in the smart grid network."""
    attack_type: str = Field(..., description="Classification of attack (e.g. brute_force, dos)")
    source_ip: Optional[str] = Field(None, description="Source IP of attack")
    dest_ip: Optional[str] = Field(None, description="Target IP of attack")
    mitre_technique_id: Optional[str] = Field(None, description="Associated MITRE technique ID")
    cve_id: Optional[str] = Field(None, description="Associated CVE ID")
    severity: float = Field(..., description="Attack severity score from 0 to 1")
    description: str = Field(..., description="Detailed threat payload information")


class KnowledgeEvent(EventMessage):
    """Enriched security event populated with threat intelligence context."""
    attack_context: Dict[str, Any] = Field(..., description="Summary details about the attack category")
    mitre_techniques: List[Dict[str, Any]] = Field(default_factory=list, description="MITRE ATT&CK records")
    cves: List[Dict[str, Any]] = Field(default_factory=list, description="CVE vulnerability details")
    cisa_advisories: List[Dict[str, Any]] = Field(default_factory=list, description="CISA ICS Advisories")
    recommended_mitigations: List[str] = Field(default_factory=list, description="Consolidated mitigation actions")
    references: List[str] = Field(default_factory=list, description="External citation links")
    confidence: float = Field(..., description="Confidence score of the enrichment (0.0 to 1.0)")
    processing_metadata: Dict[str, Any] = Field(..., description="Execution logs, pipeline time, sources searched")


class ResponseMessage(BaseMessage):

    """Response to a previous message."""
    in_response_to: str = Field(..., description="Request ID of the original message")


class Heartbeat(BaseMessage):
    """Agent heartbeat message."""
    status: str = Field(..., description="Current agent status")


class TaskRequest(BaseMessage):
    """Request to execute a task."""
    task_type: str = Field(..., description="Type of task to execute")


class TaskResult(BaseMessage):
    """Result of a task execution."""
    task_id: str = Field(..., description="ID of the completed task")
    success: bool = Field(..., description="Whether the task succeeded")


class StatusUpdate(BaseMessage):
    """Update on the status of an ongoing task."""
    task_id: str = Field(..., description="ID of the task")
    progress: float = Field(..., description="Progress percentage (0-100)")


class Alert(BaseMessage):
    """Security or system alert."""
    severity: str = Field(..., description="Alert severity (e.g., critical, warning)")
    description: str = Field(..., description="Alert description")
