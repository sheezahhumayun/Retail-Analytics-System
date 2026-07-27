"""Zone analytics — visitors, occupancy, dwell, hourly traffic (PRD §15)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo

from analytics.counting.types import CrossingEvent, EventType
from analytics.occupancy import OccupancyScope, OccupancyTracker
from analytics.occupancy.tracker import UTC, _normalize_timezone

from .types import Zone, ZoneEvent, ZoneEventType


@dataclass(frozen=True, slots=True)
class ZoneAnalyticsSnapshot:
    """Point-in-time zone metrics (PRD §15)."""

    zone_id: str
    zone_name: str
    zone_visitors: int
    current_occupancy: int
    total_visits: int
    avg_dwell_time: float
    max_dwell_time: float
    min_dwell_time: float | None
    traffic_by_hour: dict[int, int]

    def to_dict(self) -> dict:
        return {
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "zone_visitors": self.zone_visitors,
            "current_occupancy": self.current_occupancy,
            "total_visits": self.total_visits,
            "avg_dwell_time": self.avg_dwell_time,
            "max_dwell_time": self.max_dwell_time,
            "min_dwell_time": self.min_dwell_time,
            "traffic_by_hour": dict(sorted(self.traffic_by_hour.items())),
        }


class ZoneAnalytics:
    """Compute zone metrics from :class:`ZoneEvent` stream.

    Uses :class:`OccupancyTracker` with ``OccupancyScope.ZONE`` for
    entries-minus-exits occupancy (same pattern as Module 5).
    """

    def __init__(
        self,
        zone: Zone,
        *,
        timezone: str | ZoneInfo | dt_timezone = UTC,
    ) -> None:
        self._zone = zone
        self._tz = _normalize_timezone(timezone)
        self._occupancy = OccupancyTracker(
            zone.zone_id,
            scope_type=OccupancyScope.ZONE,
            timezone=self._tz,
        )
        self._visitor_ids: set[int] = set()
        self._total_visits = 0
        self._traffic_by_hour: dict[int, int] = {}
        self._completed_dwells: list[float] = []
        self._active_since: dict[int, float] = {}
        self._presence_accum: dict[int, float] = {}

    @property
    def zone(self) -> Zone:
        return self._zone

    def reset(self) -> None:
        """Clear all counters."""
        self._occupancy.reset()
        self._visitor_ids.clear()
        self._total_visits = 0
        self._traffic_by_hour.clear()
        self._completed_dwells.clear()
        self._active_since.clear()
        self._presence_accum.clear()

    def snapshot(self) -> ZoneAnalyticsSnapshot:
        return self._build_snapshot()

    def process(self, event: ZoneEvent) -> ZoneAnalyticsSnapshot:
        """Apply one zone event and return updated metrics."""
        if event.zone_id != self._zone.zone_id:
            return self.snapshot()

        if event.event_type == ZoneEventType.ZONE_ENTER:
            self._visitor_ids.add(event.track_id)
            self._total_visits += 1
            self._active_since[event.track_id] = event.timestamp
            self._presence_accum[event.track_id] = 0.0
            hour = self._event_hour(event.timestamp)
            self._traffic_by_hour[hour] = self._traffic_by_hour.get(hour, 0) + 1
            self._occupancy.process(self._to_crossing(event, EventType.ENTRY))

        elif event.event_type == ZoneEventType.ZONE_EXIT:
            self._finalize_dwell(event.track_id, event.timestamp)
            self._occupancy.process(self._to_crossing(event, EventType.EXIT))

        elif event.event_type == ZoneEventType.ZONE_PRESENCE:
            if event.dwell_delta is not None:
                self._presence_accum[event.track_id] = (
                    self._presence_accum.get(event.track_id, 0.0) + event.dwell_delta
                )

        return self.snapshot()

    def _event_hour(self, timestamp: float) -> int:
        return datetime.fromtimestamp(timestamp, tz=self._tz).hour

    def _to_crossing(self, event: ZoneEvent, event_type: EventType) -> CrossingEvent:
        return CrossingEvent(
            camera_id=event.camera_id,
            track_id=event.track_id,
            event_type=event_type,
            timestamp=event.timestamp,
            line_name=event.zone_id,
        )

    def _finalize_dwell(self, track_id: int, exit_ts: float) -> None:
        entered = self._active_since.pop(track_id, None)
        self._presence_accum.pop(track_id, None)
        if entered is not None:
            self._completed_dwells.append(max(0.0, exit_ts - entered))

    def _dwell_stats(self) -> tuple[float, float, float | None]:
        if not self._completed_dwells:
            return 0.0, 0.0, None
        dwells = self._completed_dwells
        return sum(dwells) / len(dwells), max(dwells), min(dwells)

    def _build_snapshot(self) -> ZoneAnalyticsSnapshot:
        occ = self._occupancy.snapshot()
        avg_d, max_d, min_d = self._dwell_stats()
        return ZoneAnalyticsSnapshot(
            zone_id=self._zone.zone_id,
            zone_name=self._zone.zone_name,
            zone_visitors=len(self._visitor_ids),
            current_occupancy=occ.current_occupancy,
            total_visits=self._total_visits,
            avg_dwell_time=avg_d,
            max_dwell_time=max_d,
            min_dwell_time=min_d,
            traffic_by_hour=dict(self._traffic_by_hour),
        )


class MultiZoneAnalytics:
    """Route zone events to per-zone analytics trackers."""

    def __init__(
        self,
        zones: list[Zone] | tuple[Zone, ...],
        *,
        timezone: str | ZoneInfo | dt_timezone = UTC,
    ) -> None:
        self._analytics: dict[str, ZoneAnalytics] = {
            z.zone_id: ZoneAnalytics(z, timezone=timezone)
            for z in zones
            if z.analytics_enabled
        }

    @property
    def zone_ids(self) -> tuple[str, ...]:
        return tuple(self._analytics.keys())

    def reset(self) -> None:
        for tracker in self._analytics.values():
            tracker.reset()

    def process(self, event: ZoneEvent) -> ZoneAnalyticsSnapshot | None:
        tracker = self._analytics.get(event.zone_id)
        if tracker is None:
            return None
        return tracker.process(event)

    def snapshot(self, zone_id: str) -> ZoneAnalyticsSnapshot | None:
        tracker = self._analytics.get(zone_id)
        return tracker.snapshot() if tracker is not None else None

    def all_snapshots(self) -> dict[str, ZoneAnalyticsSnapshot]:
        return {zid: t.snapshot() for zid, t in self._analytics.items()}
