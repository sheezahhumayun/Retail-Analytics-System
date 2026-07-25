"""Test Checkpoint 3 deliverable — annotated tracking videos.

Runs detect + track over all 3 sample videos, draws bounding boxes + track IDs
on each kept frame, and writes annotated mp4s to ``tests/videos/``.

Usage:
    python tests/scripts/run-tracking-demo.py
    python tests/scripts/run-tracking-demo.py --backend onnx
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SAMPLE_DATA = REPO_ROOT / "sample-data"
OUTPUT_DIR = REPO_ROOT / "tests" / "videos"

SAMPLE_VIDEOS = ["CMMentrance.mp4", "CMMstore-floor.mp4", "CMMcheckout.mp4"]

BOX_COLOR = (0, 180, 255)   # BGR — orange
TEXT_COLOR = (255, 255, 255)


def annotate_frame(cv2, frame, tracks):
    """Draw bbox + track ID on a copy of ``frame``."""
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


def run_one_video(video_path: Path, detector, backend: str) -> dict:
    import cv2

    from inference.tracking import Tracker
    from inference.video import create_video_source

    camera_id = video_path.stem
    tracker = Tracker(camera_id=camera_id)

    src = create_video_source(str(video_path), target_fps=10)
    src.open()

    ok, first_frame = src.read()
    if not ok:
        src.release()
        raise RuntimeError(f"Could not read a frame from {video_path}")

    h, w = first_frame.shape[:2]
    out_path = OUTPUT_DIR / f"tracking_{camera_id}_{backend}.mp4"
    writer = cv2.VideoWriter(
        str(out_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        10.0,
        (w, h),
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
        dets = detector.detect(frame, camera_id=camera_id, timestamp=ts)
        infer_times.append(time.perf_counter() - t0)

        t1 = time.perf_counter()
        tracks = tracker.update(dets)
        track_times.append(time.perf_counter() - t1)

        frame_count += 1
        if tracks:
            track_frame_count += 1
            total_tracks += len(tracks)
            unique_ids.update(t.track_id for t in tracks)

        writer.write(annotate_frame(cv2, frame, tracks))

    process_frame(first_frame, time.time())

    while True:
        ok, frame = src.read()
        if not ok:
            break
        process_frame(frame, time.time())

    src.release()
    writer.release()

    infer_fps = frame_count / sum(infer_times) if infer_times else 0.0
    track_fps = frame_count / sum(track_times) if track_times else 0.0

    return {
        "video": video_path.name,
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
    parser = argparse.ArgumentParser(description="Tracking demo over sample videos")
    parser.add_argument(
        "--backend",
        choices=["ultralytics", "onnx"],
        default="ultralytics",
        help="Detection backend (tracking is backend-agnostic)",
    )
    args = parser.parse_args()

    from inference.detection import create_detector

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with create_detector(backend=args.backend) as detector:
        # Warmup — same rationale as detection demo.
        import cv2

        cap = cv2.VideoCapture(str(SAMPLE_DATA / SAMPLE_VIDEOS[0]))
        ok, warmup_frame = cap.read()
        cap.release()
        if ok:
            detector.detect(warmup_frame, camera_id="warmup")

        results = []
        for name in SAMPLE_VIDEOS:
            path = SAMPLE_DATA / name
            if not path.exists():
                print(f"SKIP {name} — not found")
                continue
            print(f"Processing {name}...")
            stats = run_one_video(path, detector, args.backend)
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
