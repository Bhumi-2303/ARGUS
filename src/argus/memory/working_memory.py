"""Ephemeral working memory for agents."""
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger("argus.memory.working")

class WorkingMemory:
    """In-memory dictionary for short-term agent context."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._store: Dict[str, Any] = {}
        
    async def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)
        
    async def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        
    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False
        
    async def clear(self) -> None:
        self._store.clear()
        
    async def get_all(self) -> Dict[str, Any]:
        return dict(self._store)
