"""Occupancy metrics types (PRD §13)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class OccupancyScope(str, Enum):
    """Where occupancy is measured — extensible for Module 6 zones."""

    CAMERA = "camera"
    STORE = "store"
    ZONE = "zone"


@dataclass(frozen=True, slots=True)
class OccupancySnapshot:
    """Point-in-time occupancy metrics for a camera, store, or zone.

    ``current_occupancy`` is derived as ``total_entries − total_exits`` (floored
    at zero when configured). On offline sample clips it is an *event-derived
    estimate*, not ground truth — see Module 5 README.
    """

    scope_id: str
    scope_type: OccupancyScope
    current_occupancy: int
    today_visitors: int
    today_exits: int
    peak_occupancy: int
    peak_occupancy_time: float | None
    total_entries: int
    total_exits: int

    def to_dict(self) -> dict[str, Any]:
        peak_iso: str | None = None
        if self.peak_occupancy_time is not None:
            peak_iso = datetime.fromtimestamp(
                self.peak_occupancy_time, tz=timezone.utc
            ).isoformat()
        return {
            "scope_id": self.scope_id,
            "scope_type": self.scope_type.value,
            "current_occupancy": self.current_occupancy,
            "today_visitors": self.today_visitors,
            "today_exits": self.today_exits,
            "peak_occupancy": self.peak_occupancy,
            "peak_occupancy_time": peak_iso,
            "total_entries": self.total_entries,
            "total_exits": self.total_exits,
        }
