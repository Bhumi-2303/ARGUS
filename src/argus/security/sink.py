import httpx
import structlog
import asyncio
from typing import Dict, Any
from argus.security.audit import SecurityAuditEvent
from configs.settings import get_settings

logger = structlog.get_logger("argus.security.sink")

class AuditSink:
    """Provider-neutral audit sink to dispatch events to local logs and remote SIEM."""
    
    @staticmethod
    def dispatch(event: SecurityAuditEvent) -> None:
        """Synchronous wrapper to dispatch events."""
        # 1. Local Structured Logging (Resilient Local Auditability)
        event_dict = event.model_dump(exclude_none=True)
        logger.info("security_audit_event", **event_dict)
        
        # 2. Remote SIEM Dispatch (Fire and forget, resilient to failures)
        settings = get_settings().security
        if settings.siem_enabled and settings.siem_endpoint:
            # Dispatch asynchronously in background without blocking API
            try:
                loop = asyncio.get_running_loop()
                # Create a robust background task that handles retries
                loop.create_task(AuditSink._reliable_send_to_siem(
                    event_dict, 
                    settings.siem_endpoint, 
                    settings.siem_timeout_seconds
                ))
            except RuntimeError:
                # Fallback if no event loop is running (e.g. testing context or synchronous scripts)
                asyncio.run(AuditSink._reliable_send_to_siem(
                    event_dict, 
                    settings.siem_endpoint, 
                    settings.siem_timeout_seconds
                ))

    @staticmethod
    async def _reliable_send_to_siem(payload: Dict[str, Any], endpoint: str, timeout: int) -> None:
        """Async send to SIEM HEC or API with bounded retries and exponential backoff."""
        max_retries = 3
        base_backoff = 1.0
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.post(endpoint, json=payload)
                    
                    if response.status_code < 400:
                        return # Success
                    
                    # Log failure and decide whether to retry
                    logger.warning(
                        "siem_dispatch_failed", 
                        status_code=response.status_code, 
                        attempt=attempt+1
                    )
                    
                    if response.status_code < 500 and response.status_code != 429:
                        # 4xx errors (except Rate Limit) mean the payload or auth is bad.
                        # Retrying won't help. Drop and rely on the local log.
                        return
                        
            except Exception as e:
                logger.warning(
                    "siem_dispatch_error", 
                    error=str(e), 
                    attempt=attempt+1
                )
            
            # Wait before retry if we haven't exhausted attempts
            if attempt < max_retries - 1:
                await asyncio.sleep(base_backoff * (2 ** attempt))
                
        # If we reached here, delivery failed. 
        # Crucially, we do NOT crash the application.
        # The local log has already durably captured this event.
        logger.error("siem_dispatch_abandoned", event_id=payload.get("audit_event_id"))

