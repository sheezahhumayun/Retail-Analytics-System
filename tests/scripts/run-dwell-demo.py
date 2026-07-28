"""Test Checkpoint 7 — zone events + dwell analytics (file / RTSP / webcam).

Usage (PowerShell)::

    python tests/scripts/run-dwell-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json
    python tests/scripts/run-dwell-demo.py rtsp://10.0.0.5/stream --zone-config tests/videos/town_zones.json --camera-id entrance --duration 300
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.scripts.demo_source import (
    add_source_args,
    iter_frames,
    print_processing_stats,
    resolve_camera_id,
    resolve_duration,
    warmup_source,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Dwell-time analytics demo")
    add_source_args(parser)
    parser.add_argument("--zone-config", required=True, help="ZoneConfig JSON")
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    parser.add_argument(
        "--dwell-threshold",
        type=float,
        help="Apply same dwell_threshold_seconds to every zone (for manual alert test)",
    )
    parser.add_argument(
        "--lost-track-timeout",
        type=float,
        default=5.0,
        help="Seconds without zone events before TRACK_LOST close (default: 5)",
    )
    args = parser.parse_args()

    from analytics.dwell import DwellTracker
    from analytics.zones import ZoneConfig, ZoneDetector
    from inference.detection import create_detector
    from inference.tracking import Tracker

    config = ZoneConfig.load_json(Path(args.zone_config))
    camera_id = resolve_camera_id(args.source, args.camera_id or config.camera_id)
    zones = list(config.enabled_zones)

    thresholds: dict[str, float | None] | None = None
    if args.dwell_threshold is not None:
        thresholds = {z.zone_id: args.dwell_threshold for z in zones}

    duration = resolve_duration(args.source, args.duration)
    detector = ZoneDetector(zones, hysteresis_frames=2)
    dwell = DwellTracker(
        zones,
        dwell_thresholds=thresholds,
        lost_track_timeout_seconds=args.lost_track_timeout,
    )
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

    dwell_events = []
    threshold_events = []
    last_ts = 0.0

    with create_detector(backend=args.backend) as det:
        src = warmup_source(
            args.source,
            target_fps=args.target_fps,
            detector=det,
            camera_id=camera_id,
        )

        for frame, ts in iter_frames(
            src,
            duration=duration,
            preview=args.preview,
            preview_window="dwell",
        ):
            last_ts = ts
            dets = det.detect(frame, camera_id=camera_id, timestamp=ts)
            for ev in detector.update(tracker.update(dets)):
                result = dwell.process(ev)
                if result.dwell_event:
                    dwell_events.append(result.dwell_event)
                if result.threshold_event:
                    threshold_events.append(result.threshold_event)
            dwell.close_stale_sessions(ts)

        print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)
        src.release()

    dwell.close_stale_sessions(last_ts + args.lost_track_timeout + 1.0)

    print(f"\n{camera_id}: {len(dwell_events)} dwell event(s), "
          f"{len(threshold_events)} threshold alert(s)")
    if thresholds:
        print(f"  dwell_threshold_seconds={args.dwell_threshold} (all zones)")
    print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)

    print("\nSample dwell events (up to 10):")
    for ev in dwell_events[:10]:
        print(ev.to_dict())
    if len(dwell_events) > 10:
        print(f"  ... and {len(dwell_events) - 10} more")

    if threshold_events:
        print("\nDwell threshold alerts:")
        for ev in threshold_events:
            print(ev.to_dict())

    print("\nDwell aggregates:")
    for zone_id, snap in dwell.all_snapshots().items():
        print(f"  {zone_id}: {json.dumps(snap.to_dict(), indent=2)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
