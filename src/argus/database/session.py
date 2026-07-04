"""Async SQLAlchemy session management."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import structlog
from config.settings import get_settings

logger = structlog.get_logger("argus.database")
settings = get_settings()

DATABASE_URL = f"sqlite+aiosqlite:///{settings.db.sqlite_path}"

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_size=settings.db.pool_size,
    max_overflow=10,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("database_session_error", error=str(e))
            await session.rollback()
            raise
        finally:
            await session.close()
