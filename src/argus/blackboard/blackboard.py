"""Central blackboard implementation."""
from typing import Any, Dict, Optional
import structlog
from argus.core.enums import BlackboardSection
from argus.blackboard.sections import BlackboardSectionImpl


class Blackboard:
    """Central shared blackboard for agent communication and state sharing."""
    
    def __init__(self):
        self._sections: Dict[BlackboardSection, BlackboardSectionImpl] = {
            section: BlackboardSectionImpl(section) for section in BlackboardSection
        }
        self.logger = structlog.get_logger("argus.blackboard")

    async def write(self, section: BlackboardSection, key: str, value: Any, agent_id: str) -> None:
        """Write a value to a specific section."""
        await self._sections[section].write(key, value, agent_id)

    async def read(self, section: BlackboardSection, key: str) -> Optional[Any]:
        """Read a value from a specific section."""
        return await self._sections[section].read(key)

    async def read_section(self, section: BlackboardSection) -> Dict[str, Any]:
        """Read all entries in a section."""
        return await self._sections[section].read_all()

    async def delete(self, section: BlackboardSection, key: str) -> bool:
        """Delete a key from a section."""
        return await self._sections[section].delete(key)

    async def clear_section(self, section: BlackboardSection) -> None:
        """Clear all entries in a section."""
        await self._sections[section].clear()

    async def get_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Get a snapshot of the entire blackboard."""
        snapshot = {}
        for section, impl in self._sections.items():
            snapshot[section.value] = await impl.read_all()
        return snapshot
