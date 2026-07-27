"""Dwell-time analytics types (PRD §16 / §27 / §31 DwellEvents)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DwellCloseReason(str, Enum):
    """How a dwell session ended."""

    EXIT = "exit"
    TRACK_LOST = "track_lost"


class DwellBucket(str, Enum):
    """Histogram buckets for dwell-time distribution (dashboard Module 13)."""

    UNDER_30S = "0-30s"
    SEC_30_60 = "30-60s"
    MIN_1_3 = "1-3min"
    MIN_3_10 = "3-10min"
    OVER_10MIN = "10min+"


# (label, min_inclusive_seconds, max_exclusive_seconds or None for open-ended)
DWELL_BUCKET_BOUNDS: tuple[tuple[DwellBucket, float, float | None], ...] = (
    (DwellBucket.UNDER_30S, 0.0, 30.0),
    (DwellBucket.SEC_30_60, 30.0, 60.0),
    (DwellBucket.MIN_1_3, 60.0, 180.0),
    (DwellBucket.MIN_3_10, 180.0, 600.0),
    (DwellBucket.OVER_10MIN, 600.0, None),
)


def dwell_bucket(dwell_seconds: float) -> DwellBucket:
    """Assign a completed dwell duration to a histogram bucket."""
    value = max(0.0, dwell_seconds)
    for label, low, high in DWELL_BUCKET_BOUNDS:
        if high is None:
            return label
        if low <= value < high:
            return label
    return DwellBucket.OVER_10MIN


def empty_distribution() -> dict[str, int]:
    """Zeroed histogram — all bucket labels present."""
    return {b.value: 0 for b in DwellBucket}


@dataclass(frozen=True, slots=True)
class DwellEvent:
    """Completed anonymous dwell session (maps to PRD §31 DwellEvents entity)."""

    camera_id: str
    zone_id: str
    zone_name: str
    track_id: int
    enter_timestamp: float
    exit_timestamp: float
    dwell_seconds: float
    close_reason: DwellCloseReason = DwellCloseReason.EXIT

    def to_dict(self) -> dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "track_id": str(self.track_id),
            "enter_timestamp": datetime.fromtimestamp(
                self.enter_timestamp, tz=timezone.utc
            ).isoformat(),
            "exit_timestamp": datetime.fromtimestamp(
                self.exit_timestamp, tz=timezone.utc
            ).isoformat(),
            "dwell_seconds": self.dwell_seconds,
            "close_reason": self.close_reason.value,
        }


@dataclass(frozen=True, slots=True)
class DwellThresholdEvent:
    """PRD §27 — fired once per visit when dwell exceeds a zone threshold."""

    camera_id: str
    zone_id: str
    zone_name: str
    track_id: int
    dwell_seconds: float
    threshold_seconds: float
    timestamp: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "track_id": str(self.track_id),
            "event_type": "DWELL_THRESHOLD",
            "dwell_seconds": self.dwell_seconds,
            "threshold_seconds": self.threshold_seconds,
            "timestamp": datetime.fromtimestamp(
                self.timestamp, tz=timezone.utc
            ).isoformat(),
        }


@dataclass(frozen=True, slots=True)
class DwellAggregatesSnapshot:
    """Per-zone dwell statistics for a reporting period."""

    zone_id: str
    zone_name: str
    total_dwell_events: int
    avg_dwell_seconds: float
    median_dwell_seconds: float
    max_dwell_seconds: float
    distribution: dict[str, int]
    active_sessions: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "total_dwell_events": self.total_dwell_events,
            "avg_dwell_seconds": self.avg_dwell_seconds,
            "median_dwell_seconds": self.median_dwell_seconds,
            "max_dwell_seconds": self.max_dwell_seconds,
            "distribution": dict(self.distribution),
            "active_sessions": self.active_sessions,
        }
