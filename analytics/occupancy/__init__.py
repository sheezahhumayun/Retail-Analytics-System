"""Occupancy analytics layer (Module 5).

First pure analytics module — computes dashboard metrics from Module 4
ENTRY/EXIT events (PRD §13). No computer vision; preview of Module 10.

Quick start
-----------
>>> from analytics.counting import LineCounter, EventType
>>> from analytics.occupancy import OccupancyTracker
>>> occupancy = OccupancyTracker("entrance")
>>> for event in counter.update(tracks):
...     snap = occupancy.process(event)
...     print(snap.current_occupancy, snap.today_visitors)
"""

from .aggregator import StoreOccupancyAggregator
from .tracker import OccupancyTracker
from .types import OccupancyScope, OccupancySnapshot

__all__ = [
    "OccupancyScope",
    "OccupancySnapshot",
    "OccupancyTracker",
    "StoreOccupancyAggregator",
]
