"""Abstract base repository for database access."""
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar, Any

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Generic async repository interface with CRUD operations."""

    @abstractmethod
    async def get(self, id: Any) -> Optional[T]:
        """Retrieve an entity by its ID."""

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Retrieve all entities."""

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity."""

    @abstractmethod
    async def update(self, id: Any, entity: T) -> T:
        """Update an existing entity."""

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        """Delete an entity by its ID."""

    @abstractmethod
    async def count(self) -> int:
        """Return the total number of entities."""

    @abstractmethod
    async def exists(self, id: Any) -> bool:
        """Check if an entity exists by its ID."""
