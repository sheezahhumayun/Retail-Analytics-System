"""Line-crossing counter — emits ENTRY/EXIT events (PRD §12)."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from inference.tracking.types import PositionRecord, TrackedObject

from .geometry import is_inside, movement_crosses_line, tracking_point_from_bbox
from .types import CountingLine, CrossingEvent, EventType

if TYPE_CHECKING:
    from analytics.events.bus import EventBus

DEFAULT_LINE_MARGIN = 15.0  # px slop on counting segment at 640-scale frames


class _Awaiting(str, Enum):
    """Per-track debounce state — which event type may fire next."""

    ANY = "any"  # first crossing for this track — accept either direction
    ENTRY = "entry"
    EXIT = "exit"


class LineCounter:
    """Detect when tracked people cross a :class:`CountingLine` and emit events.

    Scans every **new** consecutive pair in ``position_history`` each frame
    (not just the latest step). On first sight of a track, all existing pairs
    are checked so crossings during the tracker's confirmation window are not
    missed.

    Debounce: after an ENTRY, another ENTRY is suppressed until an EXIT fires
    (and vice versa), preventing double-counts from boundary jitter.
    """

    def __init__(
        self,
        line: CountingLine,
        *,
        line_margin: float = DEFAULT_LINE_MARGIN,
        event_bus: EventBus | None = None,
    ) -> None:
        self._line = line
        self._line_margin = float(line_margin)
        self._event_bus = event_bus
        self._awaiting: dict[int, _Awaiting] = {}
        self._last_pair_end_idx: dict[int, int] = {}
        self._last_checked_ts: dict[int, float] = {}

    @property
    def line(self) -> CountingLine:
        return self._line

    @property
    def line_margin(self) -> float:
        return self._line_margin

    def reset(self) -> None:
        """Clear per-track debounce state (new clip / line reconfiguration)."""
        self._awaiting.clear()
        self._last_pair_end_idx.clear()
        self._last_checked_ts.clear()

    def update(self, tracks: list[TrackedObject]) -> list[CrossingEvent]:
        """Process one frame of tracks; return any new crossing events."""
        events: list[CrossingEvent] = []

        for track in tracks:
            if track.camera_id != self._line.camera_id:
                continue

            history = track.position_history
            if len(history) < 2:
                if track.track_id not in self._awaiting:
                    self._awaiting[track.track_id] = _Awaiting.ANY
                continue

            if track.track_id not in self._awaiting:
                self._awaiting[track.track_id] = _Awaiting.ANY

            pairs = self._pairs_to_check(track.track_id, history)
            for prev_rec, curr_rec in pairs:
                event = self._check_pair(track, prev_rec, curr_rec)
                if event is not None:
                    events.append(event)

            if pairs:
                self._last_pair_end_idx[track.track_id] = len(history) - 1
                self._last_checked_ts[track.track_id] = history[-1].timestamp

        return events

    def _pairs_to_check(
        self,
        track_id: int,
        history: tuple[PositionRecord, ...],
    ) -> list[tuple[PositionRecord, PositionRecord]]:
        if len(history) < 2:
            return []

        start = self._last_pair_end_idx.get(track_id, 0) + 1
        end = len(history) - 1

        if start <= end:
            return [(history[i - 1], history[i]) for i in range(start, end + 1)]

        # History deque is at maxlen — indices do not grow; only the latest
        # step is new each frame.
        if self._last_checked_ts.get(track_id) == history[-1].timestamp:
            return []
        return [(history[-2], history[-1])]

    def _check_pair(
        self,
        track: TrackedObject,
        prev_rec: PositionRecord,
        curr_rec: PositionRecord,
    ) -> CrossingEvent | None:
        prev_pt = tracking_point_from_bbox(prev_rec.bbox)
        curr_pt = tracking_point_from_bbox(curr_rec.bbox)

        if not movement_crosses_line(
            self._line,
            prev_pt,
            curr_pt,
            margin=self._line_margin,
        ):
            return None

        prev_inside = is_inside(self._line, prev_pt)
        curr_inside = is_inside(self._line, curr_pt)

        if not prev_inside and curr_inside:
            event_type = EventType.ENTRY
        elif prev_inside and not curr_inside:
            event_type = EventType.EXIT
        else:
            return None

        if not self._may_emit(track.track_id, event_type):
            return None

        self._awaiting[track.track_id] = (
            _Awaiting.EXIT if event_type == EventType.ENTRY else _Awaiting.ENTRY
        )
        crossing = CrossingEvent(
            camera_id=track.camera_id,
            track_id=track.track_id,
            event_type=event_type,
            timestamp=curr_rec.timestamp,
            line_name=self._line.name,
        )
        if self._event_bus is not None:
            from analytics.events.adapters import crossing_to_analytics

            self._event_bus.publish(crossing_to_analytics(crossing))
        return crossing

    def _may_emit(self, track_id: int, event_type: EventType) -> bool:
        awaiting = self._awaiting.get(track_id, _Awaiting.ANY)
        if awaiting == _Awaiting.ANY:
            return True
        if event_type == EventType.ENTRY:
            return awaiting == _Awaiting.ENTRY
        return awaiting == _Awaiting.EXIT
