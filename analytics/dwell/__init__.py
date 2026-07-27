"""Dwell-time analytics layer (Module 7).

Measures how long tracked individuals remain in zones (PRD §16), consuming
Module 6 zone events.

Quick start
-----------
>>> from analytics.dwell import DwellTracker
>>> from analytics.zones import ZoneDetector
>>> dwell = DwellTracker(zones, dwell_thresholds={"electronics": 60.0})
>>> for event in zone_detector.update(tracks):
...     result = dwell.process(event)
...     if result.dwell_event:
...         print(result.dwell_event.to_dict())
...     if result.threshold_event:
...         print(result.threshold_event.to_dict())
>>> dwell.close_stale_sessions(current_timestamp=now)
"""

from .aggregates import DwellAggregator
from .tracker import DwellProcessResult, DwellTracker, MultiZoneDwellTracker
from .types import (
    DWELL_BUCKET_BOUNDS,
    DwellAggregatesSnapshot,
    DwellBucket,
    DwellCloseReason,
    DwellEvent,
    DwellThresholdEvent,
    dwell_bucket,
    empty_distribution,
)

__all__ = [
    # Types
    "DwellBucket",
    "DwellCloseReason",
    "DwellEvent",
    "DwellThresholdEvent",
    "DwellAggregatesSnapshot",
    "DwellProcessResult",
    "DWELL_BUCKET_BOUNDS",
    "dwell_bucket",
    "empty_distribution",
    # Tracking
    "DwellTracker",
    "MultiZoneDwellTracker",
    # Aggregates
    "DwellAggregator",
]
