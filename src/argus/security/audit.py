"""Audit logging utility."""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class SecurityAuditEvent(BaseModel):
    audit_event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    actor_id: str
    actor_type: str = "user"
    action: str
    resource: str
    resource_id: Optional[str] = None
    outcome: str
    reason: Optional[str] = None
    source_ip: Optional[str] = None
    event_id: Optional[str] = None
    incident_id: Optional[str] = None
    correlation_id: Optional[str] = None
    authorization_context: Dict[str, Any] = Field(default_factory=dict)
    service: str = "argus-api"
    schema_version: str = "1.0"


class AuditLogger:
    """Handles structured audit logging."""
    
    @staticmethod
    def log_event(event: SecurityAuditEvent) -> None:
        """Log a structured security audit event."""
        # Delayed import to avoid circular dependency
        from argus.security.sink import AuditSink
        AuditSink.dispatch(event)

    @staticmethod
    def log(actor: str, action: str, resource: str, outcome: str, details: str, ip_address: Optional[str] = None, resource_id: Optional[str] = None) -> None:
        """Legacy method wrapper for backwards compatibility."""
        event = SecurityAuditEvent(
            actor_id=actor,
            action=action,
            resource=resource,
            resource_id=resource_id,
            outcome=outcome,
            reason=details,
            source_ip=ip_address
        )
        AuditLogger.log_event(event)
