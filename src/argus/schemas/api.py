"""API response wrappers and common schemas."""
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""
    success: bool = Field(default=True)
    data: Optional[T] = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""
    items: List[T]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    """Standard error response."""
    code: str
    message: str
    details: Optional[dict] = None
