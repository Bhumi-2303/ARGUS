"""SQLAlchemy database engine and session management for ARGUS."""

from pathlib import Path
from typing import Any, Generator, Optional
import structlog
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from configs.settings import get_settings

logger = structlog.get_logger("argus.database")

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker] = None


def _ensure_sqlite_parent_dir(url: str) -> None:
    """Ensure SQLite directory exists if using file-based SQLite."""
    if "sqlite" in url and "///" in url and ":memory:" not in url:
        path_str = url.split("///")[-1].split("?")[0]
        if path_str:
            p = Path(path_str).expanduser().resolve()
            p.parent.mkdir(parents=True, exist_ok=True)


def get_sync_engine(url: Optional[str] = None) -> Engine:
    """Get or initialize the synchronous SQLAlchemy Engine."""
    global _engine, _session_factory
    if _engine is None or url is not None:
        settings = get_settings()
        target_url = url or settings.db.sync_url
        _ensure_sqlite_parent_dir(target_url)

        connect_args = {}
        if "sqlite" in target_url:
            connect_args["check_same_thread"] = False

        engine = create_engine(
            target_url,
            connect_args=connect_args,
            pool_pre_ping=True,
            future=True,
        )
        if url is None:
            _engine = engine
            _session_factory = sessionmaker(
                bind=_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
            return _engine
        return engine
    return _engine


class AsyncEngineWrapper:
    """Async-compatible wrapper around SQLAlchemy Engine.

    Enables awaiting lifecycle methods like `await engine.dispose()`
    without requiring third-party C-extensions (like greenlet on Python 3.14).
    """

    def __init__(self, engine: Engine):
        self._engine = engine

    @property
    def url(self):
        return self._engine.url

    @property
    def engine(self) -> Engine:
        return self._engine

    async def dispose(self) -> None:
        self._engine.dispose()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._engine, name)


def get_engine(url: Optional[str] = None) -> AsyncEngineWrapper:
    """Get async-compatible engine wrapper (used by scripts/init_db.py)."""
    return AsyncEngineWrapper(get_sync_engine(url))


# Backwards compatibility alias
get_async_engine = get_engine


def get_session(url: Optional[str] = None) -> Session:
    """Get a new database session."""
    global _session_factory
    if _session_factory is None or url is not None:
        engine = get_sync_engine(url)
        factory = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        if url is None:
            _session_factory = factory
        return factory()
    return _session_factory()


get_sync_session = get_session


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()


async def close_db_connections() -> None:
    """Dispose of engine connections on application shutdown."""
    global _engine, _session_factory
    if _engine:
        _engine.dispose()
        _engine = None
        _session_factory = None
