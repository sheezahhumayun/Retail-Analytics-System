"""Shared RTSP timeout settings for backend OpenCV/FFmpeg capture."""

from __future__ import annotations

import os

from inference.video.rtsp_timeouts import (
    RTSP_OPEN_READ_TIMEOUT_MS,
    RTSP_OPEN_READ_TIMEOUT_SEC,
    configure_rtsp_videocapture_timeouts,
    open_rtsp_videocapture,
    rtsp_videocapture_open_params,
)

__all__ = [
    "RTSP_OPEN_READ_TIMEOUT_MS",
    "RTSP_OPEN_READ_TIMEOUT_SEC",
    "apply_rtsp_ffmpeg_capture_options",
    "configure_rtsp_videocapture_timeouts",
    "open_rtsp_videocapture",
    "rtsp_videocapture_open_params",
]


def apply_rtsp_ffmpeg_capture_options() -> None:
    """Set FFmpeg options to match :class:`RTSPVideoSource` ``timeout_sec``."""
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
        f"rtsp_transport;tcp|stimeout;{RTSP_OPEN_READ_TIMEOUT_SEC * 1000}"
    )
