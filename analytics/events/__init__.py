"""Event architecture and Analytics Engine (Module 10, PRD §27).

Quick start
-----------
>>> from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, EventBus
>>> from analytics.counting import LineCounter
>>>
>>> bus = EventBus()
>>> engine = AnalyticsEngine(bus, AnalyticsEngineConfig(camera_ids=["entrance"]))
>>> counter = LineCounter(line, event_bus=bus)
>>> for crossing in counter.update(tracks):
...     pass  # occupancy updated via bus subscription
>>> engine.camera_occupancy("entrance").to_dict()
"""

from .adapters import (
    camera_offline_to_analytics,
    crossing_to_analytics,
    dwell_threshold_to_analytics,
    person_detected_to_analytics,
    queue_threshold_to_analytics,
    zone_to_analytics,
)
from .bus import EventBus
from .engine import AnalyticsEngine, AnalyticsEngineConfig
from .publisher import PersonDetectionSampler
from .types import AnalyticsEvent, AnalyticsEventType

__all__ = [
    "AnalyticsEvent",
    "AnalyticsEventType",
    "AnalyticsEngine",
    "AnalyticsEngineConfig",
    "EventBus",
    "PersonDetectionSampler",
    "camera_offline_to_analytics",
    "crossing_to_analytics",
    "dwell_threshold_to_analytics",
    "person_detected_to_analytics",
    "queue_threshold_to_analytics",
    "zone_to_analytics",
]
