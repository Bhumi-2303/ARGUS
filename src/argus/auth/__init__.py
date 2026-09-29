"""ARGUS Authentication & Authorization module.

Provides production-ready OIDC/OAuth2 JWT validation, JWKS caching and key rotation,
and fine-grained Role-Based Access Control (RBAC).
"""

from argus.auth.models import UserPrincipal
from argus.auth.rbac import get_current_user, require_permission, require_roles, PERMISSIONS

__all__ = [
    "UserPrincipal",
    "get_current_user",
    "require_permission",
    "require_roles",
    "PERMISSIONS",
]
