"""Test Checkpoint 9 — zone events + queue analytics (file / RTSP / webcam).

Usage (PowerShell)::

    python tests/scripts/run-queues-demo.py sample-data/checkout.mp4 --zone-config tests/videos/checkout_zones.json
    python tests/scripts/run-queues-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --length-threshold 3
    python tests/scripts/run-queues-demo.py rtsp://10.0.0.5/stream --zone-config tests/videos/checkout_zones.json --camera-id checkout --duration 120
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
    parser = argparse.ArgumentParser(description="Queue analytics demo")
    add_source_args(parser)
    parser.add_argument("--zone-config", required=True, help="ZoneConfig JSON with queue zones")
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    parser.add_argument(
        "--length-threshold",
        type=int,
        help="Apply same queue_length_threshold to every queue zone",
    )
    parser.add_argument(
        "--duration-threshold",
        type=float,
        help="Apply same queue_duration_threshold (seconds) to every queue zone",
    )
    args = parser.parse_args()

    from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, AnalyticsEventType, EventBus
    from analytics.queues import is_queue_zone
    from analytics.zones import ZoneConfig, ZoneDetector
    from inference.detection import create_detector
    from inference.tracking import Tracker

    config = ZoneConfig.load_json(Path(args.zone_config))
    camera_id = resolve_camera_id(args.source, args.camera_id or config.camera_id)
    zones = list(config.enabled_zones)
    queue_zones = [z for z in zones if is_queue_zone(z)]
    if not queue_zones:
        print(
            "No queue zones in config — set zone_type to queue, checkout, or waiting.",
            file=sys.stderr,
        )
        return 1

    length_thresholds = None
    duration_thresholds = None
    if args.length_threshold is not None:
        length_thresholds = {z.zone_id: args.length_threshold for z in queue_zones}
    if args.duration_threshold is not None:
        duration_thresholds = {z.zone_id: args.duration_threshold for z in queue_zones}

    duration = resolve_duration(args.source, args.duration)
    bus = EventBus()
    engine = AnalyticsEngine(
        bus,
        AnalyticsEngineConfig(
            camera_ids=[camera_id],
            zones=queue_zones,
            queue_length_thresholds=length_thresholds,
            queue_duration_thresholds=duration_thresholds,
        ),
    )
    detector = ZoneDetector(zones, hysteresis_frames=2)
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

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
            preview_window="queues",
        ):
            last_ts = ts
            dets = det.detect(frame, camera_id=camera_id, timestamp=ts)
            for ev in detector.update(tracker.update(dets)):
                engine.process_zone_event(ev)

        print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)
        src.release()

    threshold_events = [
        e for e in bus.event_log if e.event_type == AnalyticsEventType.QUEUE_THRESHOLD.value
    ]

    print(f"\n{camera_id}: {len(queue_zones)} queue zone(s) tracked")
    if length_thresholds:
        print(f"  length_threshold={args.length_threshold} (all queue zones)")
    if duration_thresholds:
        print(f"  duration_threshold={args.duration_threshold}s (all queue zones)")
    print(
        "  estimated_wait = avg historical dwell in zone (MVP approximation; "
        "Phase 2 adds position-in-queue)"
    )
    print(
        "  camera note: queue must be fully visible in frame — people outside "
        "the polygon are not counted (PRD §34)"
    )

    print("\nQueue metrics (via event bus):")
    for zone_id, snap in engine.queue_snapshots().items():
        print(f"  {zone_id}: {json.dumps(snap.to_dict(), indent=2)}")

    if threshold_events:
        print(f"\nQUEUE_THRESHOLD alerts ({len(threshold_events)}):")
        for ev in threshold_events[:20]:
            print(ev.to_log_dict())
        if len(threshold_events) > 20:
            print(f"  ... and {len(threshold_events) - 20} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
