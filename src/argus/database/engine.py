"""SQLAlchemy async engine helper."""
from sqlalchemy.ext.asyncio import AsyncEngine
from argus.database.session import engine

def get_engine() -> AsyncEngine:
    """Return the global async engine instance."""
    return engine
