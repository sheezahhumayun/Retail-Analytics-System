"""Test Checkpoint 6 — detect + track + zone analytics (file / RTSP / webcam).

Usage (PowerShell)::

    python tests/scripts/run-zones-demo.py sample-data/store-floor.mp4
    python tests/scripts/run-zones-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --transitions-only
    python tests/scripts/run-zones-demo.py rtsp://10.0.0.5/stream --camera-id entrance --zone-config tests/videos/entrance_zones.json --duration 120
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

DEFAULT_ZONE_CONFIG = REPO_ROOT / "tests" / "videos" / "store_floor_zones.json"

DEFAULT_ZONE = {
    "zone_id": "floor_center",
    "zone_name": "Floor Center",
    "camera_id": "store-floor",
    "polygon_coordinates": [[100, 100], [540, 100], [540, 300], [100, 300]],
    "zone_type": "general",
    "analytics_enabled": True,
}


def _load_zone_config(path: Path):
    from analytics.zones import ZoneConfig

    if not path.is_file():
        print(
            f"Zone config not found: {path}\n"
            "Either omit --zone-config to use the built-in default, or create one:\n"
            "  python -m analytics.zones.polygon_editor sample-data/store-floor.mp4 "
            f"--camera-id store-floor --zone-id electronics --zone-name Electronics "
            f"--output {path}",
            file=sys.stderr,
        )
        raise SystemExit(1)
    return ZoneConfig.load_json(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Zone detection + analytics demo")
    add_source_args(parser)
    parser.add_argument(
        "--zone-config",
        help="ZoneConfig JSON (from polygon_editor); uses default if omitted",
    )
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    parser.add_argument(
        "--hysteresis-frames",
        type=int,
        default=2,
        help="Inside/outside frames required before ENTER/EXIT (default: 2)",
    )
    parser.add_argument(
        "--transitions-only",
        action="store_true",
        help="Print only ZONE_ENTER / ZONE_EXIT (skip PRESENCE flood)",
    )
    parser.add_argument(
        "--flap-window",
        type=float,
        default=3.0,
        help="Flag ENTER↔EXIT within this many seconds as flapping (default: 3)",
    )
    args = parser.parse_args()

    from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, EventBus
    from analytics.zones import (
        Zone,
        ZoneDetector,
        ZoneEventType,
        detect_flapping,
        event_counts,
        extract_transitions,
        format_transition_timeline,
    )
    from inference.detection import create_detector
    from inference.tracking import Tracker

    if args.zone_config:
        config = _load_zone_config(Path(args.zone_config))
        camera_id = resolve_camera_id(args.source, args.camera_id or config.camera_id)
        zones = list(config.enabled_zones)
    elif DEFAULT_ZONE_CONFIG.is_file():
        config = ZoneConfig.load_json(DEFAULT_ZONE_CONFIG)
        camera_id = resolve_camera_id(args.source, args.camera_id)
        zones = [
            Zone.from_dict({**z.to_dict(), "camera_id": camera_id})
            for z in config.enabled_zones
        ]
        print(f"Using bundled zone config: {DEFAULT_ZONE_CONFIG}")
    else:
        camera_id = resolve_camera_id(args.source, args.camera_id)
        cfg = {**DEFAULT_ZONE, "camera_id": camera_id}
        zones = [Zone.from_dict(cfg)]
        print("Using default zone config (draw your own with polygon_editor):")
        print(json.dumps({"camera_id": camera_id, "zones": [cfg]}, indent=2))

    duration = resolve_duration(args.source, args.duration)
    bus = EventBus()
    engine = AnalyticsEngine(
        bus,
        AnalyticsEngineConfig(camera_ids=[camera_id], zones=zones),
    )
    detector = ZoneDetector(zones, hysteresis_frames=args.hysteresis_frames)
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

    events = []
    last_ts = 0.0

    with create_detector(backend=args.backend) as detector_model:
        src = warmup_source(
            args.source,
            target_fps=args.target_fps,
            detector=detector_model,
            camera_id=camera_id,
        )

        for frame, ts in iter_frames(
            src,
            duration=duration,
            preview=args.preview,
            preview_window="zones",
        ):
            last_ts = ts
            dets = detector_model.detect(
                frame, camera_id=camera_id, timestamp=ts
            )
            for ev in detector.update(tracker.update(dets)):
                events.append(ev)
                engine.process_zone_event(ev)

        print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)
        src.release()

    counts = event_counts(events)
    transitions = extract_transitions(events)

    print(f"\n{camera_id}: {len(events)} zone event(s)")
    print(
        f"  by type: ENTER={counts.get('ZONE_ENTER', 0)}  "
        f"EXIT={counts.get('ZONE_EXIT', 0)}  "
        f"PRESENCE={counts.get('ZONE_PRESENCE', 0)}"
    )
    print(f"  hysteresis_frames={args.hysteresis_frames}")
    print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)

    to_print = (
        [ev for ev in events if ev.event_type != ZoneEventType.ZONE_PRESENCE]
        if args.transitions_only
        else events
    )
    for ev in to_print[:30]:
        d = ev.to_dict()
        d["t_seconds"] = round(ev.timestamp, 2)
        print(d)
    if len(to_print) > 30:
        print(f"... and {len(to_print) - 30} more")

    print("\n--- Transition timeline (ENTER/EXIT) ---")
    print(format_transition_timeline(transitions) or "(none)")

    flaps = detect_flapping(transitions, max_gap_seconds=args.flap_window)
    if flaps:
        print(f"\n⚠ Possible boundary flapping ({len(flaps)} pair(s) within "
              f"{args.flap_window}s):")
        for w in flaps[:10]:
            print(
                f"  track {w.track_id} @ {w.zone_id}: "
                f"{w.first.event_type.value} t={w.first.time_seconds:.1f}s → "
                f"{w.second.event_type.value} t={w.second.time_seconds:.1f}s "
                f"(gap={w.gap_seconds:.1f}s)"
            )
        if len(flaps) > 10:
            print(f"  ... and {len(flaps) - 10} more")
        print("  Try raising --hysteresis-frames (e.g. 3–4) if these look like jitter.")
    else:
        print("\nNo rapid ENTER↔EXIT flapping detected.")

    print("\nZone analytics (via event bus):")
    for zone_id, snap in engine.zone_snapshots().items():
        print(f"  {zone_id}: {snap.to_dict()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
