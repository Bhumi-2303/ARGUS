"""Security middleware for FastAPI.

Provides correlation ID tracing, trusted proxy client IP resolution,
multi-tier rate limiting, payload size enforcement, and audit logging.
"""

import time
import uuid
from typing import Optional, List
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from structlog import get_logger

from configs.settings import get_settings
from argus.security.rate_limiter import rate_limiter
from argus.security.audit import AuditLogger, SecurityAuditEvent

logger = get_logger("argus.security.middleware")

MAX_PAYLOAD_BYTES = 1024 * 1024  # 1 MB

# Expensive endpoints subject to tighter rate limits
EXPENSIVE_ROUTES = {
    "/api/v1/predict",
    "/api/v1/explain",
    "/api/v1/onboard",
    "/api/v1/agents/trace",
}


def resolve_client_ip(request: Request, trusted_proxies: List[str]) -> str:
    """Resolve client IP safely, only honoring X-Forwarded-For from trusted reverse proxies."""
    client_host = request.client.host if request.client else "unknown"

    # Only inspect X-Forwarded-For if direct connection is from a trusted proxy
    if client_host in trusted_proxies and "x-forwarded-for" in request.headers:
        forwarded = [ip.strip() for ip in request.headers["x-forwarded-for"].split(",") if ip.strip()]
        if forwarded:
            return forwarded[0]

    return client_host


class SecurityMiddleware(BaseHTTPMiddleware):
    """Unified security middleware handling correlation IDs, rate limiting, and audit logging."""

    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()

        # 1. Attach Request Correlation ID
        request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:12]}"
        request.state.request_id = request_id

        # 2. Resolve Client IP safely
        client_ip = resolve_client_ip(request, settings.security.trusted_proxies)
        request.state.client_ip = client_ip

        # 3. Payload size check on mutating methods
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_PAYLOAD_BYTES:
                logger.warning("payload_too_large", ip=client_ip, size=content_length, path=request.url.path)
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "payload_too_large",
                        "message": f"Payload size exceeds maximum limit of {MAX_PAYLOAD_BYTES} bytes.",
                        "request_id": request_id
                    },
                    headers={"X-Request-ID": request_id}
                )

        # 4. Rate Limiting
        if settings.features.rate_limiting and not request.url.path.startswith("/health"):
            actor_id = getattr(request.state, "user_id", None)
            rate_key = f"user:{actor_id}" if actor_id else f"ip:{client_ip}"

            # Determine limit based on endpoint sensitivity
            if request.url.path in EXPENSIVE_ROUTES:
                max_req = settings.security.rate_limit_per_minute_inference
            elif actor_id:
                max_req = settings.security.rate_limit_per_minute_authenticated
            else:
                max_req = settings.security.rate_limit_per_minute_public

            allowed, remaining, reset_time = rate_limiter.check_rate_limit(
                key=f"{rate_key}:{request.url.path}",
                max_requests=max_req,
                window_seconds=60
            )

            if not allowed:
                logger.warning(
                    "rate_limit_exceeded",
                    rate_key=rate_key,
                    path=request.url.path,
                    request_id=request_id
                )
                retry_after = max(1, int(reset_time - time.time()))
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                        "request_id": request_id
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-Request-ID": request_id
                    }
                )

        # 5. Process Request
        start_time = time.time()
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            process_time = time.time() - start_time
            # Inject X-Request-ID on outgoing response
            if "response" in locals() and response is not None:
                response.headers["X-Request-ID"] = request_id

            # Audit logging for mutating actions
            if settings.features.audit_logging and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                actor = getattr(request.state, "user_id", "anonymous")
                AuditLogger.log_event(SecurityAuditEvent(
                    actor_id=actor,
                    action=request.method,
                    resource=request.url.path,
                    outcome=f"HTTP {status_code}",
                    reason=f"Process time: {process_time:.4f}s",
                    source_ip=client_ip,
                    correlation_id=request_id
                ))

        return response
