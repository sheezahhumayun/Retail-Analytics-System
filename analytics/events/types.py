"""Canonical analytics event schema (PRD §27)."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AnalyticsEventType(str, Enum):
    """Standard event types emitted by the retail analytics platform."""

    PERSON_DETECTED = "PERSON_DETECTED"
    ENTRY = "ENTRY"
    EXIT = "EXIT"
    ZONE_ENTER = "ZONE_ENTER"
    ZONE_EXIT = "ZONE_EXIT"
    DWELL_THRESHOLD = "DWELL_THRESHOLD"
    QUEUE_THRESHOLD = "QUEUE_THRESHOLD"
    CAMERA_OFFLINE = "CAMERA_OFFLINE"


class AnalyticsEvent(BaseModel):
    """Formal event envelope consumed by the Analytics Engine and downstream modules.

    All upstream producers (counting, zones, dwell, queues, detection, video
    ingestion) emit this shape onto the internal event bus.
    """

    event_type: str
    camera_id: str
    zone_id: str | None = None
    track_id: str | None = None
    timestamp: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}

    @classmethod
    def from_epoch(
        cls,
        *,
        event_type: str | AnalyticsEventType,
        camera_id: str,
        timestamp: float,
        zone_id: str | None = None,
        track_id: str | int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AnalyticsEvent:
        """Build from epoch seconds (the pipeline's native clock)."""
        et = event_type.value if isinstance(event_type, AnalyticsEventType) else event_type
        tid = str(track_id) if track_id is not None else None
        return cls(
            event_type=et,
            camera_id=camera_id,
            zone_id=zone_id,
            track_id=tid,
            timestamp=datetime.fromtimestamp(timestamp, tz=timezone.utc),
            metadata=dict(metadata or {}),
        )

    def to_log_dict(self) -> dict[str, Any]:
        """JSON-friendly dict for demo / test logging."""
        out: dict[str, Any] = {
            "event_type": self.event_type,
            "camera_id": self.camera_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": dict(self.metadata),
        }
        if self.zone_id is not None:
            out["zone_id"] = self.zone_id
        if self.track_id is not None:
            out["track_id"] = self.track_id
        return out
