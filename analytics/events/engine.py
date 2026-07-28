"""Central Analytics Engine — single consumer of :class:`AnalyticsEvent` (PRD §27)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo

from analytics.counting.types import CrossingEvent, EventType
from analytics.dwell import DwellTracker
from analytics.dwell.types import DwellAggregatesSnapshot
from analytics.occupancy import OccupancyScope, OccupancyTracker, StoreOccupancyAggregator
from analytics.occupancy.types import OccupancySnapshot
from analytics.occupancy.tracker import UTC, _normalize_timezone
from analytics.queues import QueueTracker
from analytics.queues.types import QueueMetricsSnapshot
from analytics.zones import MultiZoneAnalytics, Zone, ZoneAnalyticsSnapshot
from analytics.zones.types import ZoneEvent

from .adapters import (
    crossing_to_analytics,
    dwell_threshold_to_analytics,
    queue_threshold_to_analytics,
    zone_to_analytics,
)
from .bus import EventBus
from .types import AnalyticsEvent, AnalyticsEventType


@dataclass
class AnalyticsEngineConfig:
    """Runtime configuration for metric aggregation."""

    camera_ids: list[str]
    zones: list[Zone] = field(default_factory=list)
    store_id: str | None = None
    timezone: str | ZoneInfo | dt_timezone = UTC
    dwell_thresholds: dict[str, float | None] | None = None
    queue_length_thresholds: dict[str, int | None] | None = None
    queue_duration_thresholds: dict[str, float | None] | None = None
    lost_track_timeout_seconds: float = 5.0
    floor_at_zero: bool = True


class AnalyticsEngine:
    """Consume bus events and produce occupancy, zone, dwell, and queue metrics.

    Producers publish PRD §27 events onto an :class:`EventBus`. This engine
    subscribes and routes them to the same aggregation logic previously invoked
    ad hoc in Modules 4–9.

    Zone presence events (``ZONE_PRESENCE``) are not on the bus — call
    :meth:`process_zone_event` from the zone detector loop so dwell thresholds
    and queue metrics stay accurate.
    """

    def __init__(
        self,
        bus: EventBus,
        config: AnalyticsEngineConfig,
    ) -> None:
        self._bus = bus
        self._config = config
        tz = _normalize_timezone(config.timezone)

        self._camera_occupancy: dict[str, OccupancyTracker] = {
            cid: OccupancyTracker(
                cid,
                scope_type=OccupancyScope.CAMERA,
                floor_at_zero=config.floor_at_zero,
                timezone=tz,
            )
            for cid in config.camera_ids
        }

        self._store: StoreOccupancyAggregator | None = None
        if config.store_id is not None and config.camera_ids:
            self._store = StoreOccupancyAggregator(
                config.store_id,
                config.camera_ids,
                floor_at_zero=config.floor_at_zero,
                timezone=tz,
            )

        self._zone_analytics = MultiZoneAnalytics(config.zones, timezone=tz)
        self._dwell = DwellTracker(
            config.zones,
            dwell_thresholds=config.dwell_thresholds,
            lost_track_timeout_seconds=config.lost_track_timeout_seconds,
        )
        self._queues = QueueTracker(
            config.zones,
            length_thresholds=config.queue_length_thresholds,
            duration_thresholds=config.queue_duration_thresholds,
        )

        bus.subscribe(self._on_event)

    @property
    def bus(self) -> EventBus:
        return self._bus

    def reset(self) -> None:
        """Clear all aggregated metrics."""
        for tracker in self._camera_occupancy.values():
            tracker.reset()
        if self._store is not None:
            self._store.reset()
        self._zone_analytics.reset()
        self._dwell.reset()
        self._queues.reset()

    def _on_event(self, event: AnalyticsEvent) -> None:
        if event.event_type == AnalyticsEventType.ENTRY.value:
            self._apply_crossing(event, EventType.ENTRY)
        elif event.event_type == AnalyticsEventType.EXIT.value:
            self._apply_crossing(event, EventType.EXIT)

    def _apply_crossing(self, event: AnalyticsEvent, event_type: EventType) -> None:
        if event.track_id is None:
            return
        crossing = CrossingEvent(
            camera_id=event.camera_id,
            track_id=int(event.track_id),
            event_type=event_type,
            timestamp=event.timestamp.timestamp(),
            line_name=str(event.metadata.get("line_name", "")),
        )
        tracker = self._camera_occupancy.get(event.camera_id)
        if tracker is not None:
            tracker.process(crossing)
        if self._store is not None:
            self._store.process(crossing)

    def process_zone_event(self, event: ZoneEvent) -> None:
        """Apply a zone event and publish bus events for transitions / thresholds."""
        analytics_event = zone_to_analytics(event)
        if analytics_event is not None:
            self._bus.publish(analytics_event)

        self._zone_analytics.process(event)

        dwell_result = self._dwell.process(event)
        if dwell_result.threshold_event is not None:
            self._bus.publish(
                dwell_threshold_to_analytics(dwell_result.threshold_event)
            )

        queue_result = self._queues.process(event)
        for threshold in queue_result.threshold_events:
            self._bus.publish(queue_threshold_to_analytics(threshold))

    def close_stale_dwell_sessions(self, current_timestamp: float) -> None:
        """Close dwell sessions whose tracks were lost (call once per frame)."""
        for dwell_event in self._dwell.close_stale_sessions(current_timestamp):
            agg = self._dwell.snapshot(dwell_event.zone_id)
            if agg is not None:
                pass  # aggregates updated inside DwellTracker

    def publish_crossing(self, event: CrossingEvent) -> None:
        """Publish a crossing event and let the engine aggregate occupancy."""
        self._bus.publish(crossing_to_analytics(event))

    def camera_occupancy(self, camera_id: str) -> OccupancySnapshot | None:
        tracker = self._camera_occupancy.get(camera_id)
        return tracker.snapshot() if tracker is not None else None

    def store_occupancy(self) -> OccupancySnapshot | None:
        return self._store.store_snapshot() if self._store is not None else None

    def zone_snapshot(self, zone_id: str) -> ZoneAnalyticsSnapshot | None:
        return self._zone_analytics.snapshot(zone_id)

    def zone_snapshots(self) -> dict[str, ZoneAnalyticsSnapshot]:
        return self._zone_analytics.all_snapshots()

    def dwell_snapshot(self, zone_id: str) -> DwellAggregatesSnapshot | None:
        return self._dwell.snapshot(zone_id)

    def dwell_snapshots(self) -> dict[str, DwellAggregatesSnapshot]:
        return self._dwell.all_snapshots()

    def queue_snapshot(self, zone_id: str) -> QueueMetricsSnapshot | None:
        return self._queues.snapshot(zone_id)

    def queue_snapshots(self) -> dict[str, QueueMetricsSnapshot]:
        return self._queues.all_snapshots()

    def event_types_seen(self) -> set[str]:
        return {e.event_type for e in self._bus.event_log}
