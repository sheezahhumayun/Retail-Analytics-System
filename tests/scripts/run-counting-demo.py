"""Test Checkpoint 4 — detect + track + count (file / RTSP / webcam).

Usage (PowerShell)::

    python tests/scripts/run-counting-demo.py sample-data/entrance.mp4
    python tests/scripts/run-counting-demo.py rtsp://10.0.0.5/stream --camera-id entrance --duration 120
    python tests/scripts/run-counting-demo.py 0 --camera-id desk --duration 60 --preview
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

DEFAULT_LINE_PATH = REPO_ROOT / "tests" / "videos" / "entrance_line.json"

DEFAULT_LINE = {
    "name": "main_entrance",
    "camera_id": "entrance",
    "x1": 50,
    "y1": 280,
    "x2": 590,
    "y2": 280,
    "inside_side": "left",
}


def _load_line_config(path: Path):
    from analytics.counting import CountingLine

    if not path.is_file():
        print(
            f"Line config not found: {path}\n"
            "Either omit --line-config to use the built-in default, or create one:\n"
            "  python -m analytics.counting.line_editor sample-data/CMMentrance.mp4 "
            f"--camera-id CMMentrance --output {path}",
            file=sys.stderr,
        )
        raise SystemExit(1)

    return CountingLine.load_json(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Entry/exit counting demo")
    add_source_args(parser)
    parser.add_argument(
        "--line-config",
        help="CountingLine JSON (from line_editor); uses default if omitted",
    )
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    args = parser.parse_args()

    from analytics.counting import CountingLine, LineCounter
    from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, EventBus
    from inference.detection import create_detector
    from inference.tracking import Tracker

    if args.line_config:
        line = _load_line_config(Path(args.line_config))
        camera_id = resolve_camera_id(args.source, args.camera_id or line.camera_id)
    elif DEFAULT_LINE_PATH.is_file():
        line = CountingLine.load_json(DEFAULT_LINE_PATH)
        camera_id = resolve_camera_id(args.source, args.camera_id)
        if line.camera_id != camera_id:
            line = CountingLine.from_dict({**line.to_dict(), "camera_id": camera_id})
        print(f"Using bundled line config: {DEFAULT_LINE_PATH}")
    else:
        camera_id = resolve_camera_id(args.source, args.camera_id)
        cfg = {**DEFAULT_LINE, "camera_id": camera_id}
        line = CountingLine.from_dict(cfg)
        print("Using default line config (draw your own with line_editor):")
        print(json.dumps(cfg, indent=2))

    if line.camera_id != camera_id:
        line = CountingLine.from_dict({**line.to_dict(), "camera_id": camera_id})

    duration = resolve_duration(args.source, args.duration)
    bus = EventBus()
    engine = AnalyticsEngine(
        bus,
        AnalyticsEngineConfig(camera_ids=[camera_id]),
    )
    counter = LineCounter(line, event_bus=bus)
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

    events = []
    last_ts = 0.0

    with create_detector(backend=args.backend) as detector:
        src = warmup_source(
            args.source,
            target_fps=args.target_fps,
            detector=detector,
            camera_id=camera_id,
        )

        for frame, ts in iter_frames(
            src,
            duration=duration,
            preview=args.preview,
            preview_window="counting",
        ):
            last_ts = ts
            dets = detector.detect(frame, camera_id=camera_id, timestamp=ts)
            events.extend(counter.update(tracker.update(dets)))

        print_processing_stats(src, target_fps=args.target_fps, last_ts=last_ts)
        src.release()

    occupancy_snap = engine.camera_occupancy(camera_id)
    if occupancy_snap is not None and occupancy_snap.total_entries > 0:
        print("\nOccupancy (via event bus):", occupancy_snap.to_dict())

    print(f"\n{camera_id}: {len(events)} crossing event(s)")
    for ev in events:
        print(ev.to_dict())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
