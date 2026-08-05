"""Shared RTSP open/read timeout values for OpenCV FFmpeg capture."""

from __future__ import annotations

# Bound how long a single OpenCV/FFmpeg open/read can block (ms).
RTSP_OPEN_READ_TIMEOUT_MS = 5000
RTSP_OPEN_READ_TIMEOUT_SEC = RTSP_OPEN_READ_TIMEOUT_MS // 1000


def rtsp_videocapture_open_params() -> list[int]:
    """OpenCV FFmpeg ``(open-only)`` timeout params for ``VideoCapture(url, api, params)``."""
    import cv2

    return [
        cv2.CAP_PROP_OPEN_TIMEOUT_MSEC,
        RTSP_OPEN_READ_TIMEOUT_MS,
        cv2.CAP_PROP_READ_TIMEOUT_MSEC,
        RTSP_OPEN_READ_TIMEOUT_MS,
    ]


def configure_rtsp_videocapture_timeouts(cap) -> tuple[bool, bool | None]:
    """Attempt ``cap.set`` timeouts (may be ignored by FFmpeg backend).

    On OpenCV 4.10 + ``CAP_FFMPEG``, these properties are ``(open-only)`` and
  must be supplied via :func:`rtsp_videocapture_open_params` at construction.
    Returns ``(open_timeout_set_ok, read_timeout_set_ok)``.
    """
    import cv2

    open_ok = bool(cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, RTSP_OPEN_READ_TIMEOUT_MS))
    read_ok: bool | None = None
    read_timeout_prop = getattr(cv2, "CAP_PROP_READ_TIMEOUT_MSEC", None)
    if read_timeout_prop is not None:
        read_ok = bool(cap.set(read_timeout_prop, RTSP_OPEN_READ_TIMEOUT_MS))
    return open_ok, read_ok


def open_rtsp_videocapture(url: str):
    """Open an FFmpeg ``VideoCapture`` with shared 5s open/read watchdog timeouts."""
    import cv2

    return cv2.VideoCapture(url, cv2.CAP_FFMPEG, rtsp_videocapture_open_params())
