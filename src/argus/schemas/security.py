"""Security, authentication, and authorization schemas."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Payload data for a JSON Web Token."""
    sub: str = Field(..., description="Subject (usually user or agent ID)")
    role: str = Field(..., description="Assigned role")
    exp: Optional[int] = Field(default=None, description="Expiration time")
    iat: Optional[int] = Field(default=None, description="Issued at time")
    jti: Optional[str] = Field(default=None, description="JWT ID")


class TokenResponse(BaseModel):
    """Response returned upon successful authentication."""
    access_token: str
    token_type: str = Field(default="bearer")
    expires_in: int


class Permission(BaseModel):
    """A granular permission."""
    resource: str
    action: str


class Role(BaseModel):
    """A role with a set of permissions."""
    name: str
    permissions: List[str] = Field(default_factory=list)


class AuditEntry(BaseModel):
    """An entry in the audit log."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor: str
    action: str
    resource: str
    outcome: str
    details: str
    ip_address: Optional[str] = None
