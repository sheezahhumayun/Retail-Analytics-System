"""Webcam video source — local development / demo source (PRD §9).

This is intentionally a thin source: a webcam is the simplest way to exercise
the whole pipeline against live, real-time frames without standing up an NVR.
It shares the exact same interface as the file and RTSP sources, so code
written against it transfers directly to production CCTV.
"""

from __future__ import annotations

import math
import sys
from typing import TYPE_CHECKING

from .base import (
    DEFAULT_LONG_SIDE,
    DEFAULT_SOURCE_FPS_FALLBACK,
    DEFAULT_TARGET_FPS,
    VideoSource,
    VideoSourceError,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    import numpy as np


class WebcamVideoSource(VideoSource):
    """Read frames from a local webcam by device index (0 = default camera).

    Parameters
    ----------
    device_index:
        OS webcam index. ``0`` is the default camera; ``1``, ``2``... for extra
        USB/IP cameras as the OS exposes them.
    target_fps, target_long_side:
        Throttle + downscale policy (see :class:`~inference.video.base.VideoSource`).
    backend:
        Optional explicit OpenCV backend (e.g. ``cv2.CAP_DSHOW`` on Windows for
        faster opens). If ``None``, the platform default is used.
    """

    def __init__(
        self,
        device_index: int = 0,
        target_fps: float = DEFAULT_TARGET_FPS,
        target_long_side: int = DEFAULT_LONG_SIDE,
        backend: int | None = None,
    ) -> None:
        super().__init__(target_fps=target_fps, target_long_side=target_long_side)
        self._device_index = int(device_index)
        # On Windows default to DirectShow — noticeably faster open than the
        # MSMF default, with identical frame output. Caller can override.
        if backend is None and sys.platform.startswith("win"):
            try:
                import cv2

                backend = cv2.CAP_DSHOW
            except Exception:
                backend = None
        self._backend = backend
        self._cap = None

    def is_live(self) -> bool:
        return True

    def _open_capture(self) -> None:
        import cv2

        if self._backend is not None:
            cap = cv2.VideoCapture(self._device_index, self._backend)
        else:
            cap = cv2.VideoCapture(self._device_index)

        if not cap.isOpened():
            raise VideoSourceError(
                f"Could not open webcam device index {self._device_index}"
            )

        self._cap = cap
        self._populate_props(cap)

    def _populate_props(self, cap) -> None:
        """Webcams frequently report 0 fps until the first frame; fall back."""
        import cv2

        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(fps) or fps <= 1.0:
            fps = DEFAULT_SOURCE_FPS_FALLBACK
        self._source_fps = fps
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._source_resolution = (w, h)

    def _raw_read(self) -> tuple[bool, "np.ndarray | None"]:
        cap = self._cap
        if cap is None:
            return False, None
        return cap.read()

    def release(self) -> None:
        cap = self._cap
        if cap is not None:
            cap.release()
            self._cap = None
        super().release()

    @property
    def device_index(self) -> int:
        return self._device_index
