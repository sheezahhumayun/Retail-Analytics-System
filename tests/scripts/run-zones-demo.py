"""Test Checkpoint 6 — detect + track + zone analytics over a sample video.

Loads a zone config JSON (draw polygons with ``polygon_editor`` first) or uses
a built-in default zone for quick smoke runs.

Usage (PowerShell)::

    python tests/scripts/run-zones-demo.py sample-data/store-floor.mp4
    python tests/scripts/run-zones-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json

Verify ENTER/EXIT transitions (not drowned in PRESENCE noise)::

    python tests/scripts/run-zones-demo.py sample-data/town.mp4 --zone-config tests/videos/town_zones.json --transitions-only
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
    parser.add_argument("video", help="Video path")
    parser.add_argument(
        "--zone-config",
        help="ZoneConfig JSON (from polygon_editor); uses default if omitted",
    )
    parser.add_argument(
        "--camera-id",
        help="Camera id stamped on detections/tracks/events (default: from config "
        "or video filename stem)",
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
        type=int,
        default=3,
        help="Flag ENTER↔EXIT within this many frames as flapping (default: 3)",
    )
    args = parser.parse_args()

    from analytics.zones import (
        MultiZoneAnalytics,
        Zone,
        ZoneConfig,
        ZoneDetector,
        ZoneEventType,
        detect_flapping,
        event_counts,
        extract_transitions,
        format_transition_timeline,
    )
    from inference.detection import create_detector
    from inference.tracking import Tracker
    from inference.video import create_video_source

    video_path = Path(args.video)
    stem_camera_id = video_path.stem or "cam"

    if args.zone_config:
        config = _load_zone_config(Path(args.zone_config))
        camera_id = args.camera_id or config.camera_id
        zones = list(config.enabled_zones)
    elif DEFAULT_ZONE_CONFIG.is_file():
        config = ZoneConfig.load_json(DEFAULT_ZONE_CONFIG)
        camera_id = args.camera_id or stem_camera_id
        zones = [
            Zone.from_dict({**z.to_dict(), "camera_id": camera_id})
            for z in config.enabled_zones
        ]
        print(f"Using bundled zone config: {DEFAULT_ZONE_CONFIG}")
    else:
        camera_id = args.camera_id or stem_camera_id
        cfg = {**DEFAULT_ZONE, "camera_id": camera_id}
        zones = [Zone.from_dict(cfg)]
        print("Using default zone config (draw your own with polygon_editor):")
        print(json.dumps({"camera_id": camera_id, "zones": [cfg]}, indent=2))

    detector = ZoneDetector(zones, hysteresis_frames=args.hysteresis_frames)
    analytics = MultiZoneAnalytics(zones)
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

    with create_detector(backend=args.backend) as detector_model:
        src = create_video_source(str(video_path), target_fps=10)
        src.open()

        ok, frame = src.read()
        if ok:
            detector_model.detect(frame, camera_id=camera_id)
            src = create_video_source(str(video_path), target_fps=10)
            src.open()

        events = []
        frame_idx = 0
        while True:
            ok, frame = src.read()
            if not ok:
                break
            dets = detector_model.detect(
                frame, camera_id=camera_id, timestamp=float(frame_idx)
            )
            frame_idx += 1
            for ev in detector.update(tracker.update(dets)):
                events.append(ev)
                analytics.process(ev)

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

    to_print = (
        [ev for ev in events if ev.event_type != ZoneEventType.ZONE_PRESENCE]
        if args.transitions_only
        else events
    )
    for ev in to_print[:30]:
        d = ev.to_dict()
        if "timestamp" in d and d["timestamp"].startswith("1970-"):
            d["frame"] = int(ev.timestamp)
        print(d)
    if len(to_print) > 30:
        print(f"... and {len(to_print) - 30} more")

    print("\n--- Transition timeline (ENTER/EXIT) ---")
    print(format_transition_timeline(transitions) or "(none)")

    flaps = detect_flapping(transitions, max_gap_frames=args.flap_window)
    if flaps:
        print(f"\n⚠ Possible boundary flapping ({len(flaps)} pair(s) within "
              f"{args.flap_window} frames):")
        for w in flaps[:10]:
            print(
                f"  track {w.track_id} @ {w.zone_id}: "
                f"{w.first.event_type.value} frame {w.first.frame} → "
                f"{w.second.event_type.value} frame {w.second.frame} "
                f"(gap={w.gap_frames})"
            )
        if len(flaps) > 10:
            print(f"  ... and {len(flaps) - 10} more")
        print("  Try raising --hysteresis-frames (e.g. 3–4) if these look like jitter.")
    else:
        print("\nNo rapid ENTER↔EXIT flapping detected.")

    print("\nZone analytics:")
    for zone_id, snap in analytics.all_snapshots().items():
        print(f"  {zone_id}: {snap.to_dict()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
