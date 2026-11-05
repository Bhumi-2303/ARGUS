"""Database migration and table creation utilities for ARGUS."""

from typing import Any
import structlog
from sqlalchemy.engine import Engine

from argus.database.models import Base

logger = structlog.get_logger("argus.database.migrations")


async def create_all_tables(engine: Any) -> None:
    """Create all defined tables if they do not already exist.

    Handles Engine, AsyncEngineWrapper, str URL, or any custom engine object.
    """
    if isinstance(engine, str):
        from argus.database.engine import get_sync_engine
        underlying = get_sync_engine(engine)
    else:
        underlying = getattr(engine, "_engine", engine)
    Base.metadata.create_all(bind=underlying)
    logger.info("database_tables_verified_or_created")


def create_all_tables_sync(engine: Any) -> None:
    """Synchronous helper for table creation."""
    if isinstance(engine, str):
        from argus.database.engine import get_sync_engine
        underlying = get_sync_engine(engine)
    else:
        underlying = getattr(engine, "_engine", engine)
    Base.metadata.create_all(bind=underlying)
    logger.info("database_tables_verified_or_created_sync")
