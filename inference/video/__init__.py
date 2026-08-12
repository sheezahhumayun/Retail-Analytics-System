"""Video ingestion layer (Module 1).

A common frame-source interface so downstream modules (detect, track, analytics)
never depend on whether frames come from a file, an RTSP CCTV stream, or a
webcam. See :class:`VideoSource`.

Quick start
-----------
>>> from inference.video import create_video_source
>>> with create_video_source("sample-data/entrance.mp4") as src:
...     ok, frame = src.read()           # frame is already throttled + downscaled
...     print(src.get_fps(), src.get_resolution(), src.get_state().value)
"""

from .base import (
    DEFAULT_LONG_SIDE,
    DEFAULT_SOURCE_FPS_FALLBACK,
    DEFAULT_TARGET_FPS,
    CameraState,
    VideoSource,
    VideoSourceError,
    anchor_timestamp,
    compute_frame_interval,
    resize_long_side,
)
from .factory import create_video_source
from .file_source import FileVideoSource
from .rtsp_source import RTSPVideoSource
from .webcam_source import WebcamVideoSource

__all__ = [
    # Core interface
    "VideoSource",
    "VideoSourceError",
    "CameraState",
    # Implementations
    "FileVideoSource",
    "RTSPVideoSource",
    "WebcamVideoSource",
    # Construction
    "create_video_source",
    # Policy defaults + helpers
    "DEFAULT_TARGET_FPS",
    "DEFAULT_LONG_SIDE",
    "DEFAULT_SOURCE_FPS_FALLBACK",
    "resize_long_side",
    "compute_frame_interval",
    "anchor_timestamp",
]
