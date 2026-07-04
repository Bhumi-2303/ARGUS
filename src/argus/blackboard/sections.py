"""Typed section implementations for the blackboard."""
from typing import Any, Dict, Optional
from argus.core.enums import BlackboardSection
from argus.blackboard.sync import ReadWriteLock, VersionedEntry
from datetime import datetime, timezone
import structlog


class BlackboardSectionImpl:
    """Implementation of a single blackboard section."""
    def __init__(self, section: BlackboardSection):
        self.section = section
        self.entries: Dict[str, VersionedEntry] = {}
        self.lock = ReadWriteLock()
        self.logger = structlog.get_logger("argus.blackboard.section").bind(section=section.value)

    async def write(self, key: str, value: Any, agent_id: str) -> None:
        """Write a value to the section."""
        await self.lock.acquire_write()
        try:
            if key in self.entries:
                self.entries[key] = self.entries[key].update(value)
            else:
                self.entries[key] = VersionedEntry(value)
            self.logger.debug("entry_written", key=key, agent_id=agent_id)
        finally:
            await self.lock.release_write()

    async def read(self, key: str) -> Optional[Any]:
        """Read a value from the section."""
        await self.lock.acquire_read()
        try:
            entry = self.entries.get(key)
            if entry:
                if entry.expires_at and entry.expires_at < datetime.now(timezone.utc):
                    return None  # Expired
                return entry.value
            return None
        finally:
            await self.lock.release_read()

    async def read_all(self) -> Dict[str, Any]:
        """Read all non-expired values from the section."""
        await self.lock.acquire_read()
        try:
            now = datetime.now(timezone.utc)
            return {
                k: v.value for k, v in self.entries.items()
                if not v.expires_at or v.expires_at >= now
            }
        finally:
            await self.lock.release_read()

    async def delete(self, key: str) -> bool:
        """Delete a key from the section."""
        await self.lock.acquire_write()
        try:
            if key in self.entries:
                del self.entries[key]
                return True
            return False
        finally:
            await self.lock.release_write()

    async def clear(self) -> None:
        """Clear all entries in the section."""
        await self.lock.acquire_write()
        try:
            self.entries.clear()
        finally:
            await self.lock.release_write()
