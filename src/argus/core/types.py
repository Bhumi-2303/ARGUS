"""Core type aliases for ARGUS platform."""
from typing import Any, Dict, TypeAlias, NewType

AgentId = NewType("AgentId", str)
TaskId = NewType("TaskId", str)
TraceId = NewType("TraceId", str)
RequestId = NewType("RequestId", str)

Payload: TypeAlias = Dict[str, Any]
Metadata: TypeAlias = Dict[str, Any]
