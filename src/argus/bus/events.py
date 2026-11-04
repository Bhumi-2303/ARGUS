"""Typed event definitions for the ARGUS message bus."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union
import uuid
from pydantic import BaseModel, Field


class BusEvent(BaseModel):
    """Authoritative typed event representation for pub/sub messaging."""

    event_id: str = Field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:12]}")
    topic: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    source: Optional[str] = "system"
    priority: int = Field(default=0, ge=0, le=2)  # 0: normal, 1: high, 2: critical
    headers: Dict[str, str] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert BusEvent to dictionary."""
        return self.model_dump()

    @classmethod
    def from_message(
        cls,
        topic: str,
        message: Any,
        correlation_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> "BusEvent":
        """Normalize arbitrary inputs (dict, Pydantic model, EventMessage, or BusEvent) into BusEvent."""
        if isinstance(message, cls):
            return message

        custom_headers = headers or {}

        if hasattr(message, "model_dump"):
            payload = message.model_dump()
            event_id = getattr(message, "event_id", None) or f"evt-{uuid.uuid4().hex[:12]}"
            corr_id = correlation_id or getattr(message, "correlation_id", None)
            source = getattr(message, "source", "system")
            priority = getattr(message, "priority", 0)
            if hasattr(priority, "value"):
                priority = 1 if priority.value in ("high", "critical", 1, 2) else 0
            elif isinstance(priority, str):
                priority = 1 if priority.lower() in ("high", "critical") else 0
            return cls(
                event_id=event_id,
                topic=topic,
                payload=payload,
                correlation_id=corr_id,
                source=source,
                priority=int(priority),
                headers=custom_headers,
            )

        if isinstance(message, dict):
            event_id = message.get("event_id") or f"evt-{uuid.uuid4().hex[:12]}"
            corr_id = correlation_id or message.get("correlation_id")
            source = message.get("source", "system")
            priority = message.get("priority", 0)
            merged_headers = dict(custom_headers)
            if "headers" in message and isinstance(message["headers"], dict):
                merged_headers.update(message["headers"])
            return cls(
                event_id=str(event_id),
                topic=topic,
                payload=message,
                correlation_id=str(corr_id) if corr_id else None,
                source=str(source),
                priority=int(priority) if isinstance(priority, (int, float)) else 0,
                headers=merged_headers,
            )

        # Fallback for scalar/string
        return cls(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            topic=topic,
            payload={"message": str(message)},
            correlation_id=correlation_id,
            headers=custom_headers,
        )
