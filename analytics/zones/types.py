"""Zone management types (PRD §14 / §15).

:class:`Zone` is administrator-defined polygon geometry in frame coordinates.
:class:`ZoneEvent` is emitted on entry, exit, and per-frame presence inside a
zone — the presence stream feeds dwell-time analytics (Module 7).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class ZoneType(str, Enum):
    """Semantic label for a zone (PRD §14 examples)."""

    ENTRANCE = "entrance"
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    GROCERY = "grocery"
    PROMOTIONAL = "promotional"
    CHECKOUT = "checkout"
    WAITING = "waiting"
    QUEUE = "queue"
    GENERAL = "general"


class ZoneEventType(str, Enum):
    """Zone transition and presence events."""

    ZONE_ENTER = "ZONE_ENTER"
    ZONE_EXIT = "ZONE_EXIT"
    ZONE_PRESENCE = "ZONE_PRESENCE"


@dataclass(frozen=True, slots=True)
class Zone:
    """Polygon-based analytics zone in frame pixel coordinates.

    Coordinates must match the downscaled frames from Module 1 (default 640px
    long side) — draw zones on the same resolution the pipeline processes.

    Attributes
    ----------
    zone_id:
        Stable identifier (e.g. ``"electronics_1"``).
    zone_name:
        Human-readable label (e.g. ``"Electronics"``).
    camera_id:
        Camera this zone belongs to.
    polygon_coordinates:
        Closed polygon vertices ``(x, y)`` in pixels (top-left origin). The
        polygon is implicitly closed — the last vertex connects back to the
        first.
    zone_type:
        Semantic category for reporting.
    analytics_enabled:
        When ``False``, the zone is stored but not evaluated at runtime.
    """

    zone_id: str
    zone_name: str
    camera_id: str
    polygon_coordinates: tuple[tuple[float, float], ...]
    zone_type: ZoneType = ZoneType.GENERAL
    analytics_enabled: bool = True

    def __post_init__(self) -> None:
        if len(self.polygon_coordinates) < 3:
            raise ValueError("polygon_coordinates requires at least 3 points")

    def to_dict(self) -> dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "camera_id": self.camera_id,
            "polygon_coordinates": [
                [float(x), float(y)] for x, y in self.polygon_coordinates
            ],
            "zone_type": self.zone_type.value,
            "analytics_enabled": self.analytics_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Zone:
        raw_pts = data["polygon_coordinates"]
        coords = tuple((float(p[0]), float(p[1])) for p in raw_pts)
        return cls(
            zone_id=str(data["zone_id"]),
            zone_name=str(data["zone_name"]),
            camera_id=str(data["camera_id"]),
            polygon_coordinates=coords,
            zone_type=ZoneType(data.get("zone_type", ZoneType.GENERAL.value)),
            analytics_enabled=bool(data.get("analytics_enabled", True)),
        )

    def save_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> Zone:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


@dataclass(frozen=True, slots=True)
class ZoneConfig:
    """All zones configured for one camera."""

    camera_id: str
    zones: tuple[Zone, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "camera_id": self.camera_id,
            "zones": [z.to_dict() for z in self.zones],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ZoneConfig:
        camera_id = str(data["camera_id"])
        zones = tuple(Zone.from_dict(z) for z in data["zones"])
        return cls(camera_id=camera_id, zones=zones)

    def save_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> ZoneConfig:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    @property
    def enabled_zones(self) -> tuple[Zone, ...]:
        return tuple(z for z in self.zones if z.analytics_enabled)


@dataclass(frozen=True, slots=True)
class ZoneEvent:
    """Structured event emitted for zone entry, exit, or presence."""

    camera_id: str
    zone_id: str
    zone_name: str
    track_id: int
    event_type: ZoneEventType
    timestamp: float
    dwell_delta: float | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "camera_id": self.camera_id,
            "zone_id": self.zone_id,
            "zone_name": self.zone_name,
            "track_id": str(self.track_id),
            "event_type": self.event_type.value,
            "timestamp": datetime.fromtimestamp(
                self.timestamp, tz=timezone.utc
            ).isoformat(),
        }
        if self.dwell_delta is not None:
            out["dwell_delta"] = self.dwell_delta
        return out
