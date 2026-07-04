"""Audit logging utility."""
import structlog
from datetime import datetime, timezone
from typing import Optional

logger = structlog.get_logger("argus.audit")

class AuditLogger:
    """Handles structured audit logging."""
    
    @staticmethod
    def log(actor: str, action: str, resource: str, outcome: str, details: str, ip_address: Optional[str] = None) -> None:
        """Log an audit event."""
        logger.info(
            "audit_event",
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor=actor,
            action=action,
            resource=resource,
            outcome=outcome,
            details=details,
            ip_address=ip_address
        )
