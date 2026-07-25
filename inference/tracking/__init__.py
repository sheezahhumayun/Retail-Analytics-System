"""Multi-object tracking layer (Module 3).

Assigns temporary, anonymous track IDs to detected people so downstream modules
call ``tracker.update(detections)`` and never depend on the underlying tracker
implementation.

Quick start
-----------
>>> from inference.detection import create_detector
>>> from inference.tracking import Tracker
>>> tracker = Tracker(camera_id="entrance")
>>> with create_detector() as det:
...     detections = det.detect(frame, camera_id="entrance")
...     tracks = tracker.update(detections)
...     print(len(tracks), "confirmed tracks")
"""

from .tracker import (
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_FRAME_RATE,
    DEFAULT_HIGH_CONF_DET_THRESHOLD,
    DEFAULT_HISTORY_LENGTH,
    DEFAULT_MIN_CONFIRMATION_FRAMES,
    DEFAULT_MIN_MATCHING_IOU,
    DEFAULT_NMS_IOU_THRESHOLD,
    DEFAULT_TRACK_ACTIVATION_THRESHOLD,
    DEFAULT_TRACK_BUFFER,
    Tracker,
)
from .types import PositionRecord, TrackedObject

__all__ = [
    # Interface + types
    "Tracker",
    "TrackedObject",
    "PositionRecord",
    # Defaults
    "DEFAULT_CONF_THRESHOLD",
    "DEFAULT_NMS_IOU_THRESHOLD",
    "DEFAULT_TRACK_BUFFER",
    "DEFAULT_FRAME_RATE",
    "DEFAULT_MIN_CONFIRMATION_FRAMES",
    "DEFAULT_HISTORY_LENGTH",
    "DEFAULT_TRACK_ACTIVATION_THRESHOLD",
    "DEFAULT_HIGH_CONF_DET_THRESHOLD",
    "DEFAULT_MIN_MATCHING_IOU",
]
