"""RTSP video source with reconnect-on-failure.

Real CCTV/NVR RTSP streams drop intermittently — this is *normal operation*,
not an edge case. The task description is explicit: ``read()`` must detect N
consecutive failures, back off, and reopen, rather than dying or spamming
reconnect attempts. PRD §8's camera "Error"/"Offline" states depend on those
transitions being surfaced reliably here.

Behaviour
---------
* Opened via OpenCV's FFMPEG backend (the same backend proven on the sample
  files in Module 0). If OpenCV's RTSP handling proves flaky on a particular
  NVR, the :func:`create_video_source` factory / this class can be swapped to
  GStreamer (``CAP_GSTREAMER``) or ``ffmpeg-python`` without touching any
  downstream module.
* A read timeout is passed via ``OPENCV_FFMPEG_CAPTURE_OPTIONS`` so a dead
  NVR doesn't hang the whole pipeline.
* After ``reconnect_threshold`` consecutive failed reads, we release and
  reopen with exponential backoff (capped at ``backoff_max`` seconds). During
* :meth:`read` returns ``(False, None)`` during reconnect attempts and never
  raises on transient drops — callers just keep calling.
"""

from __future__ import annotations

import math
import os
import time
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from .base import (
    DEFAULT_LONG_SIDE,
    DEFAULT_SOURCE_FPS_FALLBACK,
    DEFAULT_TARGET_FPS,
    CameraState,
    VideoSource,
    VideoSourceError,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    import numpy as np

    from analytics.events.bus import EventBus


# Default RTSP transport. TCP avoids the packet loss / tearing artefacts common
# with UDP RTSP over Wi-Fi and is the safest default for NVRs.
DEFAULT_RTSP_TRANSPORT = "tcp"
# How long FFMPEG waits on a dead/quiet stream before giving us a failed read.
DEFAULT_RTSP_TIMEOUT_SEC = 15


class RTSPVideoSource(VideoSource):
    """Read frames from an ``rtsp://`` (or ``rtsps://``/``rtmp://``) stream.

    Parameters
    ----------
    url:
        Full stream URL, e.g. ``rtsp://user:pass@10.0.0.5:554/Streaming/...``.
    target_fps, target_long_side:
        Throttle + downscale policy (see :class:`~inference.video.base.VideoSource`).
    reconnect_threshold:
        Number of consecutive failed reads before a reconnect is attempted.
    reconnect_attempts:
        Max reconnect tries before giving up (raises from ``open`` path; for the
        ``read`` path we surface ``CameraState.ERROR`` and keep returning
        ``(False, None)``).
    backoff_base, backoff_max:
        Exponential backoff between reconnect attempts, in seconds. Sleep
        ``min(backoff_max, backoff_base * 2**attempt)``.
    rtsp_transport:
        ``"tcp"`` (default, robust) or ``"udp"``.
    timeout_sec:
        Per-read timeout enforced inside FFMPEG so a hung NVR can't block us.
    """

    def __init__(
        self,
        url: str,
        target_fps: float = DEFAULT_TARGET_FPS,
        target_long_side: int = DEFAULT_LONG_SIDE,
        reconnect_threshold: int = 5,
        reconnect_attempts: int = 5,
        backoff_base: float = 1.0,
        backoff_max: float = 30.0,
        rtsp_transport: str = DEFAULT_RTSP_TRANSPORT,
        timeout_sec: int = DEFAULT_RTSP_TIMEOUT_SEC,
        # After a full reconnect cycle is exhausted, how long to wait before
        # trying a fresh cycle. A CCTV NVR that was down may well come back, so
        # we keep retrying periodically rather than giving up permanently.
        retry_after_exhaustion: float = 60.0,
        camera_id: str | None = None,
        event_bus: EventBus | None = None,
        # Test seam: inject a factory returning a fake cv2.VideoCapture so the
        # reconnect state machine can be unit-tested with no network.
        _capture_factory=None,
    ) -> None:
        super().__init__(target_fps=target_fps, target_long_side=target_long_side)
        self._url = url
        self._camera_id = camera_id or _default_camera_id(url)
        self._event_bus = event_bus
        self._reconnect_threshold = int(reconnect_threshold)
        self._reconnect_attempts = int(reconnect_attempts)
        self._backoff_base = float(backoff_base)
        self._backoff_max = float(backoff_max)
        self._rtsp_transport = rtsp_transport
        self._timeout_sec = int(timeout_sec)
        self._retry_after_exhaustion = float(retry_after_exhaustion)
        self._capture_factory = _capture_factory

        self._cap = None
        self._consecutive_failures = 0
        self._last_reconnect_at = 0.0
        # Allow tests/sleep/monotonic to be overridden; production uses real time.
        self._sleep = time.sleep
        self._monotonic = time.monotonic
        self._camera_offline_fired = False

    @property
    def camera_id(self) -> str:
        return self._camera_id

    def is_live(self) -> bool:
        return True

    # ------------------------------------------------------------------ #
    # Open / reopen
    # ------------------------------------------------------------------ #
    def _build_capture(self):
        """Construct a fresh cv2.VideoCapture bound to this RTSP URL.

        Sets FFMPEG capture options (transport + timeout) via the environment
        variable that OpenCV's FFMPEG backend reads.
        """
        import cv2

        options = (
            f"rtsp_transport;{self._rtsp_transport}"
            f"|stimeout;{self._timeout_sec * 1000}"
        )

        # Tell OpenCV's FFMPEG backend to use these options.
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = options

        if self._capture_factory is not None:
            return self._capture_factory(self._url)

        # Standard Python OpenCV API
        return cv2.VideoCapture(self._url, cv2.CAP_FFMPEG)

    def _open_capture(self) -> None:
        cap = self._build_capture()
        if cap is None or not cap.isOpened():
            raise VideoSourceError(f"Could not open RTSP stream: {self._url}")
        self._cap = cap
        self._populate_props(cap)
        self._consecutive_failures = 0

    def _populate_props(self, cap) -> None:
        """RTSP commonly misreports fps as 0; fall back to 30."""
        import cv2

        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(fps) or fps <= 1.0:
            fps = DEFAULT_SOURCE_FPS_FALLBACK
        self._source_fps = fps
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._source_resolution = (w, h)

    # ------------------------------------------------------------------ #
    # Reconnect state machine
    # ------------------------------------------------------------------ #
    def _reconnect(self) -> bool:
        """Try to reopen the stream with exponential backoff.

        Returns True if a working capture was re-established. Transitions state
        ERROR -> PROCESSING -> ONLINE (via next successful read) on success, or
        leaves it in ERROR on exhaustion.
        """
        self._state = CameraState.ERROR
        self._release_capture()

        for attempt in range(self._reconnect_attempts):
            self._state = CameraState.PROCESSING
            sleep_for = min(
                self._backoff_max, self._backoff_base * (2 ** attempt)
            )
            self._sleep(sleep_for)
            try:
                self._open_capture()
            except VideoSourceError:
                self._state = CameraState.ERROR
                continue
            # Reopened successfully; first read will flip us to ONLINE.
            self._consecutive_failures = 0
            self._state = CameraState.PROCESSING
            self._camera_offline_fired = False
            return True

        # All attempts failed. Record when this happened so the read loop can
        # kick off another cycle after ``retry_after_exhaustion`` seconds.
        self._last_reconnect_at = self._monotonic()
        self._state = CameraState.ERROR
        self._emit_camera_offline()
        return False

    def _emit_camera_offline(self) -> None:
        if self._event_bus is None or self._camera_offline_fired:
            return
        from analytics.events.adapters import camera_offline_to_analytics

        self._event_bus.publish(
            camera_offline_to_analytics(
                self._camera_id,
                timestamp=time.time(),
                reason="reconnect_exhausted",
                url=self._url,
            )
        )
        self._camera_offline_fired = True

    # ------------------------------------------------------------------ #
    # Read path
    # ------------------------------------------------------------------ #
    def _raw_read(self) -> tuple[bool, "np.ndarray | None"]:
        cap = self._cap
        if cap is None:
            # Capture was released (e.g. after a reconnect cycle was exhausted).
            # Periodically retry a fresh connect so a recovering NVR is picked
            # up rather than leaving the source stuck in ERROR forever.
            elapsed = self._monotonic() - self._last_reconnect_at
            if elapsed >= self._retry_after_exhaustion:
                self._reconnect()
            return False, None

        ok, frame = cap.read()
        if ok:
            self._consecutive_failures = 0
            return True, frame

        # Failed read. Tally and reconnect once we cross the threshold.
        self._consecutive_failures += 1
        if self._consecutive_failures < self._reconnect_threshold:
            return False, None

        # Crossed threshold — attempt recovery. If it fails, we stay in ERROR
        # and keep returning (False, None); the caller just keeps polling.
        self._reconnect()
        return False, None

    def _release_capture(self) -> None:
        cap = self._cap
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass
            self._cap = None

    def release(self) -> None:
        self._release_capture()
        super().release()

    @property
    def url(self) -> str:
        return self._url

    @property
    def consecutive_failures(self) -> int:
        """Diagnostic: how many reads failed in a row before a reconnect."""
        return self._consecutive_failures


def _default_camera_id(url: str) -> str:
    host = urlparse(url).hostname or "rtsp"
    return host.replace(".", "-")
