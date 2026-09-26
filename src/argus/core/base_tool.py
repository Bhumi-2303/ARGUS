"""Abstract base class for all ARGUS tools."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import structlog

from argus.core.enums import ToolCategory


class BaseTool(ABC):
    """Abstract interface that every tool must implement."""

    def __init__(self, tool_id: str, name: str, version: str, category: ToolCategory, 
                 description: str, required_permissions: List[str]):
        self.tool_id = tool_id
        self.name = name
        self.version = version
        self.category = category
        self.description = description
        self.required_permissions = required_permissions
        self.logger = structlog.get_logger("argus.tool").bind(
            tool_name=self.name
        )

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the tool."""

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool's function."""

    @abstractmethod
    async def validate(self, **kwargs: Any) -> bool:
        """Validate input arguments before execution."""

    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up tool resources."""

    def metadata(self) -> Dict[str, Any]:
        """Return the tool's metadata and capabilities schema."""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "description": self.description,
            "required_permissions": self.required_permissions
        }
