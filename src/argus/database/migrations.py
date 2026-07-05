"""Async migrations helper for creating tables."""
from sqlalchemy.ext.asyncio import AsyncEngine
from argus.database.session import Base
# Import models to register them on the metadata
import argus.database.models

async def create_all_tables(engine: AsyncEngine) -> None:
    """Create all registered tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
