"""Heatmap generation from tracking data (Module 8 / PRD §17).

Quick start
-----------
>>> from analytics.heatmaps import HeatmapEngine, HeatmapStore
>>> store = HeatmapStore("data/heatmaps", timezone="UTC")
>>> engine = HeatmapEngine("entrance", 640, 360, store=store)
>>> engine.set_reference_frame(empty_store_bgr_image)
>>> for tracks in pipeline:
...     engine.update(tracks, timestamp=frame_time)
>>> engine.flush()
>>> overlay = engine.render(start_dt, end_dt)
"""

from .accumulator import HeatmapAccumulator
from .engine import HeatmapEngine
from .renderer import render_heatmap_overlay
from .storage import HeatmapStore
from .types import HeatmapFrameSpec, HourBucketKey

__all__ = [
    "HeatmapFrameSpec",
    "HourBucketKey",
    "HeatmapAccumulator",
    "HeatmapStore",
    "HeatmapEngine",
    "render_heatmap_overlay",
]
