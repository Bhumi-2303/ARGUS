"""Role-Based Access Control (RBAC) dependencies and permission enforcement."""

from typing import Set, Optional
from fastapi import Request, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from structlog import get_logger

from configs.settings import get_settings
from argus.auth.models import UserPrincipal
from argus.auth.jwt import jwt_validator, DEFAULT_ROLE_PERMISSIONS
from argus.security.audit import AuditLogger, SecurityAuditEvent

logger = get_logger("argus.auth.rbac")

security_bearer = HTTPBearer(auto_error=False)

# Authoritative set of system permissions
PERMISSIONS: Set[str] = {
    "read:domains",
    "read:models",
    "read:results",
    "run:prediction",
    "run:explanation",
    "run:onboarding",
    "read:telemetry",
    "read:agent-topology",
    "run:agent-trace",
    "read:monitoring",
    "read:incidents",
    "write:incidents",
    "approve:response",
    "admin:system",
}


def _get_dev_principal() -> UserPrincipal:
    """Generate default development principal for non-production environments."""
    all_perms = set(PERMISSIONS)
    return UserPrincipal(
        sub="dev-admin",
        issuer="argus-local-dev",
        roles=["admin"],
        permissions=all_perms,
        email="dev-admin@argus.local",
        is_authenticated=True,
    )


async def get_current_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    token_query: Optional[str] = Query(None, alias="token", description="Token for WebSocket or SSE stream authentication")
) -> UserPrincipal:
    """FastAPI dependency to extract and validate the current authenticated principal."""
    settings = get_settings()

    # Extract token from header or query parameter
    token = None
    if auth_header and auth_header.credentials:
        token = auth_header.credentials.strip()
    elif token_query:
        token = token_query.strip()
    elif "Authorization" in request.headers:
        raw_auth = request.headers["Authorization"].strip()
        if raw_auth.lower().startswith("bearer "):
            token = raw_auth[7:].strip()

    # If token is present, validate it
    if token:
        user = await jwt_validator.validate_token(token)
        request.state.user = user
        request.state.user_id = user.sub
        return user

    # If token is missing:
    # In production or when OIDC is enabled, FAIL CLOSED (HTTP 401)
    if settings.is_production or settings.security.oidc_enabled:
        AuditLogger.log_event(SecurityAuditEvent(
            actor_id="anonymous",
            actor_type="user",
            action="AUTHENTICATION_FAILURE",
            resource=request.url.path,
            outcome="UNAUTHORIZED",
            reason="Missing Authorization header in production mode",
            source_ip=request.client.host if request.client else None,
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required: Missing Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In development mode without OIDC: use dev principal
    dev_user = _get_dev_principal()
    request.state.user = dev_user
    request.state.user_id = dev_user.sub
    return dev_user


def require_permission(required_permission: str):
    """FastAPI dependency factory enforcing a specific granular permission."""
    async def permission_dependency(
        request: Request,
        user: UserPrincipal = Depends(get_current_user)
    ) -> UserPrincipal:
        if not user.has_permission(required_permission):
            AuditLogger.log_event(SecurityAuditEvent(
                actor_id=user.sub,
                actor_type="user",
                action="AUTHORIZATION_FAILURE",
                resource=request.url.path,
                outcome="FORBIDDEN",
                reason=f"User lacks required permission: '{required_permission}'",
                source_ip=request.client.host if request.client else None,
                authorization_context={
                    "required_permission": required_permission,
                    "user_roles": user.roles,
                    "user_permissions": list(user.permissions),
                }
            ))
            logger.warning(
                "permission_denied",
                user=user.sub,
                required_permission=required_permission,
                path=request.url.path
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Missing required permission '{required_permission}'.",
            )
        return user

    return permission_dependency


def require_roles(*allowed_roles: str):
    """FastAPI dependency factory enforcing that the user has at least one of the specified roles."""
    async def role_dependency(
        request: Request,
        user: UserPrincipal = Depends(get_current_user)
    ) -> UserPrincipal:
        if not user.has_any_role(*allowed_roles) and not user.has_role("admin"):
            AuditLogger.log_event(SecurityAuditEvent(
                actor_id=user.sub,
                actor_type="user",
                action="AUTHORIZATION_FAILURE",
                resource=request.url.path,
                outcome="FORBIDDEN",
                reason=f"User lacks required role. Allowed: {list(allowed_roles)}",
                source_ip=request.client.host if request.client else None,
                authorization_context={
                    "allowed_roles": list(allowed_roles),
                    "user_roles": user.roles,
                }
            ))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Requires one of roles: {', '.join(allowed_roles)}.",
            )
        return user

    return role_dependency
