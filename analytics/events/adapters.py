"""Convert module-specific events into :class:`AnalyticsEvent`."""

from __future__ import annotations

from analytics.counting.types import CrossingEvent, EventType
from analytics.dwell.types import DwellThresholdEvent
from analytics.queues.types import QueueThresholdEvent
from analytics.zones.types import ZoneEvent, ZoneEventType
from inference.detection.types import Detection

from .types import AnalyticsEvent, AnalyticsEventType


def crossing_to_analytics(event: CrossingEvent) -> AnalyticsEvent:
    """Map a line-crossing event to ENTRY / EXIT."""
    if event.event_type == EventType.ENTRY:
        et = AnalyticsEventType.ENTRY
    else:
        et = AnalyticsEventType.EXIT
    metadata: dict = {}
    if event.line_name:
        metadata["line_name"] = event.line_name
    return AnalyticsEvent.from_epoch(
        event_type=et,
        camera_id=event.camera_id,
        track_id=event.track_id,
        timestamp=event.timestamp,
        metadata=metadata,
    )


def zone_to_analytics(event: ZoneEvent) -> AnalyticsEvent | None:
    """Map zone transition events to ZONE_ENTER / ZONE_EXIT."""
    if event.event_type == ZoneEventType.ZONE_ENTER:
        et = AnalyticsEventType.ZONE_ENTER
    elif event.event_type == ZoneEventType.ZONE_EXIT:
        et = AnalyticsEventType.ZONE_EXIT
    else:
        return None
    metadata: dict = {"zone_name": event.zone_name}
    return AnalyticsEvent.from_epoch(
        event_type=et,
        camera_id=event.camera_id,
        zone_id=event.zone_id,
        track_id=event.track_id,
        timestamp=event.timestamp,
        metadata=metadata,
    )


def dwell_threshold_to_analytics(event: DwellThresholdEvent) -> AnalyticsEvent:
    return AnalyticsEvent.from_epoch(
        event_type=AnalyticsEventType.DWELL_THRESHOLD,
        camera_id=event.camera_id,
        zone_id=event.zone_id,
        track_id=event.track_id,
        timestamp=event.timestamp,
        metadata={
            "zone_name": event.zone_name,
            "dwell_seconds": event.dwell_seconds,
            "threshold_seconds": event.threshold_seconds,
        },
    )


def queue_threshold_to_analytics(event: QueueThresholdEvent) -> AnalyticsEvent:
    metadata = {
        "zone_name": event.zone_name,
        "threshold_kind": event.threshold_kind.value,
        "queue_length": event.queue_length,
        "queue_duration_seconds": event.queue_duration_seconds,
        "estimated_wait_seconds": event.estimated_wait_seconds,
    }
    if event.threshold_length is not None:
        metadata["threshold_length"] = event.threshold_length
    if event.threshold_seconds is not None:
        metadata["threshold_seconds"] = event.threshold_seconds
    return AnalyticsEvent.from_epoch(
        event_type=AnalyticsEventType.QUEUE_THRESHOLD,
        camera_id=event.camera_id,
        zone_id=event.zone_id,
        timestamp=event.timestamp,
        metadata=metadata,
    )


def person_detected_to_analytics(
    detection: Detection,
    *,
    sample_index: int = 0,
) -> AnalyticsEvent:
    """Sampled detection telemetry — not persisted long-term (PRD §31)."""
    return AnalyticsEvent.from_epoch(
        event_type=AnalyticsEventType.PERSON_DETECTED,
        camera_id=detection.camera_id,
        track_id=None,
        timestamp=detection.timestamp,
        metadata={
            "confidence": detection.confidence,
            "bbox": list(detection.bbox),
            "class_id": detection.class_id,
            "class_name": detection.class_name,
            "sample_index": sample_index,
        },
    )


def camera_offline_to_analytics(
    camera_id: str,
    *,
    timestamp: float,
    reason: str = "reconnect_exhausted",
    url: str | None = None,
) -> AnalyticsEvent:
    metadata: dict = {"reason": reason}
    if url is not None:
        metadata["url"] = url
    return AnalyticsEvent.from_epoch(
        event_type=AnalyticsEventType.CAMERA_OFFLINE,
        camera_id=camera_id,
        timestamp=timestamp,
        metadata=metadata,
    )
