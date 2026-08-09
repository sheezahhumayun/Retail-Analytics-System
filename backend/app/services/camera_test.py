"""Lightweight camera stream connectivity test (Module 12.5)."""

from __future__ import annotations

import socket
import time
from pathlib import Path
from urllib.parse import urlparse

from ..schemas.extended.cameras import CameraTestResponse

from .opencv_io import opencv_io
from .opencv_rtsp import (
    apply_rtsp_ffmpeg_capture_options,
    open_rtsp_videocapture,
)

REPO_ROOT = Path(__file__).resolve().parents[3]


def recorded_source_file_exists(rtsp_url: str | None) -> bool:
    """True when a recorded camera's local source path resolves to a regular file."""
    if not rtsp_url:
        return False
    if not _is_local_path(rtsp_url):
        return False
    return _resolve_local_path(rtsp_url).is_file()


def test_camera_stream(rtsp_url: str | None, *, timeout: float = 5.0) -> CameraTestResponse:
    if not rtsp_url:
        return CameraTestResponse(status="error", message="No rtsp_url configured for this camera")

    started = time.perf_counter()

    if _is_local_path(rtsp_url):
        path = _resolve_local_path(rtsp_url)
        if not path.is_file():
            return CameraTestResponse(
                status="error",
                message=f"Local video file not found: {rtsp_url}",
            )
        latency_ms = int((time.perf_counter() - started) * 1000)
        resolution, fps = _probe_video_optional(path)
        return CameraTestResponse(
            status="success",
            latency_ms=latency_ms,
            resolution=resolution,
            fps=fps,
            message="Local file is readable",
        )

    parsed = urlparse(rtsp_url)
    if parsed.scheme.lower() in {"rtsp", "rtmp", "http", "https"}:
        host = parsed.hostname
        if not host:
            return CameraTestResponse(status="error", message="Invalid stream URL host")
        port = parsed.port or _default_port(parsed.scheme)
        try:
            with socket.create_connection((host, port), timeout=timeout):
                latency_ms = int((time.perf_counter() - started) * 1000)
        except OSError as exc:
            return CameraTestResponse(
                status="error",
                message=f"Could not reach {host}:{port} — {exc}",
            )
        resolution, fps = _probe_stream_optional(rtsp_url)
        return CameraTestResponse(
            status="success",
            latency_ms=latency_ms,
            resolution=resolution,
            fps=fps,
            message="Stream endpoint reachable",
        )

    return CameraTestResponse(status="error", message=f"Unsupported URL scheme: {rtsp_url}")


def _is_local_path(url: str) -> bool:
    return "://" not in url and not url.startswith("rtsp:")


def _resolve_local_path(url: str) -> Path:
    path = Path(url)
    if path.is_file():
        return path
    return REPO_ROOT / url


def _default_port(scheme: str) -> int:
    scheme = scheme.lower()
    if scheme == "rtsp":
        return 554
    if scheme == "rtmp":
        return 1935
    if scheme == "https":
        return 443
    return 80


def _probe_video_optional(path: Path) -> tuple[str | None, float | None]:
    try:
        import cv2  # type: ignore[import-untyped]

        with opencv_io():
            cap = cv2.VideoCapture(str(path))
            try:
                if not cap.isOpened():
                    return None, None
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = float(cap.get(cv2.CAP_PROP_FPS)) or None
                resolution = f"{width}x{height}" if width and height else None
                return resolution, fps
            finally:
                cap.release()
    except ImportError:
        return None, None


def _probe_stream_optional(url: str) -> tuple[str | None, float | None]:
    try:
        import cv2  # type: ignore[import-untyped]

        with opencv_io():
            apply_rtsp_ffmpeg_capture_options()
            cap = open_rtsp_videocapture(url)
            try:
                if not cap.isOpened():
                    return None, None
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = float(cap.get(cv2.CAP_PROP_FPS)) or None
                resolution = f"{width}x{height}" if width and height else None
                return resolution, fps
            finally:
                cap.release()
    except ImportError:
        return None, None
