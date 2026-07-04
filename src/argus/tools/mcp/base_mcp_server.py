"""Base class for MCP servers."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseMCPServer(ABC):
    """Abstract interface for Model Context Protocol servers."""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize connection to MCP server."""

    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List tools provided by this server."""
        
    @abstractmethod
    async def call_tool(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool on the server."""
        
    @abstractmethod
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List resources available on this server."""
        
    @abstractmethod
    async def read_resource(self, uri: str) -> Any:
        """Read a resource's contents."""
        
    @abstractmethod
    async def shutdown(self) -> None:
        """Close connection to MCP server."""
