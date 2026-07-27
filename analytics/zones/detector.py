"""Zone entry/exit/presence detection (PRD §14).

Mirrors :class:`analytics.counting.counter.LineCounter` — scans every new
consecutive pair in ``position_history`` each frame and evaluates **all**
configured zones for the camera on every track.

Uses a per-zone+track hysteresis buffer so brief boundary straddles or bbox
jitter do not flap ENTER/EXIT.
"""

from __future__ import annotations

from enum import Enum

from inference.tracking.types import PositionRecord, TrackedObject

from analytics.counting.geometry import foot_point_from_bbox

from .geometry import is_inside_zone
from .types import Zone, ZoneEvent, ZoneEventType


class _Awaiting(str, Enum):
    """Per zone+track debounce — which event type may fire next."""

    ANY = "any"
    ENTER = "enter"
    EXIT = "exit"


class ZoneDetector:
    """Detect zone transitions and presence for all zones on one camera.

    Parameters
    ----------
    zones:
        One or more :class:`Zone` definitions. Only zones with
        ``analytics_enabled=True`` are evaluated. Every zone whose
        ``camera_id`` matches a track is checked each frame.
    hysteresis_frames:
        Consecutive inside (or outside) readings required before confirming
        ZONE_ENTER (or ZONE_EXIT). Suppresses boundary flapping when a foot-
        point briefly straddles an edge. Default ``2`` matches the tracker's
        confirmation gate.
    """

    def __init__(
        self,
        zones: list[Zone] | tuple[Zone, ...],
        *,
        hysteresis_frames: int = 2,
    ) -> None:
        self._zones = tuple(z for z in zones if z.analytics_enabled)
        self._hysteresis_frames = max(1, int(hysteresis_frames))
        self._awaiting: dict[tuple[str, int], _Awaiting] = {}
        self._last_pair_end_idx: dict[tuple[str, int], int] = {}
        self._last_checked_ts: dict[tuple[str, int], float] = {}
        self._logical_inside: dict[tuple[str, int], bool] = {}
        self._inside_streak: dict[tuple[str, int], int] = {}
        self._outside_streak: dict[tuple[str, int], int] = {}

    @property
    def zones(self) -> tuple[Zone, ...]:
        return self._zones

    @property
    def hysteresis_frames(self) -> int:
        return self._hysteresis_frames

    def reset(self) -> None:
        """Clear per-track debounce state (new clip / zone reconfiguration)."""
        self._awaiting.clear()
        self._last_pair_end_idx.clear()
        self._last_checked_ts.clear()
        self._logical_inside.clear()
        self._inside_streak.clear()
        self._outside_streak.clear()

    def update(self, tracks: list[TrackedObject]) -> list[ZoneEvent]:
        """Process one frame of tracks; return zone events for all zones."""
        events: list[ZoneEvent] = []

        for track in tracks:
            for zone in self._zones:
                if track.camera_id != zone.camera_id:
                    continue
                events.extend(self._update_track_zone(track, zone))

        return events

    def _key(self, zone: Zone, track_id: int) -> tuple[str, int]:
        return (zone.zone_id, track_id)

    def _update_track_zone(
        self,
        track: TrackedObject,
        zone: Zone,
    ) -> list[ZoneEvent]:
        events: list[ZoneEvent] = []
        key = self._key(zone, track.track_id)
        history = track.position_history

        if len(history) < 2:
            if key not in self._awaiting:
                self._awaiting[key] = _Awaiting.ANY
            return events

        if key not in self._awaiting:
            self._awaiting[key] = _Awaiting.ANY

        pairs = self._pairs_to_check(key, history)
        for prev_rec, curr_rec in pairs:
            event = self._check_pair(track, zone, prev_rec, curr_rec)
            if event is not None:
                events.append(event)

        if pairs:
            self._last_pair_end_idx[key] = len(history) - 1
            self._last_checked_ts[key] = history[-1].timestamp

        return events

    def _pairs_to_check(
        self,
        key: tuple[str, int],
        history: tuple[PositionRecord, ...],
    ) -> list[tuple[PositionRecord, PositionRecord]]:
        if len(history) < 2:
            return []

        start = self._last_pair_end_idx.get(key, 0) + 1
        end = len(history) - 1

        if start <= end:
            return [(history[i - 1], history[i]) for i in range(start, end + 1)]

        if self._last_checked_ts.get(key) == history[-1].timestamp:
            return []
        return [(history[-2], history[-1])]

    def _check_pair(
        self,
        track: TrackedObject,
        zone: Zone,
        prev_rec: PositionRecord,
        curr_rec: PositionRecord,
    ) -> ZoneEvent | None:
        curr_pt = foot_point_from_bbox(curr_rec.bbox)
        curr_inside = is_inside_zone(zone, curr_pt)
        key = self._key(zone, track.track_id)
        logically_inside = self._logical_inside.get(key, False)

        if curr_inside:
            self._outside_streak[key] = 0
            if logically_inside:
                delta = max(0.0, curr_rec.timestamp - prev_rec.timestamp)
                return ZoneEvent(
                    camera_id=track.camera_id,
                    zone_id=zone.zone_id,
                    zone_name=zone.zone_name,
                    track_id=track.track_id,
                    event_type=ZoneEventType.ZONE_PRESENCE,
                    timestamp=curr_rec.timestamp,
                    dwell_delta=delta,
                )

            self._inside_streak[key] = self._inside_streak.get(key, 0) + 1
            if self._inside_streak[key] < self._hysteresis_frames:
                return None
            if not self._may_emit(zone, track.track_id, ZoneEventType.ZONE_ENTER):
                return None

            self._logical_inside[key] = True
            self._inside_streak[key] = 0
            self._awaiting[key] = _Awaiting.EXIT
            return ZoneEvent(
                camera_id=track.camera_id,
                zone_id=zone.zone_id,
                zone_name=zone.zone_name,
                track_id=track.track_id,
                event_type=ZoneEventType.ZONE_ENTER,
                timestamp=curr_rec.timestamp,
            )

        self._inside_streak[key] = 0
        if not logically_inside:
            return None

        self._outside_streak[key] = self._outside_streak.get(key, 0) + 1
        if self._outside_streak[key] < self._hysteresis_frames:
            return None
        if not self._may_emit(zone, track.track_id, ZoneEventType.ZONE_EXIT):
            return None

        self._logical_inside[key] = False
        self._outside_streak[key] = 0
        self._awaiting[key] = _Awaiting.ENTER
        return ZoneEvent(
            camera_id=track.camera_id,
            zone_id=zone.zone_id,
            zone_name=zone.zone_name,
            track_id=track.track_id,
            event_type=ZoneEventType.ZONE_EXIT,
            timestamp=curr_rec.timestamp,
        )

    def _may_emit(
        self,
        zone: Zone,
        track_id: int,
        event_type: ZoneEventType,
    ) -> bool:
        if event_type == ZoneEventType.ZONE_PRESENCE:
            return True

        awaiting = self._awaiting.get(self._key(zone, track_id), _Awaiting.ANY)
        if awaiting == _Awaiting.ANY:
            return True
        if event_type == ZoneEventType.ZONE_ENTER:
            return awaiting == _Awaiting.ENTER
        return awaiting == _Awaiting.EXIT
