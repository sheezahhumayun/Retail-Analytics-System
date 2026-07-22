#!/usr/bin/env python
"""Module 1 smoke test — exercise a VideoSource end to end and print metrics.

Use this to sanity-check that frames actually flow before wiring Module 2
(detection) on top. Runs against any source the factory understands:

    python tests/scripts/smoke_video_source.py sample-data/entrance.mp4
    python tests/scripts/smoke_video_source.py sample-data/checkout.mp4 --fps 15
    python tests/scripts/smoke_video_source.py 0                    # webcam
    python tests/scripts/smoke_video_source.py rtsp://...           # live RTSP
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Allow running from a checkout without installing the package.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from inference.video import (  # noqa: E402
    CameraState,
    VideoSourceError,
    create_video_source,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="VideoSource smoke test")
    p.add_argument(
        "source",
        help="mp4/avi/mov path, device index (e.g. 0), or rtsp:// URL",
    )
    p.add_argument("--fps", type=float, default=10.0, help="target processing fps")
    p.add_argument(
        "--long-side",
        type=int,
        default=640,
        help="downscale cap on the longest side (px)",
    )
    p.add_argument(
        "--frames", type=int, default=30, help="kept frames to read before reporting"
    )
    p.add_argument(
        "--loop", action="store_true", help="loop file sources (dev convenience)"
    )
    return p.parse_args()


def _coerce_source(spec: str):
    if spec.lstrip("-").isdigit():
        return int(spec)
    return spec


def main() -> int:
    args = parse_args()
    spec = _coerce_source(args.source)

    kwargs = dict(target_fps=args.fps, target_long_side=args.long_side)
    # File-only kwarg; factory passes **kwargs through, so only include when valid.
    if isinstance(spec, str) and not spec.lower().startswith(
        ("rtsp://", "rtsps://", "rtmp://")
    ):
        kwargs["loop"] = args.loop

    src = create_video_source(spec, **kwargs)
    print(f"source type      : {type(src).__name__}")
    print(f"is_live          : {src.is_live()}")

    try:
        src.open()
    except VideoSourceError as exc:
        print(f"OPEN FAILED ({src.get_state().value}): {exc}", file=sys.stderr)
        return 2

    print(f"source fps       : {src.get_fps():.3f}")
    sw, sh = src.get_source_resolution()
    print(f"source resolution: {sw}x{sh}")
    rw, rh = src.get_resolution()
    print(f"output resolution: {rw}x{rh}  (after downscale)")
    print(f"state after open : {src.get_state().value}")

    decode_times: list[float] = []
    kept = 0
    t0 = time.perf_counter()
    try:
        while kept < args.frames:
            tok = time.perf_counter()
            ok, frame = src.read()
            decode_times.append(time.perf_counter() - tok)
            if not ok:
                # For files this is EOF; for RTSP it may be a transient drop.
                kind = "EOF" if not src.is_live() else "transient drop / reconnect"
                print(f"read() returned False after {kept} frames ({kind})")
                if not src.is_live():
                    break
                continue
            kept += 1
    finally:
        elapsed = time.perf_counter() - t0
        final_state = src.get_state()
        src.release()

    if decode_times:
        decode_times.sort()
        mean_ms = (sum(decode_times) / len(decode_times)) * 1000.0
        p95_ms = decode_times[int(len(decode_times) * 0.95)] * 1000.0
    else:
        mean_ms = p95_ms = 0.0

    print("-" * 40)
    print(f"kept frames      : {kept}")
    print(f"wall time        : {elapsed:.3f}s")
    if kept:
        print(f"effective fps    : {kept / elapsed:.2f}")
    print(f"read() mean      : {mean_ms:.2f} ms")
    print(f"read() p95       : {p95_ms:.2f} ms")
    print(f"final state      : {final_state.value}")
    return 0 if kept > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
