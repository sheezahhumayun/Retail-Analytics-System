"""Video ingestion layer — common interface for all frame sources.

PRD §9 requires "a common interface so analytics modules do not depend directly
on the input source." This module defines that interface (the :class:`VideoSource`
ABC) plus the camera-state model (PRD §8) and two cross-cutting concerns that
the task description explicitly demands live *here*, not downstream:

* **Target-FPS throttling** — a 30fps source feeding a 10fps pipeline means
  "process every 3rd frame". This layer decides which frames to hand off so
  detection/tracking/analytics never re-implement that logic.
* **Downscale to a long-side cap** — decoding + resizing dominate CPU cost before
  detection even runs. We hand detection frames at ~640px on the long side rather
  than full 1080p/4K CCTV resolution.
"""

from __future__ import annotations

import abc
import math
import time
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    import numpy as np


class CameraState(str, Enum):
    """Lifecycle state of a camera/source, mirroring PRD §8.

    The ingestion layer is the only component that can observe the *true* state
    of a stream (it's the thing doing the reads). The DB/UI side of camera
    management arrives in Module 16; for now this enum is how this layer reports
    health so later modules can key off it (e.g. ``CAMERA_OFFLINE`` events,
    PRD §27).
    """

    DISABLED = "Disabled"      # Administratively turned off (not attempting I/O)
    OFFLINE = "Offline"        # Not opened / released / never connected
    ERROR = "Error"            # Opened but currently failing (e.g. RTSP dropped)
    PROCESSING = "Processing"  # Connected, ramping up / reconnecting / warming
    ONLINE = "Online"          # Actively producing frames


class VideoSourceError(RuntimeError):
    """Raised on failures a caller can react to (open failed, disabled, ...).

    Transient read failures (e.g. an RTSP frame drop) are *not* raised — see
    :meth:`VideoSource.read`.
    """


# Default policy values. Centralised so every implementation behaves the same
# and downstream modules can rely on consistent defaults.
DEFAULT_TARGET_FPS = 10.0          # PRD §33 target rate: 10–15 fps
DEFAULT_LONG_SIDE = 640            # CPU reality check: don't detect on 1080p/4K
DEFAULT_SOURCE_FPS_FALLBACK = 30.0 # Many stock clips / NVRs report 0; assume 30


def resize_long_side(frame: "np.ndarray", target_long_side: int) -> "np.ndarray":
    """Downscale ``frame`` so its longest side is <= ``target_long_side``.

    Uses ``cv2.INTER_AREA`` (OpenCV's recommended filter for downscaling — it
    anti-aliases instead of aliasing). Aspect ratio is preserved. If the frame
    is already at or below the cap, it is returned unchanged (no copy).
    """
    import cv2

    h, w = frame.shape[:2]
    longest = max(w, h)
    if longest <= target_long_side:
        return frame

    scale = target_long_side / longest
    new_w = max(1, int(round(w * scale)))
    new_h = max(1, int(round(h * scale)))
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)


def compute_frame_interval(source_fps: float, target_fps: float) -> int:
    """How many source frames make up one "kept" frame.

    e.g. 30fps source / 10fps target -> process 1 of every 3 -> interval 3.
    Guarded against bad inputs (<=0 / NaN fps) so a misreporting NVR can't
    crash the throttle loop.
    """
    if not math.isfinite(source_fps) or source_fps <= 0:
        source_fps = DEFAULT_SOURCE_FPS_FALLBACK
    if not math.isfinite(target_fps) or target_fps <= 0:
        return 1
    interval = round(source_fps / target_fps)
    return max(1, interval)


class VideoSource(abc.ABC):
    """Abstraction over a frame source: file, RTSP stream, or webcam.

    Every downstream module (detect(frame), track(detections), ...) consumes a
    :class:`VideoSource` and is agnostic to the concrete source. See
    :mod:`inference.video.factory` for construction.

    Contract notes
    --------------
    * ``open()`` must be called before ``read()``. It raises
      :class:`VideoSourceError` on hard failure (file missing, disabled).
    * ``read()`` returns ``(ok, frame)``. ``ok`` is False on end-of-file (files)
      or a transient drop that this layer will recover from (RTSP). It does
      *not* raise on transient drops — real CCTV/NVR streams drop intermittently
      and that is normal operation, not an exceptional condition (PRD §8 "Error"
      state is surfaced via :meth:`get_state`, not exceptions).
    * Each successful kept frame updates :meth:`get_last_timestamp` — **media
      time** (seconds from file start) for recordings, **wall-clock** for live
      sources. Downstream analytics must use this instead of assuming
      ``frame_index / target_fps``.
    """

    def __init__(
        self,
        target_fps: float = DEFAULT_TARGET_FPS,
        target_long_side: int = DEFAULT_LONG_SIDE,
    ) -> None:
        self._target_fps = float(target_fps)
        self._target_long_side = int(target_long_side)
        self._state: CameraState = CameraState.OFFLINE
        # Counts *every* underlying frame grab, kept or skipped. Used by the
        # throttle loop and exposed for diagnostics/tests.
        self._frame_index: int = 0
        self._kept_frame_count: int = 0
        self._last_timestamp: float = 0.0
        self._wall_start: float | None = None
        self._source_fps: float = DEFAULT_SOURCE_FPS_FALLBACK
        self._source_resolution: tuple[int, int] = (0, 0)  # native (w, h)
        self._opened: bool = False

    # ------------------------------------------------------------------ #
    # Abstract API — each implementation fills these in.
    # ------------------------------------------------------------------ #
    @abc.abstractmethod
    def _open_capture(self) -> None:
        """Open the underlying cv2 capture and populate source fps/resolution.

        Implementations set ``self._source_fps`` and ``self._source_resolution``
        from the opened capture. Raise :class:`VideoSourceError` on hard
        failure.
        """

    @abc.abstractmethod
    def _raw_read(self) -> tuple[bool, "np.ndarray | None"]:
        """One underlying capture read — no throttle/resize applied.

        Implementations must NOT raise on transient failures; return
        ``(False, None)`` instead so the common :meth:`read` can decide policy
        (reconnect, state transitions, etc.).
        """

    @abc.abstractmethod
    def is_live(self) -> bool:
        """True for RTSP/webcam (no EOF, real-time), False for files."""

    # ------------------------------------------------------------------ #
    # Concrete API.
    # ------------------------------------------------------------------ #
    def open(self) -> None:
        if self._state is CameraState.DISABLED:
            raise VideoSourceError("Cannot open a disabled video source")
        self._state = CameraState.PROCESSING
        self._frame_index = 0
        self._kept_frame_count = 0
        self._last_timestamp = 0.0
        self._wall_start = None
        try:
            self._open_capture()
        except VideoSourceError:
            self._state = CameraState.ERROR
            raise
        # Stay PROCESSING until the first successful read proves we get frames.
        self._opened = True

    def read(self) -> tuple[bool, "np.ndarray | None"]:
        """Return the next *kept* frame at the target FPS, downscaled.

        Applies two layers of policy before handing a frame to the caller:

        1. **Throttle**: advances the underlying stream, decoding only on kept
           frames (skipped frames use ``grab()``, which is much cheaper than a
           full ``retrieve()``/decode). See :func:`compute_frame_interval`.
        2. **Downscale**: long side capped at ``target_long_side``.

        Returns ``(False, None)`` on EOF (files) or when no frame is available
        this call (e.g. during an RTSP reconnect attempt). Does not raise for
        transient stream drops.
        """
        if not self._opened:
            raise VideoSourceError("Source is not open; call open() first")
        if self._state is CameraState.DISABLED:
            return False, None

        interval = compute_frame_interval(self._source_fps, self._target_fps)

        while True:
            # Decide whether THIS underlying frame is one we hand off.
            self._frame_index += 1
            keep = (self._frame_index % interval == 0)

            ok, frame = self._raw_read()
            if not ok:
                # End of file, transient drop, or mid-reconnect: nothing to give
                # the caller this round. State may have been bumped to ERROR by
                # the implementation during reconnect handling.
                return False, None

            if keep:
                # Mark ONLINE once we've actually produced a frame.
                self._state = CameraState.ONLINE
                if self._wall_start is None:
                    self._wall_start = time.perf_counter()
                self._kept_frame_count += 1
                self._last_timestamp = self._compute_timestamp()
                if frame is not None and self._target_long_side > 0:
                    frame = resize_long_side(frame, self._target_long_side)
                return True, frame
            # else: this was a skipped frame; loop and grab the next.

    def _compute_timestamp(self) -> float:
        """Seconds for the current kept frame — media time (files) or wall clock (live)."""
        if self.is_live():
            return time.time()
        fps = self._source_fps
        if not math.isfinite(fps) or fps <= 0:
            fps = DEFAULT_SOURCE_FPS_FALLBACK
        return self._frame_index / fps

    def get_last_timestamp(self) -> float:
        """Timestamp of the most recent kept frame (see :meth:`_compute_timestamp`)."""
        return self._last_timestamp

    def get_kept_frame_count(self) -> int:
        """Number of frames returned by :meth:`read` since :meth:`open`."""
        return self._kept_frame_count

    def get_source_frame_index(self) -> int:
        """Underlying source frame counter (includes skipped/throttled frames)."""
        return self._frame_index

    def get_target_fps(self) -> float:
        """Configured processing rate cap — not necessarily achieved wall-clock."""
        return self._target_fps

    def get_effective_fps(self) -> float:
        """Measured kept-frame rate since the first kept frame (wall-clock)."""
        if self._wall_start is None or self._kept_frame_count < 1:
            return 0.0
        elapsed = time.perf_counter() - self._wall_start
        if elapsed <= 0:
            return 0.0
        return self._kept_frame_count / elapsed

    def get_media_duration(self) -> float | None:
        """Total media length in seconds (file sources only); ``None`` if unknown."""
        return None

    def get_fps(self) -> float:
        """Native source FPS (post-open). Falls back to 30.0 if unreported."""
        return self._source_fps

    def get_source_resolution(self) -> tuple[int, int]:
        """Native capture resolution as ``(width, height)``."""
        return self._source_resolution

    def get_resolution(self) -> tuple[int, int]:
        """Resolution the caller actually sees — the downscaled dimensions."""
        w, h = self._source_resolution
        if w == 0 or h == 0:
            return (0, 0)
        longest = max(w, h)
        if longest <= self._target_long_side:
            return (w, h)
        scale = self._target_long_side / longest
        return (max(1, int(round(w * scale))), max(1, int(round(h * scale))))

    def get_state(self) -> CameraState:
        return self._state

    def release(self) -> None:
        """Release the underlying capture. Idempotent. State -> OFFLINE."""
        self._opened = False
        if self._state is not CameraState.DISABLED:
            self._state = CameraState.OFFLINE

    # ----- Administrative controls (full camera management is Module 16) --- #
    def disable(self) -> None:
        self._state = CameraState.DISABLED

    def enable(self) -> None:
        if self._state is CameraState.DISABLED:
            self._state = CameraState.OFFLINE

    # ----- Context manager: source is the unit of resource ownership ------- #
    def __enter__(self) -> "VideoSource":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()
