"""Persist heatmap accumulators per camera per hour bucket (PRD §17 / §31)."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone as dt_timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np

from .accumulator import HeatmapAccumulator
from .types import HourBucketKey


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


class HeatmapStore:
    """File-backed hour-bucket storage for heatmap accumulators.

    Layout::

        {root}/{camera_id}/{YYYY-MM-DD}/{HH}.npz

    Each file stores ``density``, ``trajectory``, and frame ``spec`` metadata.
    Summing buckets for a time range avoids reprocessing video (PRD §31).
    """

    def __init__(self, root_dir: str | Path, *, timezone: str | ZoneInfo | dt_timezone = dt_timezone.utc) -> None:
        self._root = Path(root_dir)
        self._tz = _normalize_timezone(timezone)

    @property
    def root(self) -> Path:
        return self._root

    @property
    def timezone(self) -> ZoneInfo | dt_timezone:
        return self._tz

    def bucket_path(self, key: HourBucketKey) -> Path:
        cam, day, hour = key.to_path_parts()
        return self._root / cam / day / f"{hour}.npz"

    def save(self, key: HourBucketKey, accumulator: HeatmapAccumulator) -> Path:
        path = self.bucket_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        arrays = accumulator.to_arrays()
        np.savez_compressed(
            path,
            density=arrays["density"],
            trajectory=arrays["trajectory"],
            spec_width=np.int32(arrays["spec"]["width"]),
            spec_height=np.int32(arrays["spec"]["height"]),
            spec_grid_scale=np.int32(arrays["spec"]["grid_scale"]),
            meta=json.dumps(key.to_dict()),
        )
        return path

    def load(self, key: HourBucketKey) -> HeatmapAccumulator | None:
        path = self.bucket_path(key)
        if not path.is_file():
            return None
        data = np.load(path, allow_pickle=False)
        spec = {
            "width": int(data["spec_width"]),
            "height": int(data["spec_height"]),
            "grid_scale": int(data["spec_grid_scale"]),
        }
        return HeatmapAccumulator.from_arrays(
            {
                "density": data["density"],
                "trajectory": data["trajectory"],
                "spec": spec,
            }
        )

    def list_keys(self, camera_id: str) -> list[HourBucketKey]:
        cam_dir = self._root / camera_id
        if not cam_dir.is_dir():
            return []
        keys: list[HourBucketKey] = []
        for day_dir in sorted(cam_dir.iterdir()):
            if not day_dir.is_dir():
                continue
            try:
                day = date.fromisoformat(day_dir.name)
            except ValueError:
                continue
            for npz in sorted(day_dir.glob("*.npz")):
                hour = int(npz.stem)
                keys.append(HourBucketKey(camera_id=camera_id, day=day, hour=hour))
        return keys

    def keys_in_range(
        self,
        camera_id: str,
        start: datetime,
        end: datetime,
    ) -> list[HourBucketKey]:
        """Return hour buckets overlapping ``[start, end)`` in store timezone."""
        if start.tzinfo is None:
            start = start.replace(tzinfo=self._tz)
        else:
            start = start.astimezone(self._tz)
        if end.tzinfo is None:
            end = end.replace(tzinfo=self._tz)
        else:
            end = end.astimezone(self._tz)

        keys: list[HourBucketKey] = []
        cursor = start.replace(minute=0, second=0, microsecond=0)
        if cursor > start:
            cursor -= timedelta(hours=1)
        while cursor < end:
            keys.append(HourBucketKey.from_datetime(camera_id, cursor))
            cursor += timedelta(hours=1)
        # Deduplicate while preserving order
        seen: set[tuple[str, str, int]] = set()
        unique: list[HourBucketKey] = []
        for k in keys:
            sig = (k.camera_id, k.day.isoformat(), k.hour)
            if sig not in seen:
                seen.add(sig)
                unique.append(k)
        return unique

    def merge_range(
        self,
        camera_id: str,
        start: datetime,
        end: datetime,
        *,
        base_spec: HeatmapAccumulator | None = None,
    ) -> HeatmapAccumulator | None:
        """Load and sum all hour buckets in ``[start, end)``."""
        keys = self.keys_in_range(camera_id, start, end)
        merged: HeatmapAccumulator | None = None
        for key in keys:
            acc = self.load(key)
            if acc is None:
                continue
            if merged is None:
                merged = acc.copy()
            elif acc.spec != merged.spec:
                continue
            else:
                merged.merge_inplace(acc)
        return merged if merged is not None else base_spec
