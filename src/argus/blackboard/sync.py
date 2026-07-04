"""Concurrency control utilities for the blackboard."""
import asyncio
from typing import Any, Optional
from datetime import datetime, timezone


class ReadWriteLock:
    """Async Read-Write lock implementation."""
    def __init__(self):
        self._readers = 0
        self._writers = 0
        self._read_cond = asyncio.Condition()
        self._write_cond = asyncio.Condition()

    async def acquire_read(self):
        async with self._read_cond:
            while self._writers > 0:
                await self._read_cond.wait()
            self._readers += 1

    async def release_read(self):
        async with self._read_cond:
            self._readers -= 1
            if self._readers == 0:
                async with self._write_cond:
                    self._write_cond.notify()

    async def acquire_write(self):
        async with self._write_cond:
            while self._writers > 0 or self._readers > 0:
                await self._write_cond.wait()
            self._writers += 1

    async def release_write(self):
        async with self._write_cond:
            self._writers -= 1
            self._write_cond.notify()
            async with self._read_cond:
                self._read_cond.notify_all()


class VersionedEntry:
    """Wrapper for a blackboard entry with versioning for optimistic concurrency."""
    def __init__(self, value: Any, version: int = 1, expires_at: Optional[datetime] = None):
        self.value = value
        self.version = version
        self.expires_at = expires_at

    def update(self, new_value: Any, expected_version: Optional[int] = None) -> 'VersionedEntry':
        if expected_version is not None and self.version != expected_version:
            raise ValueError(f"Version mismatch. Expected {expected_version}, got {self.version}")
        return VersionedEntry(new_value, self.version + 1, self.expires_at)
