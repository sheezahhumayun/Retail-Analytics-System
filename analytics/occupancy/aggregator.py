"""Store-level occupancy rollup across multiple entrance cameras (PRD §13)."""

from __future__ import annotations

from datetime import timezone as dt_timezone
from zoneinfo import ZoneInfo

from analytics.counting.types import CrossingEvent

from .tracker import OccupancyTracker, UTC, _normalize_timezone
from .types import OccupancyScope, OccupancySnapshot


class StoreOccupancyAggregator:
    """Per-camera trackers plus a store-level rollup for multi-camera stores.

    Routes each :class:`CrossingEvent` to the camera tracker matching
    ``event.camera_id``. Store metrics are recomputed after every event so
    ``peak_occupancy`` reflects the combined occupancy across all registered
    cameras.
    """

    def __init__(
        self,
        store_id: str,
        camera_ids: list[str],
        *,
        floor_at_zero: bool = True,
        timezone: str | ZoneInfo | dt_timezone = UTC,
    ) -> None:
        self._store_id = store_id
        self._floor_at_zero = floor_at_zero
        self._tz = _normalize_timezone(timezone)
        self._cameras: dict[str, OccupancyTracker] = {
            cid: OccupancyTracker(
                cid,
                scope_type=OccupancyScope.CAMERA,
                floor_at_zero=floor_at_zero,
                timezone=self._tz,
            )
            for cid in camera_ids
        }
        self._store_peak = 0
        self._store_peak_time: float | None = None
        self._threshold_breached = False

    @property
    def store_id(self) -> str:
        return self._store_id

    @property
    def camera_ids(self) -> tuple[str, ...]:
        return tuple(self._cameras.keys())

    def reset(self) -> None:
        """Reset all camera and store rollup counters."""
        for tracker in self._cameras.values():
            tracker.reset()
        self._store_peak = 0
        self._store_peak_time = None
        self._threshold_breached = False

    def check_threshold(self, threshold: float) -> bool:
        """Return True only on below-threshold → at-or-above-threshold transition."""
        current = self.store_snapshot().current_occupancy
        if current >= threshold:
            if not self._threshold_breached:
                self._threshold_breached = True
                return True
            return False
        self._threshold_breached = False
        return False

    def camera_tracker(self, camera_id: str) -> OccupancyTracker | None:
        return self._cameras.get(camera_id)

    def camera_snapshot(self, camera_id: str) -> OccupancySnapshot | None:
        tracker = self._cameras.get(camera_id)
        return tracker.snapshot() if tracker is not None else None

    def store_snapshot(self) -> OccupancySnapshot:
        """Aggregated store metrics (sum of cameras + store-level peak)."""
        snaps = [t.snapshot() for t in self._cameras.values()]
        current = sum(s.current_occupancy for s in snaps)
        total_entries = sum(s.total_entries for s in snaps)
        total_exits = sum(s.total_exits for s in snaps)
        today_visitors = sum(s.today_visitors for s in snaps)
        today_exits = sum(s.today_exits for s in snaps)
        return OccupancySnapshot(
            scope_id=self._store_id,
            scope_type=OccupancyScope.STORE,
            current_occupancy=current,
            today_visitors=today_visitors,
            today_exits=today_exits,
            peak_occupancy=self._store_peak,
            peak_occupancy_time=self._store_peak_time,
            total_entries=total_entries,
            total_exits=total_exits,
        )

    def process(self, event: CrossingEvent) -> OccupancySnapshot | None:
        """Route event to its camera tracker and refresh store rollup."""
        tracker = self._cameras.get(event.camera_id)
        if tracker is None:
            return None

        tracker.process(event)

        if tracker.last_day_rolled:
            self._store_peak = 0
            self._store_peak_time = None

        store_current = sum(t.snapshot().current_occupancy for t in self._cameras.values())
        if store_current > self._store_peak:
            self._store_peak = store_current
            self._store_peak_time = event.timestamp

        return self.store_snapshot()
