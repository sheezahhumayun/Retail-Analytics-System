"""Database configuration (Module 11)."""

from __future__ import annotations

import os
from functools import lru_cache

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Host port 5433 avoids conflict with a local PostgreSQL install on 5432 (Windows).
DEFAULT_DATABASE_URL = "postgresql+psycopg2://retail:retail@localhost:5433/retail_analytics"


@lru_cache(maxsize=1)
def get_database_url() -> str:
    """Resolve SQLAlchemy URL from ``DATABASE_URL`` env or local default."""
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_raw_event_retention_days() -> int:
    """Days to keep raw ``events`` rows before pruning (PRD §35)."""
    raw = os.getenv("RAW_EVENT_RETENTION_DAYS", "90")
    try:
        return max(1, int(raw))
    except ValueError:
        return 90
