"""Test Checkpoint 10 — full pipeline event bus + Analytics Engine demo.

Usage (PowerShell)::

    python tests/scripts/run-events-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json
    python tests/scripts/run-events-demo.py sample-data/entrance.mp4 --line-config tests/videos/entrance_line.json
    python tests/scripts/run-events-demo.py rtsp://10.0.0.5/stream --camera-id entrance --zone-config tests/videos/town_zones.json --duration 60
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.scripts.demo_source import (
    add_source_args,
    is_live_source_spec,
    iter_frames,
    print_processing_stats,
    resolve_camera_id,
    resolve_duration,
    warmup_source,
)

DEFAULT_LINE_PATH = REPO_ROOT / "tests" / "videos" / "entrance_line.json"
DEFAULT_ZONE_CONFIG = REPO_ROOT / "tests" / "videos" / "town_zones.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="End-to-end event bus demo (Module 10 checkpoint)",
    )
    add_source_args(parser)
    parser.add_argument("--line-config", help="CountingLine JSON (optional)")
    parser.add_argument("--zone-config", help="ZoneConfig JSON (optional)")
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    parser.add_argument(
        "--dwell-threshold",
        type=float,
        help="Apply dwell_threshold_seconds to every zone",
    )
    parser.add_argument("--length-threshold", type=int, help="Queue length alert threshold")
    parser.add_argument("--duration-threshold", type=float, help="Queue duration alert (seconds)")
    parser.add_argument(
        "--detection-sample-seconds",
        type=float,
        default=1.0,
        help="PERSON_DETECTED sample interval (default: 1.0)",
    )
    parser.add_argument(
        "--log-events",
        action="store_true",
        help="Print every bus event (verbose)",
    )
    args = parser.parse_args()

    from analytics.counting import CountingLine, LineCounter
    from analytics.events import (
        AnalyticsEngine,
        AnalyticsEngineConfig,
        EventBus,
        PersonDetectionSampler,
    )
    from analytics.zones import Zone, ZoneConfig, ZoneDetector
    from inference.detection import create_detector
    from inference.tracking import Tracker
    from inference.video import RTSPVideoSource, create_video_source

    camera_id = resolve_camera_id(args.source, args.camera_id)
    duration = resolve_duration(args.source, args.duration)

    zones: list[Zone] = []
    if args.zone_config:
        config = ZoneConfig.load_json(Path(args.zone_config))
        zones = list(config.enabled_zones)
    elif DEFAULT_ZONE_CONFIG.is_file():
        config = ZoneConfig.load_json(DEFAULT_ZONE_CONFIG)
        zones = [
            Zone.from_dict({**z.to_dict(), "camera_id": camera_id})
            for z in config.enabled_zones
        ]
        print(f"Using bundled zone config: {DEFAULT_ZONE_CONFIG}")

    dwell_thresholds = None
    if args.dwell_threshold is not None and zones:
        dwell_thresholds = {z.zone_id: args.dwell_threshold for z in zones}

    queue_length_thresholds = None
    queue_duration_thresholds = None
    if zones:
        if args.length_threshold is not None:
            from analytics.queues import is_queue_zone

            queue_length_thresholds = {
                z.zone_id: args.length_threshold for z in zones if is_queue_zone(z)
            }
        if args.duration_threshold is not None:
            from analytics.queues import is_queue_zone

            queue_duration_thresholds = {
                z.zone_id: args.duration_threshold for z in zones if is_queue_zone(z)
            }

    bus = EventBus()
    engine = AnalyticsEngine(
        bus,
        AnalyticsEngineConfig(
            camera_ids=[camera_id],
            zones=zones,
            dwell_thresholds=dwell_thresholds,
            queue_length_thresholds=queue_length_thresholds,
            queue_duration_thresholds=queue_duration_thresholds,
        ),
    )

    counter = None
    if args.line_config or DEFAULT_LINE_PATH.is_file():
        line_path = Path(args.line_config) if args.line_config else DEFAULT_LINE_PATH
        line = CountingLine.load_json(line_path)
        if line.camera_id != camera_id:
            line = CountingLine.from_dict({**line.to_dict(), "camera_id": camera_id})
        counter = LineCounter(line, event_bus=bus)
        print(f"Counting line: {line_path}")

    zone_detector = ZoneDetector(zones) if zones else None
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)
    sampler = PersonDetectionSampler(
        bus,
        camera_id,
        sample_interval_seconds=args.detection_sample_seconds,
    )

    last_ts = 0.0
    with create_detector(backend=args.backend) as detector:
        src_kwargs: dict = {}
        if is_live_source_spec(args.source):
            src_kwargs["event_bus"] = bus
        src = warmup_source(
            args.source,
            target_fps=args.target_fps,
            detector=detector,
            camera_id=camera_id,
            **src_kwargs,
        )

        for frame, ts in iter_frames(
            src,
            duration=duration,
            preview=args.preview,
            preview_window="events",
        ):
            last_ts = ts
            dets = detector.detect(frame, camera_id=camera_id, timestamp=ts)
            sampler.maybe_publish(dets)
            tracks = tracker.update(dets)
            if counter is not None:
                counter.update(tracks)
            if zone_detector is not None:
                for ze in zone_detector.update(tracks):
                    engine.process_zone_event(ze)
            engine.close_stale_dwell_sessions(ts)

        print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)
        src.release()

    counts = Counter(e.event_type for e in bus.event_log)
    print(f"\n{camera_id}: {len(bus.event_log)} bus event(s)")
    for etype, count in sorted(counts.items()):
        print(f"  {etype}: {count}")

    occ = engine.camera_occupancy(camera_id)
    if occ is not None:
        print("\nOccupancy (from bus):", json.dumps(occ.to_dict(), indent=2))

    if zones:
        print("\nZone snapshots:")
        for zid, snap in engine.zone_snapshots().items():
            print(f"  {zid}:", json.dumps(snap.to_dict()))

        print("\nDwell snapshots:")
        for zid, snap in engine.dwell_snapshots().items():
            print(f"  {zid}:", json.dumps(snap.to_dict()))

        print("\nQueue snapshots:")
        for zid, snap in engine.queue_snapshots().items():
            print(f"  {zid}:", json.dumps(snap.to_dict()))

    if args.log_events:
        print("\nEvent log:")
        for ev in bus.event_log:
            print(json.dumps(ev.to_log_dict()))

    if isinstance(src, RTSPVideoSource) and counts.get("CAMERA_OFFLINE"):
        print("\nCAMERA_OFFLINE observed (stream reconnect exhausted).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
