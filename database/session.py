"""SQLAlchemy engine and session helpers."""

from __future__ import annotations

import logging
import threading
from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from .config import get_database_url

logger = logging.getLogger(__name__)

POOL_SIZE = 10
MAX_OVERFLOW = 10
POOL_TIMEOUT = 30
POOL_RECYCLE = 1800

_engine: Engine | None = None
_engine_url: str | None = None
_engine_lock = threading.Lock()


def get_engine(*, database_url: str | None = None, echo: bool = False) -> Engine:
    """Return a process-wide SQLAlchemy engine."""
    global _engine, _engine_url
    url = database_url or get_database_url()
    with _engine_lock:
        if _engine is None or _engine_url != url:
            if _engine is not None:
                _engine.dispose()
            _engine = create_engine(
                url,
                echo=echo,
                pool_pre_ping=True,
                pool_size=POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_timeout=POOL_TIMEOUT,
                pool_recycle=POOL_RECYCLE,
            )
            _engine_url = url
        return _engine


def log_pool_settings(engine: Engine | None = None) -> None:
    """Log resolved pool configuration for startup diagnostics."""
    eng = engine or get_engine()
    logger.info(
        "Database connection pool: pool_size=%d max_overflow=%d pool_timeout=%ds "
        "pool_recycle=%ds pool_pre_ping=True status=%s",
        POOL_SIZE,
        MAX_OVERFLOW,
        POOL_TIMEOUT,
        POOL_RECYCLE,
        eng.pool.status(),
    )


def reset_engine() -> None:
    """Drop cached engine (tests)."""
    global _engine, _engine_url
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _engine_url = None


def create_all(*, database_url: str | None = None) -> None:
    """Create all tables (dev convenience — prefer Alembic in production)."""
    engine = get_engine(database_url=database_url)
    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope(*, database_url: str | None = None) -> Iterator[Session]:
    """Transactional session context manager."""
    session = Session(get_engine(database_url=database_url))
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Generator[Session, None, None]:
    """FastAPI-style dependency generator."""
    with session_scope() as session:
        yield session
