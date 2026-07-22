"""File-backed video source (mp4 / avi / mov / anything OpenCV/FFMPEG can read).

This is the workhorse source for development: every other module can be built
and tested entirely against local files in ``sample-data/`` and later swapped
for an RTSP stream with zero code changes (see :mod:`inference.video.rtsp_source`
and :func:`inference.video.factory.create_video_source`).
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import TYPE_CHECKING

from .base import (
    DEFAULT_SOURCE_FPS_FALLBACK,
    DEFAULT_TARGET_FPS,
    DEFAULT_LONG_SIDE,
    VideoSource,
    VideoSourceError,
)

if TYPE_CHECKING:  # pragma: no cover - typing only
    import numpy as np


class FileVideoSource(VideoSource):
    """Read frames from a local video file (mp4/avi/mov).

    Parameters
    ----------
    path:
        Path to the video file.
    target_fps:
        Effective processing rate to hand downstream (PRD §33). Frames between
        kept frames are advanced with ``grab()`` (cheap) instead of decoded.
    target_long_side:
        Downscale cap on the longest side; detection never sees full 1080p/4K.
    loop:
        When True, the file restarts at EOF so dev loops never stop. Default
        False — a real run over a finite file ends cleanly with ``(False, None)``.
    """

    def __init__(
        self,
        path: str | os.PathLike,
        target_fps: float = DEFAULT_TARGET_FPS,
        target_long_side: int = DEFAULT_LONG_SIDE,
        loop: bool = False,
    ) -> None:
        super().__init__(target_fps=target_fps, target_long_side=target_long_side)
        self._path = Path(path)
        self._loop = bool(loop)
        self._cap = None  # cv2.VideoCapture, imported lazily in _open_capture

    def is_live(self) -> bool:
        return False

    def _open_capture(self) -> None:
        import cv2

        if not self._path.exists():
            raise VideoSourceError(f"Video file not found: {self._path}")

        # CAP_FFMPEG gives reliable mp4/avi/mov handling and matches what the
        # RTSP source uses, so behaviour is consistent across source types.
        cap = cv2.VideoCapture(str(self._path), cv2.CAP_FFMPEG)
        if not cap.isOpened():
            raise VideoSourceError(f"Could not open video file: {self._path}")

        self._cap = cap
        self._populate_props(cap)

    def _populate_props(self, cap) -> None:
        """Read fps/resolution from the capture, guarding against bad reports.

        Stock/downloaded footage and some NVR exports report ``CAP_PROP_FPS``
        as 0 or NaN; treat those as "unknown" and fall back to the standard 30.
        """
        import cv2

        fps = float(cap.get(cv2.CAP_PROP_FPS))
        if not math.isfinite(fps) or fps <= 0:
            fps = DEFAULT_SOURCE_FPS_FALLBACK
        self._source_fps = fps

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._source_resolution = (w, h)

    def _raw_read(self) -> tuple[bool, "np.ndarray | None"]:
        import cv2

        cap = self._cap
        if cap is None:
            return False, None

        ok, frame = cap.read()
        if ok:
            return True, frame

        # EOF. Loop if asked to, otherwise signal end-of-stream.
        if self._loop:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ok, frame = cap.read()
            return ok, frame
        return False, None

    def release(self) -> None:
        cap = self._cap
        if cap is not None:
            cap.release()
            self._cap = None
        super().release()

    @property
    def path(self) -> Path:
        return self._path
