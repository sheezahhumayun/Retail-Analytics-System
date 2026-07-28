"""Test Checkpoint 8 — detect + track + heatmap overlay (file / RTSP / webcam).

Usage (PowerShell)::

    python tests/scripts/run-heatmap-demo.py sample-data/store-floor.mp4
    python tests/scripts/run-heatmap-demo.py sample-data/town.mp4 --camera-id town -o tests/videos/town_heatmap.png
    python tests/scripts/run-heatmap-demo.py rtsp://user:pass@10.0.0.5/stream --camera-id entrance --duration 120 --preview-every 30
    python tests/scripts/run-heatmap-demo.py 0 --camera-id desk-cam --duration 60 --preview
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.scripts.demo_source import (
    add_source_args,
    analytics_timestamp,
    current_hour_window,
    is_live_source_spec,
    iter_frames,
    open_source,
    print_processing_stats,
    resolve_camera_id,
    resolve_duration,
    warmup_source,
)


def _render_overlay(
    engine,
    *,
    is_live: bool,
    recording_start: datetime,
    last_media_ts: float,
):
    if is_live:
        hour_start, hour_end = current_hour_window(timezone.utc)
        return engine.render(hour_start, hour_end, include_live=True)
    end_dt = recording_start + timedelta(seconds=max(last_media_ts, 0.0) + 1.0)
    return engine.render(recording_start, end_dt, include_live=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Heatmap generation demo")
    add_source_args(parser)
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    parser.add_argument(
        "--recording-start",
        default="2026-07-28T12:00:00+00:00",
        help="ISO datetime for media t=0 hour buckets (file replays only)",
    )
    parser.add_argument(
        "--store-dir",
        default=str(REPO_ROOT / "data" / "heatmaps"),
        help="Hour-bucket persistence directory",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=str(REPO_ROOT / "tests" / "videos" / "heatmap_overlay.png"),
        help="Save rendered overlay PNG",
    )
    parser.add_argument(
        "--reference-output",
        help="Optional path to save the reference frame used for overlay",
    )
    parser.add_argument(
        "--preview-every",
        type=float,
        default=0.0,
        help="Refresh heatmap preview window every N seconds (0 = off)",
    )
    args = parser.parse_args()

    import cv2

    from analytics.heatmaps import HeatmapEngine, HeatmapStore
    from inference.detection import create_detector
    from inference.tracking import Tracker

    camera_id = resolve_camera_id(args.source, args.camera_id)
    duration = resolve_duration(args.source, args.duration)
    recording_start = (
        None if is_live_source_spec(args.source) else datetime.fromisoformat(args.recording_start)
    )
    store = HeatmapStore(args.store_dir, timezone="UTC")

    probe = open_source(args.source, target_fps=args.target_fps)
    ok, first_frame = probe.read()
    if not ok:
        print(f"Could not read a frame from {args.source!r}", file=sys.stderr)
        return 1
    h, w = first_frame.shape[:2]
    probe.release()

    engine = HeatmapEngine(camera_id, w, h, grid_scale=4, store=store, timezone="UTC")
    engine.set_reference_frame(first_frame)
    if args.reference_output:
        cv2.imwrite(args.reference_output, first_frame)

    preview_window = "heatmap"
    last_preview = 0.0
    last_media_ts = 0.0

    with create_detector(backend=args.backend) as det:
        src = warmup_source(
            args.source,
            target_fps=args.target_fps,
            detector=det,
            camera_id=camera_id,
        )
        tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

        for frame, media_ts in iter_frames(src, duration=duration):
            last_media_ts = media_ts
            bucket_ts = analytics_timestamp(media_ts, src, recording_start)
            dets = det.detect(frame, camera_id=camera_id, timestamp=bucket_ts)
            engine.update(tracker.update(dets), bucket_ts)

            if args.preview_every > 0:
                now = time.time()
                if now - last_preview >= args.preview_every:
                    overlay = _render_overlay(
                        engine,
                        is_live=src.is_live(),
                        recording_start=recording_start or datetime.now(timezone.utc),
                        last_media_ts=last_media_ts,
                    )
                    cv2.imshow(preview_window, overlay)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
                    last_preview = now

        if args.preview or args.preview_every > 0:
            cv2.destroyWindow(preview_window)

        effective_fps = src.get_effective_fps()
        kept = src.get_kept_frame_count()
        is_live = src.is_live()
        media_dur = src.get_media_duration()
        src.release()

    rec_start = recording_start or datetime.now(timezone.utc)
    overlay = _render_overlay(
        engine,
        is_live=is_live,
        recording_start=rec_start,
        last_media_ts=last_media_ts,
    )
    engine.flush()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), overlay)

    print(f"{camera_id}: {kept} kept frames")
    print(
        f"  processing: target {args.target_fps} fps, effective {effective_fps:.2f} fps"
    )
    if is_live:
        print(f"  wall time covered: {last_media_ts:.1f}s")
        print("  timestamps: wall clock (live source)")
    else:
        print(f"  media time covered: {last_media_ts:.1f}s", end="")
        if media_dur is not None:
            print(f" / {media_dur:.1f}s file duration")
        else:
            print()
    print(f"  reference: {w}x{h}  grid: {w // 4}x{h // 4}")
    print(f"  hour buckets → {args.store_dir}/{camera_id}/")
    print(f"  overlay saved → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
