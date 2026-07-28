"""Queue analytics types (PRD §19 / §27 / §31 QueueMetrics)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from analytics.zones.types import Zone, ZoneType

# Zone types interpreted as queue/service areas (Module 9).
QUEUE_ZONE_TYPES: frozenset[ZoneType] = frozenset(
    {ZoneType.QUEUE, ZoneType.CHECKOUT, ZoneType.WAITING}
)


def is_queue_zone(zone: Zone) -> bool:
    """True when ``zone`` should be tracked as a queue/service area."""
    return zone.analytics_enabled and zone.zone_type in QUEUE_ZONE_TYPES


class QueueThresholdKind(str, Enum):
    """Which queue threshold was exceeded."""

    LENGTH = "length"
    DURATION = "duration"


@dataclass(frozen=True, slots=True)
class QueueThresholdEvent:
    """PRD §27 — fired when queue length or duration exceeds configured limits."""

    camera_id: str
    zone_id: str
    zone_name: str
    threshold_kind: QueueThresholdKind
    queue_length: int
    queue_duration_seconds: float
    estimated_wait_seconds: float
    timestamp: float
    threshold_length: int | None = None
    threshold_seconds: float | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "camera_id": self.camera_id,
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "event_type": "QUEUE_THRESHOLD",
            "threshold_kind": self.threshold_kind.value,
            "queue_length": self.queue_length,
            "queue_duration_seconds": self.queue_duration_seconds,
            "estimated_wait_seconds": self.estimated_wait_seconds,
            "timestamp": datetime.fromtimestamp(
                self.timestamp, tz=timezone.utc
            ).isoformat(),
        }
        if self.threshold_length is not None:
            out["threshold_length"] = self.threshold_length
        if self.threshold_seconds is not None:
            out["threshold_seconds"] = self.threshold_seconds
        return out


@dataclass(frozen=True, slots=True)
class QueueMetricsSnapshot:
    """Per-queue-zone metrics (PRD §19)."""

    zone_id: str
    zone_name: str
    camera_id: str
    current_queue_length: int
    avg_queue_length: float
    max_queue_length: int
    estimated_wait_seconds: float
    queue_duration_seconds: float
    length_samples: int
    completed_wait_samples: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "camera_id": self.camera_id,
            "current_queue_length": self.current_queue_length,
            "avg_queue_length": self.avg_queue_length,
            "max_queue_length": self.max_queue_length,
            "estimated_wait_seconds": self.estimated_wait_seconds,
            "queue_duration_seconds": self.queue_duration_seconds,
            "length_samples": self.length_samples,
            "completed_wait_samples": self.completed_wait_samples,
        }
