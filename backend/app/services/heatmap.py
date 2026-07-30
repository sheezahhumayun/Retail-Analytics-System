"""Heatmap data service — reads Module 8 hour-bucket NPZ files (no CV deps)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from ..config import get_settings
from ..exceptions import ApiError
from ..schemas.analytics import HeatmapResponse, HeatmapSpec


@dataclass(frozen=True, slots=True)
class _BucketKey:
    camera_id: str
    day: date
    hour: int

    def path(self, root: Path) -> Path:
        return root / self.camera_id / self.day.isoformat() / f"{self.hour:02d}.npz"


def _load_bucket(path: Path) -> tuple[np.ndarray, np.ndarray, dict[str, int]] | None:
    if not path.is_file():
        return None
    data = np.load(path, allow_pickle=False)
    spec = {
        "width": int(data["spec_width"]),
        "height": int(data["spec_height"]),
        "grid_scale": int(data["spec_grid_scale"]),
    }
    return data["density"], data["trajectory"], spec


def _keys_in_range(
    root: Path,
    camera_id: str,
    start: datetime,
    end: datetime,
) -> list[_BucketKey]:
    keys: list[_BucketKey] = []
    cursor = start.replace(minute=0, second=0, microsecond=0)
    if cursor > start:
        cursor -= timedelta(hours=1)
    while cursor < end:
        keys.append(_BucketKey(camera_id=camera_id, day=cursor.date(), hour=cursor.hour))
        cursor += timedelta(hours=1)
    seen: set[tuple[str, str, int]] = set()
    unique: list[_BucketKey] = []
    for k in keys:
        sig = (k.camera_id, k.day.isoformat(), k.hour)
        if sig not in seen:
            seen.add(sig)
            unique.append(k)
    return unique


def fetch_heatmap(
    camera_id: str,
    metric_date: date,
    from_time: time,
    to_time: time,
) -> HeatmapResponse:
    if from_time > to_time:
        raise ApiError(
            400,
            "invalid_time_range",
            "from_time must be before or equal to to_time",
        )

    settings = get_settings()
    root = Path(settings.heatmap_data_dir)
    tz = ZoneInfo(settings.store_timezone) if settings.store_timezone != "UTC" else timezone.utc

    start = datetime.combine(metric_date, from_time, tzinfo=tz)
    end = datetime.combine(metric_date, to_time, tzinfo=tz)
    if end <= start:
        end = datetime.combine(metric_date, time(23, 59, 59), tzinfo=tz)

    merged_density: np.ndarray | None = None
    merged_trajectory: np.ndarray | None = None
    spec: dict[str, int] | None = None

    for key in _keys_in_range(root, camera_id, start, end):
        loaded = _load_bucket(key.path(root))
        if loaded is None:
            continue
        density, trajectory, bucket_spec = loaded
        if merged_density is None:
            merged_density = density.copy()
            merged_trajectory = trajectory.copy()
            spec = bucket_spec
        else:
            if bucket_spec != spec:
                continue
            merged_density += density
            merged_trajectory += trajectory

    if merged_density is None or merged_trajectory is None or spec is None:
        raise ApiError(
            404,
            "heatmap_not_found",
            f"No heatmap data for camera '{camera_id}' on {metric_date.isoformat()}",
            details={"camera_id": camera_id, "date": metric_date.isoformat()},
        )

    total_hits = float(merged_density.sum() + merged_trajectory.sum())
    return HeatmapResponse(
        camera_id=camera_id,
        date=metric_date.isoformat(),
        from_time=from_time.strftime("%H:%M:%S"),
        to_time=to_time.strftime("%H:%M:%S"),
        spec=HeatmapSpec(
            width=spec["width"],
            height=spec["height"],
            grid_scale=spec["grid_scale"],
        ),
        density=merged_density.tolist(),
        trajectory=merged_trajectory.tolist(),
        total_hits=total_hits,
    )
