"""Zone management and zone analytics (Module 6).

Polygon-based zones with entry/exit/presence detection and analytics
(PRD §14–§15).

Quick start
-----------
>>> from analytics.zones import Zone, ZoneDetector, ZoneAnalytics
>>> zone = Zone(
...     zone_id="electronics",
...     zone_name="Electronics",
...     camera_id="store-floor",
...     polygon_coordinates=((50, 100), (300, 100), (300, 350), (50, 350)),
... )
>>> detector = ZoneDetector([zone])
>>> analytics = ZoneAnalytics(zone)
>>> for event in detector.update(tracks):
...     snap = analytics.process(event)
...     print(event.to_dict(), snap.to_dict())
"""

from .analytics import MultiZoneAnalytics, ZoneAnalytics, ZoneAnalyticsSnapshot
from .detector import ZoneDetector
from .geometry import foot_point_from_bbox, is_inside_zone, point_in_polygon
from .types import Zone, ZoneConfig, ZoneEvent, ZoneEventType, ZoneType
from .verify import (
    FlapWarning,
    TransitionRecord,
    detect_flapping,
    event_counts,
    extract_transitions,
    format_transition_timeline,
)

__all__ = [
    # Types
    "Zone",
    "ZoneConfig",
    "ZoneType",
    "ZoneEvent",
    "ZoneEventType",
    # Detection
    "ZoneDetector",
    # Analytics
    "ZoneAnalytics",
    "ZoneAnalyticsSnapshot",
    "MultiZoneAnalytics",
    # Verification
    "TransitionRecord",
    "FlapWarning",
    "event_counts",
    "extract_transitions",
    "detect_flapping",
    "format_transition_timeline",
    # Geometry
    "foot_point_from_bbox",
    "point_in_polygon",
    "is_inside_zone",
]
