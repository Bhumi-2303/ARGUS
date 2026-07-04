"""Tool registry implementation."""
import asyncio
from typing import Dict, List, Optional, Any
import structlog
from argus.core.base_tool import BaseTool
from argus.core.interfaces import ISecurityProvider

logger = structlog.get_logger("argus.tools.registry")

class ToolRegistry:
    """Manages available tools and access control."""
    
    def __init__(self, security_provider: ISecurityProvider):
        self._tools: Dict[str, BaseTool] = {}
        self.security = security_provider
        self._lock = asyncio.Lock()
        
    async def register(self, tool: BaseTool) -> None:
        """Register a new tool."""
        async with self._lock:
            await tool.initialize()
            self._tools[tool.name] = tool
            logger.info("tool_registered", tool_name=tool.name, category=tool.category)
            
    async def deregister(self, tool_name: str) -> None:
        """Deregister and shutdown a tool."""
        async with self._lock:
            if tool_name in self._tools:
                tool = self._tools[tool_name]
                await tool.shutdown()
                del self._tools[tool_name]
                logger.info("tool_deregistered", tool_name=tool_name)
                
    async def get(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        async with self._lock:
            return self._tools.get(tool_name)
            
    async def get_all(self) -> List[BaseTool]:
        """Get all registered tools."""
        async with self._lock:
            return list(self._tools.values())
            
    async def execute(self, tool_name: str, role: str, **kwargs: Any) -> Any:
        """Execute a tool after checking permissions."""
        tool = await self.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
            
        # Check permissions
        for perm in tool.required_permissions:
            if not await self.security.check_permission(role, "tool", perm):
                logger.warning("tool_execution_denied", tool_name=tool_name, role=role, missing_perm=perm)
                raise PermissionError(f"Role {role} lacks permission {perm} to execute {tool_name}")
                
        # Validate arguments
        if not await tool.validate(**kwargs):
            raise ValueError(f"Invalid arguments for tool {tool_name}")
            
        # Execute
        logger.debug("executing_tool", tool_name=tool_name)
        return await tool.execute(**kwargs)
