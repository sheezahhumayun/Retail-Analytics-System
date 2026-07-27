"""Test Checkpoint 4 — detect + track + count over a sample video.

Loads a counting-line JSON (draw one with ``line_editor`` first) or uses a
built-in default line for quick smoke runs.

Usage (PowerShell — use one line, or backtick `` ` `` for continuation)::

    python tests/scripts/run-counting-demo.py sample-data/entrance.mp4
    python tests/scripts/run-counting-demo.py sample-data/CMMentrance.mp4 --line-config tests/videos/CMMentrance_line.json

``camera_id`` comes from the line JSON when ``--line-config`` is set (use the
same id when drawing the line: video stem, e.g. ``CMMentrance``).

Draw / replace the line config (interactive OpenCV window)::

    python -m analytics.counting.line_editor sample-data/entrance.mp4 --camera-id entrance --output tests/videos/entrance_line.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
    parser.add_argument("video", help="Video path")
    parser.add_argument(
        "--line-config",
        help="CountingLine JSON (from line_editor); uses default if omitted",
    )
    parser.add_argument(
        "--camera-id",
        help="Camera id stamped on detections/tracks/events (default: from line "
        "config if --line-config is set, else video filename without extension)",
    )
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    args = parser.parse_args()

    from analytics.counting import CountingLine, LineCounter
    from inference.detection import create_detector
    from inference.tracking import Tracker
    from inference.video import create_video_source

    video_path = Path(args.video)
    stem_camera_id = video_path.stem or "cam"

    if args.line_config:
        line = _load_line_config(Path(args.line_config))
        camera_id = args.camera_id or line.camera_id
    elif DEFAULT_LINE_PATH.is_file():
        line = CountingLine.load_json(DEFAULT_LINE_PATH)
        camera_id = args.camera_id or stem_camera_id
        if line.camera_id != camera_id:
            line = CountingLine.from_dict({**line.to_dict(), "camera_id": camera_id})
        print(f"Using bundled line config: {DEFAULT_LINE_PATH}")
    else:
        camera_id = args.camera_id or stem_camera_id
        cfg = {**DEFAULT_LINE, "camera_id": camera_id}
        line = CountingLine.from_dict(cfg)
        print("Using default line config (draw your own with line_editor):")
        print(json.dumps(cfg, indent=2))

    if line.camera_id != camera_id:
        line = CountingLine.from_dict({**line.to_dict(), "camera_id": camera_id})

    counter = LineCounter(line)
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

    with create_detector(backend=args.backend) as detector:
        src = create_video_source(str(video_path), target_fps=10)
        src.open()

        # Warmup
        ok, frame = src.read()
        if ok:
            detector.detect(frame, camera_id=camera_id)
            src = create_video_source(str(video_path), target_fps=10)
            src.open()

        events = []
        frame_idx = 0
        while True:
            ok, frame = src.read()
            if not ok:
                break
            dets = detector.detect(
                frame, camera_id=camera_id, timestamp=float(frame_idx)
            )
            frame_idx += 1
            tracks = tracker.update(dets)
            events.extend(counter.update(tracks))

        src.release()

    print(f"\n{camera_id}: {len(events)} crossing event(s)")
    for ev in events:
        print(ev.to_dict())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
