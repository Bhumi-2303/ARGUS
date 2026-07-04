"""Shared memory utilizing the Blackboard."""
from typing import Any, Optional
from argus.core.interfaces import IBlackboard
from argus.core.enums import BlackboardSection

class SharedMemory:
    """Delegates to the shared context blackboard section."""
    
    def __init__(self, agent_id: str, blackboard: IBlackboard):
        self.agent_id = agent_id
        self.blackboard = blackboard
        
    async def get(self, key: str) -> Optional[Any]:
        return await self.blackboard.read(BlackboardSection.SHARED_CONTEXT, key)
        
    async def set(self, key: str, value: Any) -> None:
        await self.blackboard.write(BlackboardSection.SHARED_CONTEXT, key, value, self.agent_id)
        
    async def delete(self, key: str) -> bool:
        return await self.blackboard.delete(BlackboardSection.SHARED_CONTEXT, key)
        
    async def clear(self) -> None:
        await self.blackboard.clear_section(BlackboardSection.SHARED_CONTEXT)
