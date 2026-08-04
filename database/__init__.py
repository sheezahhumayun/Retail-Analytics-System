"""Database & event storage (Module 11, PRD §31 / §35)."""

from .cleanup import prune_raw_events, run_cleanup
from .config import get_database_url, get_raw_event_retention_days
from .models import (
    Alert,
    AlertRule,
    Camera,
    CountingLine,
    DwellEventRow,
    Event,
    OccupancyMetric,
    Organization,
    QueueMetric,
    Store,
    Track,
    User,
    VisitorMetric,
    Zone,
    ZoneMetric,
)
from .seed import seed_reference_data
from .session import create_all, get_engine, get_session, reset_engine, session_scope

_LAZY_EXPORTS = {
    "AnalyticsDbWriter",
    "DbWriterConfig",
    "visitors_by_hour_yesterday",
}

__all__ = [
    "Alert",
    "AlertRule",
    "AnalyticsDbWriter",
    "Camera",
    "CountingLine",
    "DbWriterConfig",
    "DwellEventRow",
    "Event",
    "OccupancyMetric",
    "Organization",
    "QueueMetric",
    "Store",
    "Track",
    "User",
    "VisitorMetric",
    "Zone",
    "ZoneMetric",
    "create_all",
    "get_database_url",
    "get_engine",
    "get_raw_event_retention_days",
    "get_session",
    "prune_raw_events",
    "reset_engine",
    "run_cleanup",
    "seed_reference_data",
    "session_scope",
    "visitors_by_hour_yesterday",
]


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        from .writer import AnalyticsDbWriter, DbWriterConfig, visitors_by_hour_yesterday

        return {
            "AnalyticsDbWriter": AnalyticsDbWriter,
            "DbWriterConfig": DbWriterConfig,
            "visitors_by_hour_yesterday": visitors_by_hour_yesterday,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
