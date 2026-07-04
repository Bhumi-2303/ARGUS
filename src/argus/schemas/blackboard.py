"""Blackboard schemas for shared memory."""
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from argus.core.enums import BlackboardSection


class BlackboardEntry(BaseModel):
    """A single entry in the blackboard."""
    section: BlackboardSection
    key: str
    value: Any
    version: int = Field(default=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    created_by: str


class SharedContext(BaseModel):
    """Snapshot of the shared context section."""
    context_data: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class SectionSnapshot(BaseModel):
    """Snapshot of an entire blackboard section."""
    section: BlackboardSection
    entries: Dict[str, BlackboardEntry] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
