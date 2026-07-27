"""Entry/exit counting types (PRD §12 / §27).

A :class:`CountingLine` is administrator-defined geometry in frame coordinates.
A :class:`CrossingEvent` is the first structured analytics event the platform
emits — Module 10 formalizes the bus; this module proves the schema in code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any


class InsideSide(str, Enum):
    """Which side of the directed line ``(x1, y1) → (x2, y2)`` is *inside*.

    "Left" and "right" follow the standard cross-product convention: stand at
    ``(x1, y1)`` facing ``(x2, y2)``; left is inside when ``inside_side`` is
    ``LEFT``.
    """

    LEFT = "left"
    RIGHT = "right"


class EventType(str, Enum):
    """PRD §27 entry/exit event types."""

    ENTRY = "ENTRY"
    EXIT = "EXIT"


@dataclass(frozen=True, slots=True)
class CountingLine:
    """Virtual counting line in frame pixel coordinates.

    Coordinates must match the downscaled frames from Module 1 (default 640px
    long side) — draw lines on the same resolution the pipeline processes.

    Attributes
    ----------
    x1, y1, x2, y2:
        Line endpoints in pixels (top-left origin).
    inside_side:
        Which side of the directed segment is considered "inside" the store.
    camera_id:
        Camera this line belongs to.
    name:
        Human-readable label (e.g. ``"main_entrance"``).
    """

    x1: float
    y1: float
    x2: float
    y2: float
    inside_side: InsideSide
    camera_id: str
    name: str = "line_1"

    @property
    def start(self) -> tuple[float, float]:
        return (self.x1, self.y1)

    @property
    def end(self) -> tuple[float, float]:
        return (self.x2, self.y2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "camera_id": self.camera_id,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "inside_side": self.inside_side.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CountingLine:
        return cls(
            x1=float(data["x1"]),
            y1=float(data["y1"]),
            x2=float(data["x2"]),
            y2=float(data["y2"]),
            inside_side=InsideSide(data["inside_side"]),
            camera_id=str(data["camera_id"]),
            name=str(data.get("name", "line_1")),
        )

    def save_json(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> CountingLine:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


@dataclass(frozen=True, slots=True)
class CrossingEvent:
    """Structured event emitted when a track crosses a counting line.

    Matches PRD §12 (camera, track, type, timestamp) and seeds the §27 event
    schema for Module 10.
    """

    camera_id: str
    track_id: int
    event_type: EventType
    timestamp: float
    line_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        """JSON-serializable dict (PRD §27 shape)."""
        return {
            "camera_id": self.camera_id,
            "track_id": str(self.track_id),
            "event_type": self.event_type.value,
            "timestamp": datetime.fromtimestamp(
                self.timestamp, tz=timezone.utc
            ).isoformat(),
        }
