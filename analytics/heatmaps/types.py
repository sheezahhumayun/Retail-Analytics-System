"""Heatmap types (PRD §17)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class HeatmapFrameSpec:
    """Processing-frame dimensions the accumulator aligns to.

    Foot-points and trajectories are recorded in these pixel coordinates
    (Module 1 downscaled output, default 640px long side).
    """

    width: int
    height: int
    grid_scale: int = 4

    @property
    def grid_width(self) -> int:
        return max(1, self.width // self.grid_scale)

    @property
    def grid_height(self) -> int:
        return max(1, self.height // self.grid_scale)


@dataclass(frozen=True, slots=True)
class HourBucketKey:
    """Persisted accumulator identity — one bucket per camera per local hour."""

    camera_id: str
    day: date
    hour: int

    def to_path_parts(self) -> tuple[str, str, str]:
        return (self.camera_id, self.day.isoformat(), f"{self.hour:02d}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "day": self.day.isoformat(),
            "hour": self.hour,
        }

    @classmethod
    def from_datetime(cls, camera_id: str, dt: datetime) -> HourBucketKey:
        return cls(camera_id=camera_id, day=dt.date(), hour=dt.hour)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HourBucketKey:
        return cls(
            camera_id=str(data["camera_id"]),
            day=date.fromisoformat(str(data["day"])),
            hour=int(data["hour"]),
        )
