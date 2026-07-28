"""Shared helpers for pipeline demo scripts (file / RTSP / webcam)."""

from __future__ import annotations

import argparse
import time
from collections.abc import Callable, Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from inference.video import VideoSource, create_video_source

_LIVE_SCHEMES = ("rtsp://", "rtsps://", "rtmp://")


def parse_source_spec(spec: str) -> str | int:
    """Route CLI string to factory spec (``0`` → webcam index)."""
    s = spec.strip()
    if s.isdigit():
        return int(s)
    return s


def is_live_source_spec(spec: str) -> bool:
    parsed = parse_source_spec(spec)
    if isinstance(parsed, int):
        return True
    return parsed.lower().startswith(_LIVE_SCHEMES)


def resolve_camera_id(spec: str, override: str | None = None) -> str:
    if override:
        return override
    parsed = parse_source_spec(spec)
    if isinstance(parsed, int):
        return f"webcam-{parsed}"
    lowered = parsed.lower()
    if lowered.startswith(_LIVE_SCHEMES):
        host = urlparse(parsed).hostname or "rtsp"
        return host.replace(".", "-")
    return Path(parsed).stem or "cam"


def add_source_args(parser: argparse.ArgumentParser) -> None:
    """Register common source / live-processing flags on a demo parser."""
    parser.add_argument(
        "source",
        help="Video file path, rtsp:// URL, or webcam device index (e.g. 0)",
    )
    parser.add_argument(
        "--camera-id",
        help="Camera id for detections/tracks/events (default: derived from source)",
    )
    parser.add_argument(
        "--target-fps",
        type=float,
        default=10.0,
        help="Processing rate cap for VideoSource throttle (default: 10)",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Wall-clock seconds to run (live/webcam default 120; 0 = until Ctrl+C)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show frames in an OpenCV window (press q to stop early)",
    )


def resolve_duration(spec: str, duration: float | None) -> float | None:
    """Return wall-clock cap in seconds, or None for EOF / until Ctrl+C."""
    if duration is not None:
        if duration <= 0:
            return None
        return duration
    if is_live_source_spec(spec):
        print(
            "Live source: no --duration set, defaulting to 120s "
            "(use --duration 0 to run until Ctrl+C)"
        )
        return 120.0
    return None


def open_source(spec: str, *, target_fps: float, **kwargs) -> VideoSource:
    parsed = parse_source_spec(spec)
    src = create_video_source(parsed, target_fps=target_fps, **kwargs)
    src.open()
    return src


def warmup_source(
    spec: str,
    *,
    target_fps: float,
    detector: Any | None = None,
    camera_id: str | None = None,
    **kwargs,
) -> VideoSource:
    """Read one kept frame (optional detect warmup), then reopen for the main loop."""
    open_kwargs = dict(kwargs)
    if is_live_source_spec(spec) and camera_id is not None:
        open_kwargs["camera_id"] = camera_id
    probe = open_source(spec, target_fps=target_fps, **open_kwargs)
    ok, first_frame = probe.read()
    if not ok:
        probe.release()
        raise RuntimeError(f"Could not read a frame from {spec!r}")
    if detector is not None and camera_id is not None:
        detector.detect(first_frame, camera_id=camera_id)
    probe.release()
    return open_source(spec, target_fps=target_fps, **open_kwargs)


def iter_frames(
    src: VideoSource,
    *,
    duration: float | None = None,
    preview: bool = False,
    preview_fn: Callable[[Any], Any] | None = None,
    preview_window: str = "preview",
) -> Iterator[tuple[Any, float]]:
    """Yield ``(frame, get_last_timestamp())`` until EOF, duration, or ``q`` in preview."""
    import cv2

    deadline = time.time() + duration if duration is not None else None

    while True:
        if deadline is not None and time.time() >= deadline:
            break
        ok, frame = src.read()
        if not ok:
            if src.is_live():
                continue
            break
        ts = src.get_last_timestamp()
        yield frame, ts
        if preview:
            shown = preview_fn(frame) if preview_fn else frame
            cv2.imshow(preview_window, shown)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    if preview:
        cv2.destroyWindow(preview_window)


def analytics_timestamp(
    media_or_wall_ts: float,
    src: VideoSource,
    recording_start: datetime | None,
) -> float:
    """File replays: epoch = recording_start + media time. Live: wall clock as-is."""
    if src.is_live() or recording_start is None:
        return media_or_wall_ts
    return recording_start.timestamp() + media_or_wall_ts


def current_hour_window(
    tz: timezone = timezone.utc,
) -> tuple[datetime, datetime]:
    now = datetime.now(tz)
    start = now.replace(minute=0, second=0, microsecond=0)
    return start, start + timedelta(hours=1)


def print_processing_stats(
    src: VideoSource,
    *,
    target_fps: float,
    last_ts: float,
) -> None:
    kept = src.get_kept_frame_count()
    eff = src.get_effective_fps()
    media_dur = src.get_media_duration()
    time_label = "wall time" if src.is_live() else "media covered"
    print(
        f"  processing: target {target_fps} fps, effective {eff:.2f} fps, "
        f"{kept} kept frames, {time_label} {last_ts:.1f}s"
        + (f" / {media_dur:.1f}s file" if media_dur is not None else "")
    )
    if src.is_live():
        print("  timestamps: wall clock (live source)")
    else:
        print(f"  timestamps: source media time ({src.get_fps():.2f} fps)")
