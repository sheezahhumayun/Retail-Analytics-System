"""Dwell-time aggregate statistics from completed :class:`DwellEvent` records."""

from __future__ import annotations

import statistics

from .types import DwellAggregatesSnapshot, DwellEvent, dwell_bucket, empty_distribution


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


class DwellAggregator:
    """Compute avg / median / max / distribution from completed dwell events."""

    def __init__(self, zone_id: str, zone_name: str) -> None:
        self._zone_id = zone_id
        self._zone_name = zone_name
        self._dwells: list[float] = []
        self._distribution: dict[str, int] = empty_distribution()
        self._active_sessions = 0

    @property
    def zone_id(self) -> str:
        return self._zone_id

    def reset(self) -> None:
        self._dwells.clear()
        self._distribution = empty_distribution()
        self._active_sessions = 0

    def set_active_sessions(self, count: int) -> None:
        self._active_sessions = count

    def add(self, event: DwellEvent) -> None:
        if event.zone_id != self._zone_id:
            return
        seconds = max(0.0, event.dwell_seconds)
        self._dwells.append(seconds)
        bucket = dwell_bucket(seconds).value
        self._distribution[bucket] = self._distribution.get(bucket, 0) + 1

    def snapshot(self) -> DwellAggregatesSnapshot:
        if not self._dwells:
            return DwellAggregatesSnapshot(
                zone_id=self._zone_id,
                zone_name=self._zone_name,
                total_dwell_events=0,
                avg_dwell_seconds=0.0,
                median_dwell_seconds=0.0,
                max_dwell_seconds=0.0,
                distribution=dict(self._distribution),
                active_sessions=self._active_sessions,
            )
        return DwellAggregatesSnapshot(
            zone_id=self._zone_id,
            zone_name=self._zone_name,
            total_dwell_events=len(self._dwells),
            avg_dwell_seconds=sum(self._dwells) / len(self._dwells),
            median_dwell_seconds=_median(self._dwells),
            max_dwell_seconds=max(self._dwells),
            distribution=dict(self._distribution),
            active_sessions=self._active_sessions,
        )
