"""Entry/exit counting layer (Module 4).

Virtual counting lines that emit structured ENTRY/EXIT events when tracked
people cross them (PRD §12 / §27).

Quick start
-----------
>>> from analytics.counting import CountingLine, InsideSide, LineCounter
>>> line = CountingLine(100, 200, 500, 200, InsideSide.RIGHT, camera_id="entrance")
>>> counter = LineCounter(line)
>>> events = counter.update(tracks)  # list[CrossingEvent]
>>> events[0].to_dict()
{'camera_id': 'entrance', 'track_id': '7', 'event_type': 'ENTRY', 'timestamp': '...'}
"""

from .counter import LineCounter
from .geometry import (
    foot_point_from_bbox,
    is_inside,
    movement_crosses_line,
    point_side,
    segments_intersect,
    tracking_point_from_bbox,
)
from .types import CountingLine, CrossingEvent, EventType, InsideSide

__all__ = [
    # Types
    "CountingLine",
    "InsideSide",
    "CrossingEvent",
    "EventType",
    # Counter
    "LineCounter",
    # Geometry helpers (re-exported for tests / zone reuse)
    "foot_point_from_bbox",
    "tracking_point_from_bbox",
    "is_inside",
    "movement_crosses_line",
    "point_side",
    "segments_intersect",
]
