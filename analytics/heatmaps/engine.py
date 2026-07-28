"""Heatmap engine — accumulate tracks, bucket by hour, render overlays (PRD §17)."""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from analytics.counting.geometry import foot_point_from_bbox
from inference.tracking.types import TrackedObject

from .accumulator import HeatmapAccumulator
from .renderer import render_heatmap_overlay
from .storage import HeatmapStore, _normalize_timezone
from .types import HeatmapFrameSpec, HourBucketKey


class HeatmapEngine:
    """Accumulate foot-points and trajectories; persist per-hour; render overlays.

    Parameters
    ----------
    camera_id:
        Camera identifier for bucket keys.
    frame_width, frame_height:
        Processed frame size (must match reference frame and track coordinates).
    grid_scale:
        Accumulator resolution divisor (default 4 → 1/4 grid).
    store:
        Optional :class:`HeatmapStore` for hour-bucket persistence.
    timezone:
        IANA timezone for hour-bucket boundaries.
    """

    def __init__(
        self,
        camera_id: str,
        frame_width: int,
        frame_height: int,
        *,
        grid_scale: int = 4,
        store: HeatmapStore | None = None,
        timezone: str | ZoneInfo | dt_timezone = dt_timezone.utc,
    ) -> None:
        self._camera_id = camera_id
        self._spec = HeatmapFrameSpec(frame_width, frame_height, grid_scale)
        self._store = store
        self._tz = _normalize_timezone(timezone)

        self._reference_frame: np.ndarray | None = None
        self._live = HeatmapAccumulator(self._spec)
        self._current_key: HourBucketKey | None = None
        self._last_segment_ts: dict[int, float] = {}

    @property
    def camera_id(self) -> str:
        return self._camera_id

    @property
    def spec(self) -> HeatmapFrameSpec:
        return self._spec

    @property
    def reference_frame(self) -> np.ndarray | None:
        return self._reference_frame

    def set_reference_frame(self, frame: np.ndarray) -> None:
        """Store a static BGR reference (empty store) for overlay rendering."""
        h, w = frame.shape[:2]
        if (w, h) != (self._spec.width, self._spec.height):
            raise ValueError(
                f"reference frame {w}x{h} must match engine spec "
                f"{self._spec.width}x{self._spec.height}"
            )
        self._reference_frame = frame.copy()

    def update(self, tracks: list[TrackedObject], timestamp: float) -> None:
        """Accumulate foot-points and trajectory segments for ``timestamp``."""
        self._roll_hour_bucket(timestamp)

        for track in tracks:
            if track.camera_id != self._camera_id:
                continue
            fx, fy = foot_point_from_bbox(track.bbox)
            self._live.add_point(fx, fy)

            history = track.position_history
            if len(history) < 2:
                continue
            last_ts = history[-1].timestamp
            if self._last_segment_ts.get(track.track_id) == last_ts:
                continue
            p1 = foot_point_from_bbox(history[-2].bbox)
            p2 = foot_point_from_bbox(history[-1].bbox)
            self._live.add_segment(p1[0], p1[1], p2[0], p2[1])
            self._last_segment_ts[track.track_id] = last_ts

    def flush(self) -> None:
        """Persist the in-memory hour bucket (merged into any existing file)."""
        if self._store is None or self._current_key is None:
            return
        if self._live.total_hits() <= 0:
            return
        existing = self._store.load(self._current_key)
        if existing is not None:
            existing.merge_inplace(self._live)
            self._store.save(self._current_key, existing)
        else:
            self._store.save(self._current_key, self._live)
        self._live.clear()

    def render(
        self,
        start: datetime | None = None,
        end: datetime | None = None,
        *,
        include_live: bool = True,
        **render_kwargs,
    ) -> np.ndarray:
        """Render heatmap overlay for a time range (or live buffer if no range)."""
        if self._reference_frame is None:
            raise RuntimeError("set_reference_frame() before render()")

        acc: HeatmapAccumulator | None = None
        if start is not None and end is not None and self._store is not None:
            acc = self._store.merge_range(self._camera_id, start, end)
        if include_live and self._live.total_hits() > 0:
            live = self._live.copy()
            if acc is None:
                acc = live
            else:
                acc.merge_inplace(live)
        if acc is None and self._store is not None and self._current_key is not None:
            acc = self._store.load(self._current_key)
        if acc is None:
            acc = HeatmapAccumulator(self._spec)

        return render_heatmap_overlay(
            acc,
            self._reference_frame,
            **render_kwargs,
        )

    def _roll_hour_bucket(self, timestamp: float) -> None:
        dt = datetime.fromtimestamp(timestamp, tz=self._tz)
        key = HourBucketKey.from_datetime(self._camera_id, dt)
        if key == self._current_key:
            return
        if self._current_key is not None:
            self.flush()
        self._current_key = key
        self._live.clear()
        self._last_segment_ts.clear()
