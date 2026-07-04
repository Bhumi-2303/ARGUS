"""Tool and tool execution schemas."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from argus.core.enums import ToolCategory


class ToolMetadata(BaseModel):
    """Metadata describing a tool's capabilities."""
    name: str
    version: str
    category: ToolCategory
    description: str
    parameters_schema: Dict[str, Any] = Field(default_factory=dict)


class ToolRequest(BaseModel):
    """A request to execute a tool."""
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    timeout: int = Field(default=60)


class ToolResult(BaseModel):
    """The result of a tool execution."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolPermission(BaseModel):
    """Permission required to use a tool."""
    tool_name: str
    required_role: str
