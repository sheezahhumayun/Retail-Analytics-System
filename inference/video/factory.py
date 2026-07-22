"""Factory: pick the right :class:`VideoSource` implementation from a spec.

This is the single entry point downstream code should use so that the choice of
file vs. RTSP vs. webcam never leaks into detection/tracking/analytics modules
(the seam PRD §9 mandates). Swap sources by changing the string passed in — no
code changes anywhere else.
"""

from __future__ import annotations

import os
from pathlib import Path

from .base import VideoSource
from .file_source import FileVideoSource
from .rtsp_source import RTSPVideoSource
from .webcam_source import WebcamVideoSource

# URL schemes that mean "live network stream handled by the RTSP source".
_LIVE_SCHEMES = ("rtsp://", "rtsps://", "rtmp://")

# Extensions we treat as file sources even if the path doesn't exist yet
# (so a clearer "file not found" error comes from FileVideoSource).
_FILE_EXTENSIONS = (".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v", ".flv")


def create_video_source(
    spec: str | int | os.PathLike,
    *,
    target_fps: float | None = None,
    target_long_side: int | None = None,
    **kwargs,
) -> VideoSource:
    """Construct a :class:`VideoSource` from a source spec.

    Routing
    -------
    * ``int``                                     -> :class:`WebcamVideoSource`
    * ``"rtsp://..."`` / ``"rtsps://"`` / ``"rtmp://"`` -> :class:`RTSPVideoSource`
    * ``str`` / ``Path`` (file path or extension) -> :class:`FileVideoSource`

    Pass-through kwargs go to the chosen implementation (e.g. ``loop=True`` for
    files, ``reconnect_threshold=`` for RTSP, ``backend=`` for webcam).

    ``target_fps`` and ``target_long_side`` are accepted positionally-style for
    all sources for symmetry; they default inside each implementation when None.
    """
    common: dict = {}
    if target_fps is not None:
        common["target_fps"] = target_fps
    if target_long_side is not None:
        common["target_long_side"] = target_long_side

    # --- Webcam by device index ------------------------------------------- #
    if isinstance(spec, int) and not isinstance(spec, bool):
        return WebcamVideoSource(device_index=spec, **common, **kwargs)

    # --- Normalize to a string for URL/extension checks ------------------- #
    if isinstance(spec, os.PathLike):
        spec_str = os.fspath(spec)
    else:
        spec_str = str(spec)

    lowered = spec_str.strip().lower()

    # --- Live network stream ---------------------------------------------- #
    if lowered.startswith(_LIVE_SCHEMES):
        return RTSPVideoSource(url=spec_str, **common, **kwargs)

    # --- File (anything else) --------------------------------------------- #
    # We don't hard-require a known extension: if it's not a scheme and not an
    # int, treat it as a file path. FileVideoSource gives a clear error if the
    # path is missing, and OpenCV/FFMPEG handles formats beyond our extension
    # list. We only use the extension to allow callers to pass a not-yet-existing
    # path without it being mistaken for something else.
    return FileVideoSource(path=spec_str, **common, **kwargs)
