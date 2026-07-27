"""Dwell session tracker — consumes Module 6 zone events (PRD §16)."""

from __future__ import annotations

from dataclasses import dataclass

from analytics.zones.types import Zone, ZoneEvent, ZoneEventType

from .aggregates import DwellAggregator
from .types import (
    DwellAggregatesSnapshot,
    DwellCloseReason,
    DwellEvent,
    DwellThresholdEvent,
)


@dataclass
class _ActiveSession:
    """In-progress dwell for one track in one zone."""

    camera_id: str
    zone_id: str
    zone_name: str
    track_id: int
    enter_timestamp: float
    last_seen_timestamp: float
    threshold_seconds: float | None = None
    threshold_fired: bool = False


@dataclass(frozen=True, slots=True)
class DwellProcessResult:
    """Events and updated aggregates from one :meth:`DwellTracker.process` call."""

    dwell_event: DwellEvent | None = None
    threshold_event: DwellThresholdEvent | None = None
    aggregates: DwellAggregatesSnapshot | None = None


class DwellTracker:
    """Track dwell sessions from ZONE_ENTER / ZONE_EXIT / ZONE_PRESENCE.

    Parameters
    ----------
    zones:
        Zone definitions (used for ids, names, and optional per-zone thresholds).
    dwell_thresholds:
        Per-zone ``dwell_threshold_seconds`` overrides. Zones omitted here use
        ``None`` (no threshold alerts).
    lost_track_timeout_seconds:
        If a track has an open dwell session but no zone event (including
        PRESENCE) for this many seconds, close the session using
        ``last_seen_timestamp`` as the exit time with
        ``close_reason=TRACK_LOST``. This is an **approximation** for tracking
        failures — not a real zone exit. Default ``5.0`` s is slightly above
        ByteTrack's ``track_buffer`` at Module 1's 10 fps (~3 s).
    """

    def __init__(
        self,
        zones: list[Zone] | tuple[Zone, ...],
        *,
        dwell_thresholds: dict[str, float | None] | None = None,
        lost_track_timeout_seconds: float = 5.0,
    ) -> None:
        self._lost_track_timeout = max(0.1, float(lost_track_timeout_seconds))
        thresholds = dwell_thresholds or {}
        self._zone_meta: dict[str, tuple[str, str, float | None]] = {}
        for z in zones:
            if not z.analytics_enabled:
                continue
            thresh = thresholds.get(z.zone_id)
            self._zone_meta[z.zone_id] = (z.zone_name, z.camera_id, thresh)

        self._sessions: dict[tuple[str, int], _ActiveSession] = {}
        self._aggregators: dict[str, DwellAggregator] = {
            zid: DwellAggregator(zid, meta[0]) for zid, meta in self._zone_meta.items()
        }

    @property
    def lost_track_timeout_seconds(self) -> float:
        return self._lost_track_timeout

    @property
    def zone_ids(self) -> tuple[str, ...]:
        return tuple(self._zone_meta.keys())

    def reset(self) -> None:
        self._sessions.clear()
        for agg in self._aggregators.values():
            agg.reset()

    def active_session_count(self, zone_id: str | None = None) -> int:
        if zone_id is None:
            return len(self._sessions)
        return sum(1 for key in self._sessions if key[0] == zone_id)

    def snapshot(self, zone_id: str) -> DwellAggregatesSnapshot | None:
        agg = self._aggregators.get(zone_id)
        if agg is None:
            return None
        agg.set_active_sessions(self.active_session_count(zone_id))
        return agg.snapshot()

    def all_snapshots(self) -> dict[str, DwellAggregatesSnapshot]:
        return {
            zid: snap
            for zid in self._zone_meta
            if (snap := self.snapshot(zid)) is not None
        }

    def process(self, event: ZoneEvent) -> DwellProcessResult:
        """Apply one zone event; may emit dwell or threshold events."""
        meta = self._zone_meta.get(event.zone_id)
        if meta is None:
            return DwellProcessResult()

        zone_name, camera_id, threshold = meta
        key = (event.zone_id, event.track_id)
        dwell_event: DwellEvent | None = None
        threshold_event: DwellThresholdEvent | None = None

        if event.event_type == ZoneEventType.ZONE_ENTER:
            self._sessions[key] = _ActiveSession(
                camera_id=camera_id,
                zone_id=event.zone_id,
                zone_name=zone_name,
                track_id=event.track_id,
                enter_timestamp=event.timestamp,
                last_seen_timestamp=event.timestamp,
                threshold_seconds=threshold,
            )

        elif event.event_type == ZoneEventType.ZONE_PRESENCE:
            session = self._sessions.get(key)
            if session is not None:
                session.last_seen_timestamp = event.timestamp
                threshold_event = self._maybe_threshold(session, event.timestamp)

        elif event.event_type == ZoneEventType.ZONE_EXIT:
            dwell_event = self._close_session(
                key,
                exit_timestamp=event.timestamp,
                close_reason=DwellCloseReason.EXIT,
            )

        agg = self._aggregators.get(event.zone_id)
        aggregates = None
        if agg is not None:
            if dwell_event is not None:
                agg.add(dwell_event)
            agg.set_active_sessions(self.active_session_count(event.zone_id))
            aggregates = agg.snapshot()

        return DwellProcessResult(
            dwell_event=dwell_event,
            threshold_event=threshold_event,
            aggregates=aggregates,
        )

    def close_stale_sessions(self, current_timestamp: float) -> list[DwellEvent]:
        """Close open dwells whose track has not been seen within the timeout.

        Call once per processed frame (or on a timer) with the current epoch
        time. Returns completed :class:`DwellEvent` records closed as
        ``TRACK_LOST``.
        """
        closed: list[DwellEvent] = []
        stale_keys: list[tuple[str, int]] = []

        for key, session in self._sessions.items():
            gap = current_timestamp - session.last_seen_timestamp
            if gap >= self._lost_track_timeout:
                stale_keys.append(key)

        for key in stale_keys:
            session = self._sessions.get(key)
            if session is None:
                continue
            ev = self._close_session(
                key,
                exit_timestamp=session.last_seen_timestamp,
                close_reason=DwellCloseReason.TRACK_LOST,
            )
            if ev is not None:
                closed.append(ev)
                agg = self._aggregators.get(ev.zone_id)
                if agg is not None:
                    agg.add(ev)
                    agg.set_active_sessions(self.active_session_count(ev.zone_id))

        return closed

    def _maybe_threshold(
        self,
        session: _ActiveSession,
        timestamp: float,
    ) -> DwellThresholdEvent | None:
        if session.threshold_seconds is None or session.threshold_fired:
            return None
        dwell = max(0.0, timestamp - session.enter_timestamp)
        if dwell < session.threshold_seconds:
            return None
        session.threshold_fired = True
        return DwellThresholdEvent(
            camera_id=session.camera_id,
            zone_id=session.zone_id,
            zone_name=session.zone_name,
            track_id=session.track_id,
            dwell_seconds=dwell,
            threshold_seconds=session.threshold_seconds,
            timestamp=timestamp,
        )

    def _close_session(
        self,
        key: tuple[str, int],
        *,
        exit_timestamp: float,
        close_reason: DwellCloseReason,
    ) -> DwellEvent | None:
        session = self._sessions.pop(key, None)
        if session is None:
            return None
        dwell = max(0.0, exit_timestamp - session.enter_timestamp)
        return DwellEvent(
            camera_id=session.camera_id,
            zone_id=session.zone_id,
            zone_name=session.zone_name,
            track_id=session.track_id,
            enter_timestamp=session.enter_timestamp,
            exit_timestamp=exit_timestamp,
            dwell_seconds=dwell,
            close_reason=close_reason,
        )


class MultiZoneDwellTracker:
    """Thin wrapper when zones are already grouped — delegates to :class:`DwellTracker`."""

    def __init__(
        self,
        zones: list[Zone] | tuple[Zone, ...],
        *,
        dwell_thresholds: dict[str, float | None] | None = None,
        lost_track_timeout_seconds: float = 5.0,
    ) -> None:
        self._tracker = DwellTracker(
            zones,
            dwell_thresholds=dwell_thresholds,
            lost_track_timeout_seconds=lost_track_timeout_seconds,
        )

    @property
    def tracker(self) -> DwellTracker:
        return self._tracker

    def reset(self) -> None:
        self._tracker.reset()

    def process(self, event: ZoneEvent) -> DwellProcessResult:
        return self._tracker.process(event)

    def close_stale_sessions(self, current_timestamp: float) -> list[DwellEvent]:
        return self._tracker.close_stale_sessions(current_timestamp)

    def all_snapshots(self) -> dict[str, DwellAggregatesSnapshot]:
        return self._tracker.all_snapshots()
