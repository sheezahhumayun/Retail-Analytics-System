"""MJPEG live-camera stream service (Phase 1a preview)."""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import TYPE_CHECKING

import cv2

from inference.video import create_video_source
from inference.video.base import CameraState, VideoSource, VideoSourceError

from .opencv_io import opencv_io
from .opencv_rtsp import RTSP_OPEN_READ_TIMEOUT_SEC

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[3]

MJPEG_BOUNDARY = "frame"
MJPEG_CONTENT_TYPE = f"multipart/x-mixed-replace; boundary={MJPEG_BOUNDARY}"

# Target preview rate — matches VideoSource default policy.
STREAM_TARGET_FPS = 10.0
STREAM_LONG_SIDE = 640
STREAM_JPEG_QUALITY = 80

# How long to wait for the first decodable frame before failing the request.
OPEN_FRAME_TIMEOUT_SEC = 15.0
OPEN_FRAME_POLL_SEC = 0.1

# Stop a live preview if no frame arrives within this window mid-stream.
# Secondary safety net only — primary bound is STREAM_RTSP_RECONNECT_* fast-fail
# (~5s read + ~5s single reopen ≈ 10s before CameraState.ERROR).
LIVE_STREAM_STALL_TIMEOUT_SEC = 15.0

_LIVE_SCHEMES = ("rtsp://", "rtsps://", "rtmp://")

# MJPEG preview-only RTSP reconnect profile. RTSPVideoSource defaults (threshold=5,
# attempts=5, 1/2/4/8/16s backoff, 60s retry-after-exhaustion) remain for
# inference pipelines, demos, and other long-running callers.
STREAM_RTSP_RECONNECT_KWARGS: dict = {
    "reconnect_threshold": 1,  # reconnect after first failed read, not five ~5s reads
    "reconnect_attempts": 1,  # one reopen try (~5s open timeout), not five
    "backoff_base": 0.0,
    "backoff_max": 0.0,  # no 1+2+4+8+16s sleeps inside _reconnect()
    "retry_after_exhaustion": 5.0,  # cap=None retry cadence, not 60s
}


class StreamOpenError(RuntimeError):
    """Raised when the stream cannot be opened or produces no initial frame."""


def resolve_stream_spec(url: str) -> str:
    """Resolve repo-relative file paths used by seed/demo cameras."""
    path = Path(url)
    if path.is_file():
        return str(path)
    candidate = REPO_ROOT / url
    if candidate.is_file():
        return str(candidate)
    return url


def _is_network_stream(spec: str) -> bool:
    lowered = spec.strip().lower()
    return lowered.startswith(_LIVE_SCHEMES)


def create_stream_source(rtsp_url: str) -> VideoSource:
    """Build a :class:`VideoSource` for preview streaming."""
    resolved = resolve_stream_spec(rtsp_url)
    kwargs: dict = {}
    if not _is_network_stream(resolved):
        kwargs["loop"] = True
    else:
        kwargs["timeout_sec"] = RTSP_OPEN_READ_TIMEOUT_SEC
        kwargs.update(STREAM_RTSP_RECONNECT_KWARGS)
    return create_video_source(
        resolved,
        target_fps=STREAM_TARGET_FPS,
        target_long_side=STREAM_LONG_SIDE,
        **kwargs,
    )


def _encode_jpeg_bytes(frame: np.ndarray) -> bytes:
    ok, jpeg = cv2.imencode(
        ".jpg",
        frame,
        [int(cv2.IMWRITE_JPEG_QUALITY), STREAM_JPEG_QUALITY],
    )
    if not ok:
        raise StreamOpenError("Failed to encode frame as JPEG")
    return jpeg.tobytes()


def _encode_jpeg_chunk(frame: np.ndarray) -> bytes:
    jpeg = _encode_jpeg_bytes(frame)
    header = (
        f"--{MJPEG_BOUNDARY}\r\n"
        "Content-Type: image/jpeg\r\n"
        f"Content-Length: {len(jpeg)}\r\n\r\n"
    ).encode("ascii")
    return header + jpeg + b"\r\n"


def capture_snapshot_jpeg(rtsp_url: str) -> bytes:
    """Open a live source, read one frame, and return raw JPEG bytes."""
    source = create_stream_source(rtsp_url)
    deadline = time.monotonic() + OPEN_FRAME_TIMEOUT_SEC
    try:
        with opencv_io():
            source.open()
        while time.monotonic() < deadline:
            with opencv_io():
                ok, frame = source.read()
            if ok and frame is not None:
                jpeg = _encode_jpeg_bytes(frame)
                release_stream_source(source)
                return jpeg
            time.sleep(OPEN_FRAME_POLL_SEC)
    except VideoSourceError as exc:
        release_stream_source(source)
        raise StreamOpenError(str(exc)) from exc

    release_stream_source(source)
    raise StreamOpenError("Could not read an initial frame from the camera stream")


def open_stream_source(rtsp_url: str) -> tuple[VideoSource, bytes]:
    """Open the source and return it together with the first MJPEG chunk."""
    source = create_stream_source(rtsp_url)
    deadline = time.monotonic() + OPEN_FRAME_TIMEOUT_SEC
    try:
        with opencv_io():
            source.open()
        while time.monotonic() < deadline:
            with opencv_io():
                ok, frame = source.read()
            if ok and frame is not None:
                return source, _encode_jpeg_chunk(frame)
            time.sleep(OPEN_FRAME_POLL_SEC)
    except VideoSourceError as exc:
        release_stream_source(source)
        raise StreamOpenError(str(exc)) from exc

    release_stream_source(source)
    raise StreamOpenError("Could not read an initial frame from the camera stream")


def release_stream_source(source: VideoSource) -> None:
    with opencv_io():
        source.release()


def _live_stream_lost(source: VideoSource, last_frame_at: float) -> bool:
    """True when a live source has stopped producing frames mid-stream."""
    if source.get_state() == CameraState.ERROR:
        return True
    return time.monotonic() - last_frame_at >= LIVE_STREAM_STALL_TIMEOUT_SEC


def read_stream_frame(source: VideoSource) -> tuple[bool, "np.ndarray | None"]:
    """Blocking :meth:`VideoSource.read` — must run off the event loop."""
    with opencv_io():
        return source.read()


async def async_iter_open_mjpeg_stream(
    source: VideoSource,
    first_chunk: bytes,
    *,
    camera_id: str | None = None,
) -> AsyncIterator[bytes]:
    """Yield MJPEG chunks from an already-open source."""
    stream_lost = False
    try:
        yield first_chunk
        last_frame_at = time.monotonic()

        frame_interval = 1.0 / STREAM_TARGET_FPS
        while True:
            loop_start = time.monotonic()
            ok, frame = await asyncio.to_thread(read_stream_frame, source)
            if not ok or frame is None:
                if source.is_live():
                    if _live_stream_lost(source, last_frame_at):
                        stream_lost = True
                        break
                    await asyncio.sleep(OPEN_FRAME_POLL_SEC)
                    continue
                break
            last_frame_at = time.monotonic()
            yield _encode_jpeg_chunk(frame)
            elapsed = time.monotonic() - loop_start
            sleep_for = frame_interval - elapsed
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
    except GeneratorExit:
        return
    finally:
        await asyncio.to_thread(release_stream_source, source)
        if stream_lost and camera_id:
            from .camera_health import persist_camera_stream_error

            try:
                if persist_camera_stream_error(camera_id):
                    logger.warning(
                        "Live MJPEG stream lost for camera %s — "
                        "persisted status=error and closed preview connection",
                        camera_id,
                    )
            except Exception:
                logger.exception(
                    "Failed to persist error status for camera %s after stream loss",
                    camera_id,
                )
