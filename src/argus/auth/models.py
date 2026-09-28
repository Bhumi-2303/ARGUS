"""Data models for authentication and authorization."""

from typing import List, Set, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserPrincipal(BaseModel):
    """Authenticated user or service principal identity."""
    sub: str = Field(..., description="Unique subject identifier (user ID or client ID)")
    issuer: str = Field(..., description="Token issuer identifier")
    roles: List[str] = Field(default_factory=list, description="Assigned enterprise roles")
    permissions: Set[str] = Field(default_factory=set, description="Direct or derived granular permissions")
    email: Optional[str] = Field(None, description="Principal email address if available")
    client_id: Optional[str] = Field(None, description="OAuth2 client ID if available")
    claims: Dict[str, Any] = Field(default_factory=dict, description="Raw validated token claims")
    is_authenticated: bool = Field(True, description="Whether the principal is authenticated")

    def has_permission(self, permission: str) -> bool:
        """Check if principal holds a specific permission or wildcard admin authority."""
        if "admin:system" in self.permissions or "admin" in self.roles:
            return True
        return permission in self.permissions

    def has_any_permission(self, *permissions: str) -> bool:
        """Check if principal holds any of the specified permissions."""
        if "admin:system" in self.permissions or "admin" in self.roles:
            return True
        return any(p in self.permissions for p in permissions)

    def has_all_permissions(self, *permissions: str) -> bool:
        """Check if principal holds all of the specified permissions."""
        if "admin:system" in self.permissions or "admin" in self.roles:
            return True
        return all(p in self.permissions for p in permissions)

    def has_role(self, role: str) -> bool:
        """Check if principal is assigned a specific role."""
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        """Check if principal is assigned any of the specified roles."""
        return any(r in self.roles for r in roles)
