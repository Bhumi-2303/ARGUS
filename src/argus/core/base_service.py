"""Abstract base class for all ARGUS services."""
from abc import ABC
import structlog


class BaseService(ABC):
    """Abstract service layer base class."""

    def __init__(self) -> None:
        self.logger = structlog.get_logger(f"argus.service.{self.__class__.__name__.lower()}")
