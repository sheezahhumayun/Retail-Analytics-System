"""SQLAlchemy engine and session helpers."""

from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from .config import get_database_url

_engine: Engine | None = None


def get_engine(*, database_url: str | None = None, echo: bool = False) -> Engine:
    """Return a process-wide SQLAlchemy engine."""
    global _engine
    url = database_url or get_database_url()
    if _engine is None or str(_engine.url) != url:
        _engine = create_engine(url, echo=echo, pool_pre_ping=True)
    return _engine


def reset_engine() -> None:
    """Drop cached engine (tests)."""
    global _engine
    if _engine is not None:
        _engine.dispose()
    _engine = None


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
