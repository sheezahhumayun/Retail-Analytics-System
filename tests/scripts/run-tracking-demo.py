"""Test Checkpoint 3 — annotated tracking (file / RTSP / webcam).

Usage::

    python tests/scripts/run-tracking-demo.py
    python tests/scripts/run-tracking-demo.py --backend onnx
    python tests/scripts/run-tracking-demo.py sample-data/entrance3.mp4
    python tests/scripts/run-tracking-demo.py rtsp://10.0.0.5/stream --camera-id entrance --duration 60 --preview
    python tests/scripts/run-tracking-demo.py 0 --camera-id desk --duration 30 --preview
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.scripts.demo_source import (
    add_source_args,
    iter_frames,
    open_source,
    resolve_camera_id,
    resolve_duration,
    warmup_source,
)

SAMPLE_DATA = REPO_ROOT / "sample-data"
OUTPUT_DIR = REPO_ROOT / "tests" / "videos"

SAMPLE_VIDEOS = ["entrance3.mp4"]

BOX_COLOR = (0, 180, 255)
TEXT_COLOR = (255, 255, 255)


def annotate_frame(cv2, frame, tracks):
    out = frame.copy()
    for t in tracks:
        x1, y1, x2, y2 = (int(round(v)) for v in t.bbox)
        cv2.rectangle(out, (x1, y1), (x2, y2), BOX_COLOR, 2)
        label = f"#{t.track_id} {t.confidence:.2f}"
        (tw, th), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        label_y1 = max(0, y1 - th - baseline - 4)
        cv2.rectangle(out, (x1, label_y1), (x1 + tw + 4, y1), BOX_COLOR, -1)
        cv2.putText(
            out,
            label,
            (x1 + 2, y1 - baseline - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            TEXT_COLOR,
            1,
            cv2.LINE_AA,
        )
    return out


def run_one_source(
    source: str,
    detector,
    backend: str,
    *,
    camera_id: str | None = None,
    target_fps: float = 10.0,
    duration: float | None = None,
    preview: bool = False,
) -> dict:
    import cv2

    from inference.tracking import Tracker

    cam = resolve_camera_id(source, camera_id)
    tracker = Tracker(camera_id=cam)

    probe = open_source(source, target_fps=target_fps)
    ok, first_frame = probe.read()
    if not ok:
        probe.release()
        raise RuntimeError(f"Could not read a frame from {source!r}")
    h, w = first_frame.shape[:2]
    probe.release()

    out_path = OUTPUT_DIR / f"tracking_{cam}_{backend}.mp4"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), target_fps, (w, h)
    )

    frame_count = 0
    track_frame_count = 0
    total_tracks = 0
    unique_ids: set[int] = set()
    infer_times: list[float] = []
    track_times: list[float] = []

    def process_frame(frame, ts: float):
        nonlocal frame_count, track_frame_count, total_tracks
        t0 = time.perf_counter()
        dets = detector.detect(frame, camera_id=cam, timestamp=ts)
        infer_times.append(time.perf_counter() - t0)

        t1 = time.perf_counter()
        tracks = tracker.update(dets)
        track_times.append(time.perf_counter() - t1)

        frame_count += 1
        if tracks:
            track_frame_count += 1
            total_tracks += len(tracks)
            unique_ids.update(t.track_id for t in tracks)

        annotated = annotate_frame(cv2, frame, tracks)
        writer.write(annotated)
        return annotated

    src = warmup_source(
        source,
        target_fps=target_fps,
        detector=detector,
        camera_id=cam,
    )

    for frame, ts in iter_frames(src, duration=duration, preview=False):
        annotated = process_frame(frame, ts)
        if preview:
            cv2.imshow("tracking", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    if preview:
        cv2.destroyWindow("tracking")

    src.release()
    writer.release()

    infer_fps = frame_count / sum(infer_times) if infer_times else 0.0
    track_fps = frame_count / sum(track_times) if track_times else 0.0

    return {
        "video": source,
        "backend": backend,
        "frames": frame_count,
        "frames_with_tracks": track_frame_count,
        "total_track_instances": total_tracks,
        "unique_track_ids": len(unique_ids),
        "infer_fps": infer_fps,
        "track_fps": track_fps,
        "output": str(out_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Tracking demo")
    parser.add_argument(
        "source",
        nargs="?",
        help="Optional: video file, rtsp:// URL, or webcam index. Omit to run bundled samples.",
    )
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    parser.add_argument("--camera-id", help="Camera id (default: derived from source)")
    parser.add_argument("--target-fps", type=float, default=10.0)
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Wall-clock seconds (live/webcam default 120; 0 = until Ctrl+C)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Show annotated frames in an OpenCV window (press q to stop early)",
    )
    args = parser.parse_args()

    from inference.detection import create_detector

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with create_detector(backend=args.backend) as detector:
        import cv2

        cap = cv2.VideoCapture(str(SAMPLE_DATA / SAMPLE_VIDEOS[0]))
        ok, warmup_frame = cap.read()
        cap.release()
        if ok:
            detector.detect(warmup_frame, camera_id="warmup")

        if args.source:
            duration = resolve_duration(args.source, args.duration)
            print(f"Processing {args.source}...")
            stats = run_one_source(
                args.source,
                detector,
                args.backend,
                camera_id=args.camera_id,
                target_fps=args.target_fps,
                duration=duration,
                preview=args.preview,
            )
            print(
                f"  {stats['frames']} frames, "
                f"{stats['unique_track_ids']} unique IDs, "
                f"infer {stats['infer_fps']:.1f} fps, "
                f"track {stats['track_fps']:.0f} fps"
            )
            print(f"  -> {stats['output']}")
            return 0

        results = []
        for name in SAMPLE_VIDEOS:
            path = SAMPLE_DATA / name
            if not path.exists():
                print(f"SKIP {name} — not found")
                continue
            print(f"Processing {name}...")
            stats = run_one_source(
                str(path),
                detector,
                args.backend,
                target_fps=args.target_fps,
            )
            results.append(stats)
            print(
                f"  {stats['frames']} frames, "
                f"{stats['unique_track_ids']} unique IDs, "
                f"infer {stats['infer_fps']:.1f} fps, "
                f"track {stats['track_fps']:.0f} fps"
            )
            print(f"  -> {stats['output']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
