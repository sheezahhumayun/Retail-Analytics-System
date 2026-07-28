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

    from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, EventBus
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
    bus = EventBus()
    engine = AnalyticsEngine(
        bus,
        AnalyticsEngineConfig(
            camera_ids=[camera_id],
            zones=zones,
            dwell_thresholds=thresholds,
            lost_track_timeout_seconds=args.lost_track_timeout,
        ),
    )
    detector = ZoneDetector(zones, hysteresis_frames=2)
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

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
                engine.process_zone_event(ev)
            engine.close_stale_dwell_sessions(ts)

        print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)
        src.release()

    engine.close_stale_dwell_sessions(last_ts + args.lost_track_timeout + 1.0)

    from analytics.events import AnalyticsEventType

    threshold_events = [
        ev.to_log_dict()
        for ev in bus.event_log
        if ev.event_type == AnalyticsEventType.DWELL_THRESHOLD.value
    ]
    total_dwell = sum(
        snap.total_dwell_events for snap in engine.dwell_snapshots().values()
    )

    print(f"\n{camera_id}: {total_dwell} dwell event(s), "
          f"{len(threshold_events)} threshold alert(s)")
    if thresholds:
        print(f"  dwell_threshold_seconds={args.dwell_threshold} (all zones)")
    print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)

    print("\nSample dwell events (up to 10):")
    for zid, snap in engine.dwell_snapshots().items():
        if snap.total_dwell_events:
            print(f"  {zid}: {snap.total_dwell_events} completed session(s)")

    if threshold_events:
        print("\nDwell threshold alerts (from bus):")
        for ev in threshold_events:
            print(ev)

    print("\nDwell aggregates (via event bus):")
    for zone_id, snap in engine.dwell_snapshots().items():
        print(f"  {zone_id}: {json.dumps(snap.to_dict(), indent=2)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
