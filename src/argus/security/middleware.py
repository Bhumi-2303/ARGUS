"""Security middleware for FastAPI."""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from structlog import get_logger

from config.settings import get_settings
from argus.security.rate_limiter import rate_limiter
from argus.security.audit import AuditLogger

logger = get_logger("argus.security.middleware")

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware handling rate limiting and audit logging."""
    
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        
        # Rate Limiting
        if settings.features.rate_limiting:
            # Use client IP as the key for simplicity. In prod, might use authenticated user ID
            client_ip = request.client.host if request.client else "unknown"
            
            allowed, _, _ = rate_limiter.check_rate_limit(
                key=client_ip,
                max_requests=settings.security.rate_limit_requests,
                window_seconds=settings.security.rate_limit_window_seconds
            )
            
            if not allowed:
                logger.warning("rate_limit_exceeded", ip=client_ip, path=request.url.path)
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too Many Requests", "message": "Rate limit exceeded"}
                )

        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Audit Logging for modifying requests
            if settings.features.audit_logging and request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                # Attempt to get user from request state if authentication middleware set it
                actor = getattr(request.state, "user_id", "anonymous")
                AuditLogger.log(
                    actor=actor,
                    action=request.method,
                    resource=request.url.path,
                    outcome=f"HTTP {response.status_code}",
                    details=f"Process time: {process_time:.4f}s",
                    ip_address=request.client.host if request.client else "unknown"
                )
                
            return response
            
        except Exception as e:
            logger.error("request_failed", error=str(e), path=request.url.path)
            # You might want to log failed requests to audit log here as well
            raise
