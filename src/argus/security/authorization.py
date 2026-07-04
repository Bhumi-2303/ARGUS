"""Authorization service using RBAC."""
import yaml
from typing import Callable, Any
from functools import wraps
from fastapi import Depends, HTTPException, status
from structlog import get_logger

from argus.security.auth import get_current_user
from argus.schemas.security import TokenPayload
from argus.core.exceptions import AuthorizationError

logger = get_logger("argus.security.authorization")


class RBACManager:
    def __init__(self, config_path: str = "config/security.yaml"):
        self.roles = {}
        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f)
                self.roles = data.get("roles", {})
        except Exception as e:
            logger.error("failed_to_load_roles", error=str(e))

    def check_permission(self, role: str, resource: str, action: str) -> bool:
        """Check if a role has permission to perform an action on a resource."""
        if role not in self.roles:
            return False
            
        permissions = self.roles[role].get("permissions", [])
        
        # Admin has full access
        if "*" in permissions:
            return True
            
        required_perm = f"{action}:{resource}"
        
        # Check explicit permission
        if required_perm in permissions:
            return True
            
        # Check wildcard action (e.g. read:*)
        if f"{action}:*" in permissions:
            return True
            
        return False


rbac = RBACManager()


def require_role(role: str) -> Callable:
    """FastAPI dependency to require a specific role."""
    def role_checker(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if user.role != role and user.role != "admin":
            logger.warning("unauthorized_role_access", user_id=user.sub, required_role=role, actual_role=user.role)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user
    return role_checker


def require_permission(resource: str, action: str) -> Callable:
    """FastAPI dependency to require a specific permission."""
    def permission_checker(user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not rbac.check_permission(user.role, resource, action):
            logger.warning("unauthorized_permission_access", user_id=user.sub, resource=resource, action=action)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return user
    return permission_checker
