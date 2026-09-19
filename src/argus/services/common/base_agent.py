from abc import ABC, abstractmethod
from argus.services.common.schemas import AgentMessage

class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentMessage:
        """Process incoming agent message and return a response message."""
        pass
