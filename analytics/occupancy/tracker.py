"""In-memory occupancy tracker — consumes Module 4 crossing events (PRD §13)."""

from __future__ import annotations

from datetime import date, datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from analytics.counting.types import CrossingEvent, EventType

from .types import OccupancyScope, OccupancySnapshot


def _normalize_timezone(tz: str | ZoneInfo | dt_timezone) -> ZoneInfo | dt_timezone:
    if isinstance(tz, ZoneInfo):
        return tz
    if isinstance(tz, dt_timezone):
        return tz
    if str(tz).upper() == "UTC":
        return dt_timezone.utc
    try:
        return ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        raise ZoneInfoNotFoundError(
            f"{tz!r} requires the tzdata package on Windows (pip install tzdata)"
        ) from None


UTC = dt_timezone.utc


class OccupancyTracker:
    """Maintain occupancy metrics from ENTRY/EXIT events for one scope.

    Parameters
    ----------
    scope_id:
        Camera id, store id, or zone id (see ``scope_type``).
    scope_type:
        ``CAMERA`` for per-entrance counting; ``STORE`` for rolled-up store
        metrics; ``ZONE`` reserved for Module 6.
    floor_at_zero:
        When ``True``, ``current_occupancy`` never goes below 0. Required for
        MVP when EXITS arrive without a prior ENTRY (people already inside when
        a clip or live stream starts).
    timezone:
        IANA timezone for midnight rollover of today's counters (default UTC).
        Use the store's local timezone once Module 16 admin config exists.
    """

    def __init__(
        self,
        scope_id: str,
        *,
        scope_type: OccupancyScope = OccupancyScope.CAMERA,
        floor_at_zero: bool = True,
        timezone: str | ZoneInfo | dt_timezone = UTC,
    ) -> None:
        self._scope_id = scope_id
        self._scope_type = scope_type
        self._floor_at_zero = floor_at_zero
        self._tz = _normalize_timezone(timezone)

        self._total_entries = 0
        self._total_exits = 0
        self._today_visitors = 0
        self._today_exits = 0
        self._peak_occupancy = 0
        self._peak_occupancy_time: float | None = None
        self._day_start: date | None = None
        self._last_day_rolled = False

    @property
    def last_day_rolled(self) -> bool:
        """True when the most recent :meth:`process` crossed a local midnight."""
        return self._last_day_rolled

    @property
    def scope_id(self) -> str:
        return self._scope_id

    @property
    def scope_type(self) -> OccupancyScope:
        return self._scope_type

    @property
    def floor_at_zero(self) -> bool:
        return self._floor_at_zero

    @property
    def timezone(self) -> ZoneInfo | dt_timezone:
        return self._tz

    def reset(self) -> None:
        """Clear all counters — call when a live camera starts on an empty store."""
        self._total_entries = 0
        self._total_exits = 0
        self._today_visitors = 0
        self._today_exits = 0
        self._peak_occupancy = 0
        self._peak_occupancy_time = None
        self._day_start = None
        self._last_day_rolled = False

    def snapshot(self) -> OccupancySnapshot:
        """Current metrics without processing a new event."""
        return OccupancySnapshot(
            scope_id=self._scope_id,
            scope_type=self._scope_type,
            current_occupancy=self._current_occupancy(),
            today_visitors=self._today_visitors,
            today_exits=self._today_exits,
            peak_occupancy=self._peak_occupancy,
            peak_occupancy_time=self._peak_occupancy_time,
            total_entries=self._total_entries,
            total_exits=self._total_exits,
        )

    def process(self, event: CrossingEvent) -> OccupancySnapshot:
        """Apply one crossing event and return updated metrics."""
        self._last_day_rolled = self._maybe_roll_day(event.timestamp)

        if event.event_type == EventType.ENTRY:
            self._total_entries += 1
            self._today_visitors += 1
        elif event.event_type == EventType.EXIT:
            self._total_exits += 1
            self._today_exits += 1

        self._update_peak(event.timestamp)
        return self.snapshot()

    def _current_occupancy(self) -> int:
        raw = self._total_entries - self._total_exits
        if self._floor_at_zero and raw < 0:
            return 0
        return raw

    def _update_peak(self, timestamp: float) -> None:
        current = self._current_occupancy()
        if current > self._peak_occupancy:
            self._peak_occupancy = current
            self._peak_occupancy_time = timestamp

    def _maybe_roll_day(self, timestamp: float) -> bool:
        event_date = datetime.fromtimestamp(timestamp, tz=self._tz).date()
        if self._day_start is None:
            self._day_start = event_date
            return False
        if event_date > self._day_start:
            self._roll_day()
            self._day_start = event_date
            return True
        return False

    def _roll_day(self) -> None:
        """Reset daily counters at local midnight (PRD today's visitors/exits)."""
        self._total_entries = 0
        self._total_exits = 0
        self._today_visitors = 0
        self._today_exits = 0
        self._peak_occupancy = 0
        self._peak_occupancy_time = None
