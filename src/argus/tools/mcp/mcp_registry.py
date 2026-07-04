"""Registry for MCP servers."""
from typing import Dict, List, Optional
import structlog
from argus.tools.mcp.base_mcp_server import BaseMCPServer

logger = structlog.get_logger("argus.tools.mcp.registry")

class MCPRegistry:
    """Manages configured MCP servers."""
    
    def __init__(self):
        self._servers: Dict[str, BaseMCPServer] = {}
        
    async def register_server(self, server: BaseMCPServer) -> None:
        """Register and initialize an MCP server."""
        await server.initialize()
        self._servers[server.name] = server
        logger.info("mcp_server_registered", name=server.name)
        
    def get_server(self, name: str) -> Optional[BaseMCPServer]:
        """Get an MCP server by name."""
        return self._servers.get(name)
        
    def list_servers(self) -> List[str]:
        """List all registered MCP servers."""
        return list(self._servers.keys())
        
    async def shutdown_all(self) -> None:
        """Shutdown all registered servers."""
        for name, server in self._servers.items():
            try:
                await server.shutdown()
                logger.info("mcp_server_shutdown", name=name)
            except Exception as e:
                logger.error("mcp_server_shutdown_failed", name=name, error=str(e))
        self._servers.clear()
