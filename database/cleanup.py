"""Scheduled pruning of raw analytics events (PRD §35)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func
from sqlmodel import Session, select

from .config import get_raw_event_retention_days
from .models import Event
from .session import session_scope

logger = logging.getLogger(__name__)


def prune_raw_events(
    session: Session,
    *,
    retention_days: int | None = None,
    now: datetime | None = None,
) -> int:
    """Delete ``events`` rows older than the retention window.

    Aggregated tables (``visitor_metrics``, ``zone_metrics``, etc.) are kept.
    Returns the number of rows deleted.
    """
    days = retention_days if retention_days is not None else get_raw_event_retention_days()
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=days)
    result = session.exec(delete(Event).where(Event.timestamp < cutoff))
    deleted = result.rowcount if result.rowcount is not None else 0
    session.commit()
    logger.info("Pruned %s raw event row(s) older than %s", deleted, cutoff.isoformat())
    return deleted


def run_cleanup(*, retention_days: int | None = None) -> int:
    """Entry point for cron / scheduled job."""
    with session_scope() as session:
        return prune_raw_events(session, retention_days=retention_days)


def count_events_older_than(session: Session, cutoff: datetime) -> int:
    return int(
        session.exec(
            select(func.count()).select_from(Event).where(Event.timestamp < cutoff)
        ).one()
    )


def main() -> None:
    deleted = run_cleanup()
    print(f"Pruned {deleted} raw event row(s).")


if __name__ == "__main__":
    main()
