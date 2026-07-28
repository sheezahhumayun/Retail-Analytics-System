"""Queue tracker — consumes Module 6 zone events (PRD §19)."""

from __future__ import annotations

from dataclasses import dataclass

from analytics.counting.types import CrossingEvent, EventType
from analytics.occupancy import OccupancyScope, OccupancyTracker
from analytics.zones.types import Zone, ZoneEvent, ZoneEventType

from .aggregates import QueueLengthAggregator
from .types import (
    QueueMetricsSnapshot,
    QueueThresholdEvent,
    QueueThresholdKind,
    is_queue_zone,
)


@dataclass
class _ZoneQueueState:
    camera_id: str
    zone_id: str
    zone_name: str
    occupancy: OccupancyTracker
    length_agg: QueueLengthAggregator
    completed_waits: list[float]
    active_since: dict[int, float]
    episode_start: float | None = None
    length_threshold: int | None = None
    duration_threshold: float | None = None
    length_threshold_fired: bool = False
    duration_threshold_fired: bool = False
    last_timestamp: float | None = None


@dataclass(frozen=True, slots=True)
class QueueProcessResult:
    """Output from one :meth:`QueueTracker.process` call."""

    threshold_events: tuple[QueueThresholdEvent, ...] = ()
    metrics: QueueMetricsSnapshot | None = None


class QueueTracker:
    """Turn zone occupancy into queue metrics and threshold alerts.

    A queue zone is a normal Module 6 polygon with ``zone_type`` of
    ``queue``, ``checkout``, or ``waiting``. Current queue length equals
    zone occupancy (entries minus exits). Estimated wait time uses the
    historical average completed dwell in that zone — an MVP approximation;
    position-in-queue refinement is Phase 2 (PRD §37).

    Parameters
    ----------
    zones:
        Zone definitions; only queue-eligible types are tracked.
    length_thresholds:
        Per-zone ``queue_length_threshold`` — alert when occupancy reaches
        this count.
    duration_thresholds:
        Per-zone ``queue_duration_threshold`` in seconds — alert when the
        queue has been non-empty continuously for this long.
    """

    def __init__(
        self,
        zones: list[Zone] | tuple[Zone, ...],
        *,
        length_thresholds: dict[str, int | None] | None = None,
        duration_thresholds: dict[str, float | None] | None = None,
    ) -> None:
        length_thresholds = length_thresholds or {}
        duration_thresholds = duration_thresholds or {}
        self._zones: dict[str, _ZoneQueueState] = {}

        for zone in zones:
            if not is_queue_zone(zone):
                continue
            self._zones[zone.zone_id] = _ZoneQueueState(
                camera_id=zone.camera_id,
                zone_id=zone.zone_id,
                zone_name=zone.zone_name,
                occupancy=OccupancyTracker(
                    zone.zone_id,
                    scope_type=OccupancyScope.ZONE,
                ),
                length_agg=QueueLengthAggregator(),
                completed_waits=[],
                active_since={},
                length_threshold=length_thresholds.get(zone.zone_id),
                duration_threshold=duration_thresholds.get(zone.zone_id),
            )

    @property
    def zone_ids(self) -> tuple[str, ...]:
        return tuple(self._zones.keys())

    def reset(self) -> None:
        for state in self._zones.values():
            state.occupancy.reset()
            state.length_agg.reset()
            state.completed_waits.clear()
            state.active_since.clear()
            state.episode_start = None
            state.length_threshold_fired = False
            state.duration_threshold_fired = False
            state.last_timestamp = None

    def snapshot(self, zone_id: str) -> QueueMetricsSnapshot | None:
        state = self._zones.get(zone_id)
        if state is None:
            return None
        return self._build_snapshot(state, timestamp=None)

    def all_snapshots(self) -> dict[str, QueueMetricsSnapshot]:
        return {
            zid: snap
            for zid in self._zones
            if (snap := self.snapshot(zid)) is not None
        }

    def process(self, event: ZoneEvent) -> QueueProcessResult:
        state = self._zones.get(event.zone_id)
        if state is None:
            return QueueProcessResult()

        if event.event_type == ZoneEventType.ZONE_ENTER:
            state.active_since[event.track_id] = event.timestamp
            state.occupancy.process(self._crossing(event, EventType.ENTRY))

        elif event.event_type == ZoneEventType.ZONE_EXIT:
            self._finalize_wait(state, event.track_id, event.timestamp)
            state.occupancy.process(self._crossing(event, EventType.EXIT))

        state.last_timestamp = event.timestamp
        length = state.occupancy.snapshot().current_occupancy
        state.length_agg.sample(length)
        self._update_episode(state, length, event.timestamp)

        thresholds = self._maybe_thresholds(state, length, event.timestamp)
        metrics = self._build_snapshot(state, timestamp=event.timestamp)
        return QueueProcessResult(threshold_events=thresholds, metrics=metrics)

    def _crossing(self, event: ZoneEvent, event_type: EventType) -> CrossingEvent:
        return CrossingEvent(
            camera_id=event.camera_id,
            track_id=event.track_id,
            event_type=event_type,
            timestamp=event.timestamp,
            line_name=event.zone_id,
        )

    def _finalize_wait(
        self,
        state: _ZoneQueueState,
        track_id: int,
        exit_ts: float,
    ) -> None:
        entered = state.active_since.pop(track_id, None)
        if entered is not None:
            state.completed_waits.append(max(0.0, exit_ts - entered))

    def _update_episode(
        self,
        state: _ZoneQueueState,
        length: int,
        timestamp: float,
    ) -> None:
        if length <= 0:
            state.episode_start = None
            state.length_threshold_fired = False
            state.duration_threshold_fired = False
            return
        if state.episode_start is None:
            state.episode_start = timestamp

    def _episode_duration(self, state: _ZoneQueueState, timestamp: float) -> float:
        if state.episode_start is None:
            return 0.0
        return max(0.0, timestamp - state.episode_start)

    def _estimated_wait(self, state: _ZoneQueueState) -> float:
        if not state.completed_waits:
            return 0.0
        return sum(state.completed_waits) / len(state.completed_waits)

    def _maybe_thresholds(
        self,
        state: _ZoneQueueState,
        length: int,
        timestamp: float,
    ) -> tuple[QueueThresholdEvent, ...]:
        events: list[QueueThresholdEvent] = []
        duration = self._episode_duration(state, timestamp)
        estimated = self._estimated_wait(state)

        if (
            state.length_threshold is not None
            and not state.length_threshold_fired
            and length >= state.length_threshold
        ):
            state.length_threshold_fired = True
            events.append(
                QueueThresholdEvent(
                    camera_id=state.camera_id,
                    zone_id=state.zone_id,
                    zone_name=state.zone_name,
                    threshold_kind=QueueThresholdKind.LENGTH,
                    queue_length=length,
                    queue_duration_seconds=duration,
                    estimated_wait_seconds=estimated,
                    timestamp=timestamp,
                    threshold_length=state.length_threshold,
                )
            )

        if (
            state.duration_threshold is not None
            and not state.duration_threshold_fired
            and length > 0
            and duration >= state.duration_threshold
        ):
            state.duration_threshold_fired = True
            events.append(
                QueueThresholdEvent(
                    camera_id=state.camera_id,
                    zone_id=state.zone_id,
                    zone_name=state.zone_name,
                    threshold_kind=QueueThresholdKind.DURATION,
                    queue_length=length,
                    queue_duration_seconds=duration,
                    estimated_wait_seconds=estimated,
                    timestamp=timestamp,
                    threshold_seconds=state.duration_threshold,
                )
            )

        if (
            state.length_threshold is not None
            and state.length_threshold_fired
            and length < state.length_threshold
        ):
            state.length_threshold_fired = False

        return tuple(events)

    def _build_snapshot(
        self,
        state: _ZoneQueueState,
        *,
        timestamp: float | None = None,
    ) -> QueueMetricsSnapshot:
        length = state.occupancy.snapshot().current_occupancy
        ts = timestamp if timestamp is not None else state.last_timestamp
        duration = self._episode_duration(state, ts) if ts is not None else 0.0

        return QueueMetricsSnapshot(
            zone_id=state.zone_id,
            zone_name=state.zone_name,
            camera_id=state.camera_id,
            current_queue_length=length,
            avg_queue_length=state.length_agg.avg_queue_length(),
            max_queue_length=state.length_agg.max_queue_length,
            estimated_wait_seconds=self._estimated_wait(state),
            queue_duration_seconds=duration,
            length_samples=state.length_agg.sample_count,
            completed_wait_samples=len(state.completed_waits),
        )
