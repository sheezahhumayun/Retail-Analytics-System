"""Queue analytics layer (Module 9).

Checkout/service queue metrics from Module 6 zone events (PRD §19).

Quick start
-----------
>>> from analytics.queues import QueueTracker, is_queue_zone
>>> from analytics.zones import Zone, ZoneDetector, ZoneType
>>> queue_zone = Zone(..., zone_type=ZoneType.QUEUE)
>>> queues = QueueTracker([queue_zone], length_thresholds={"lane_1": 5})
>>> for event in zone_detector.update(tracks):
...     result = queues.process(event)
...     if result.metrics:
...         print(result.metrics.to_dict())
...     for alert in result.threshold_events:
...         print(alert.to_dict())
"""

from .aggregates import QueueLengthAggregator
from .tracker import QueueProcessResult, QueueTracker
from .types import (
    QUEUE_ZONE_TYPES,
    QueueMetricsSnapshot,
    QueueThresholdEvent,
    QueueThresholdKind,
    is_queue_zone,
)

__all__ = [
    "QUEUE_ZONE_TYPES",
    "QueueLengthAggregator",
    "QueueMetricsSnapshot",
    "QueueProcessResult",
    "QueueThresholdEvent",
    "QueueThresholdKind",
    "QueueTracker",
    "is_queue_zone",
]
