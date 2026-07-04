"""In-memory cache with TTL."""
import time
from typing import Any, Dict, Optional, Tuple

class TTLCache:
    """Simple TTL based cache."""
    
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        
    async def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expires = self._cache[key]
            if time.time() < expires:
                return value
            else:
                del self._cache[key]
        return None
        
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._cache[key] = (value, expires)
        
    async def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
        
    async def clear(self) -> None:
        self._cache.clear()
