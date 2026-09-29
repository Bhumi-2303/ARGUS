"""Standardized error responses and global exception handlers.

Ensures internal exceptions, filesystem paths, stack traces, and environment details
are never leaked in API responses while securely logging them with correlation IDs.
"""

import uuid
from typing import Optional, Any
from fastapi import Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from structlog import get_logger

logger = get_logger("argus.security.errors")


def get_request_id(request: Request) -> str:
    """Extract or generate request correlation ID."""
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:12]}"


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle standard HTTPExceptions with a consistent error envelope."""
    request_id = get_request_id(request)
    headers = getattr(exc, "headers", None) or {}
    headers["X-Request-ID"] = request_id

    # If detail is already a dict, preserve it; otherwise format as message
    detail = exc.detail
    if isinstance(detail, dict):
        content = {
            "detail": detail,
            "error": "http_error",
            "request_id": request_id,
            **detail
        }
    else:
        content = {
            "detail": str(detail),
            "error": "http_error",
            "message": str(detail),
            "request_id": request_id
        }

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors safely."""
    request_id = get_request_id(request)
    logger.warning("request_validation_failed", path=request.url.path, errors=exc.errors(), request_id=request_id)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "message": "Invalid request parameters or payload.",
            "details": exc.errors(),
            "request_id": request_id
        },
        headers={"X-Request-ID": request_id}
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all unhandled exception handler that masks internal errors in production."""
    request_id = get_request_id(request)
    logger.error(
        "unhandled_server_exception",
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__,
        request_id=request_id,
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please contact the administrator with the correlation request ID.",
            "request_id": request_id
        },
        headers={"X-Request-ID": request_id}
    )
