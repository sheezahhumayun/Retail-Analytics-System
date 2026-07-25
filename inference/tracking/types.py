"""Tracking return types (PRD §11 contract).

PRD §11 requires temporary, anonymous track IDs so the same individual is
recognized across consecutive frames. :class:`TrackedObject` is the shape every
downstream module (counting, dwell, zones, heatmaps) consumes.

Position history is carried on each object so Module 4 (line-crossing direction)
and Module 7 (dwell) can reason about motion without re-querying a side store.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PositionRecord:
    """One point in a track's recent trajectory.

    Attributes
    ----------
    center:
        Centroid ``(cx, cy)`` in pixel coordinates (top-left origin).
    timestamp:
        Frame time as epoch seconds.
    bbox:
        ``(x1, y1, x2, y2)`` bounding box at this timestep.
    """

    center: tuple[float, float]
    timestamp: float
    bbox: tuple[float, float, float, float]


@dataclass(frozen=True, slots=True)
class TrackedObject:
    """One confirmed person track in one frame.

    Attributes
    ----------
    track_id:
        Anonymous, temporary ID assigned by the tracker. Not stable across
        cameras and may change after long occlusion (see README known
        limitations).
    bbox:
        ``(x1, y1, x2, y2)`` pixel coordinates in the input frame.
    class_id:
        COCO class id (``0`` = person after Module 2's default filter).
    class_name:
        Human-readable label (``"person"`` by default).
    confidence:
        Detection confidence for this frame's association.
    camera_id:
        Which camera/source produced the frame.
    timestamp:
        Frame time as epoch seconds.
    position_history:
        Recent trajectory, oldest → newest, capped at the tracker's
        ``history_length`` (default 30). Used by line-crossing and dwell
        modules for direction and duration checks.
    """

    track_id: int
    bbox: tuple[float, float, float, float]
    class_id: int
    class_name: str
    confidence: float
    camera_id: str
    timestamp: float
    position_history: tuple[PositionRecord, ...]

    @property
    def x1(self) -> float:
        return self.bbox[0]

    @property
    def y1(self) -> float:
        return self.bbox[1]

    @property
    def x2(self) -> float:
        return self.bbox[2]

    @property
    def y2(self) -> float:
        return self.bbox[3]

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    @property
    def center(self) -> tuple[float, float]:
        """Current-frame centroid ``(cx, cy)``."""
        return (
            (self.bbox[0] + self.bbox[2]) / 2.0,
            (self.bbox[1] + self.bbox[3]) / 2.0,
        )

    @property
    def age(self) -> int:
        """Number of stored positions in history (including the current frame)."""
        return len(self.position_history)


def freeze_history(
    buffer: deque[PositionRecord],
) -> tuple[PositionRecord, ...]:
    """Snapshot a mutable deque into the immutable tuple on :class:`TrackedObject`."""
    return tuple(buffer)
