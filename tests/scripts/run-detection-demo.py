"""Test Checkpoint 2 deliverable — annotated detection videos + FPS baseline.

Runs PersonDetector over all 3 sample videos, draws bounding boxes + confidence
on each kept frame, writes annotated mp4s, and logs per-video average FPS as
the CPU baseline for future performance decisions (PRD §39 Milestone 1).

Reports TWO fps numbers per video:
  - infer_fps:         detector.detect() time only (what downstream modules
                        actually care about -- no drawing/encoding).
  - full_pipeline_fps: detect() + annotation drawing + mp4 encoding, i.e.
                        what this demo script itself takes wall-clock.
A one-frame warmup call happens before any video is timed, so PyTorch/ONNX
Runtime's first-call kernel-autotune/session-warmup cost doesn't land inside
whichever video happens to run first (it used to skew entrance.mp4 low).

Usage:
    python tests/scripts/run-detection-demo.py --backend ultralytics
    python tests/scripts/run-detection-demo.py sample-data/entrance.mp4
    python tests/scripts/run-detection-demo.py rtsp://10.0.0.5/stream --camera-id entrance --duration 60 --preview
    python tests/scripts/run-detection-demo.py 0 --camera-id desk --duration 30 --preview
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Make ``inference`` importable when run directly (repo_root/tests/scripts/..).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SAMPLE_DATA = REPO_ROOT / "sample-data"
OUTPUT_DIR = REPO_ROOT / "tests" / "videos"
BASELINE_LOG = OUTPUT_DIR / "detection_baseline.txt"

SAMPLE_VIDEOS = ["entrance.mp4", "store-floor.mp4", "checkout.mp4"]

BOX_COLOR = (0, 220, 0)       # BGR -- green
TEXT_COLOR = (255, 255, 255)  # BGR -- white


def annotate_frame(cv2, frame, detections):
    """Draw bbox + class + confidence on a copy of ``frame``."""
    out = frame.copy()
    for d in detections:
        x1, y1, x2, y2 = (int(round(v)) for v in d.bbox)
        cv2.rectangle(out, (x1, y1), (x2, y2), BOX_COLOR, 2)
        label = f"{d.class_name} {d.confidence:.2f}"
        (tw, th), baseline = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
        )
        label_y1 = max(0, y1 - th - baseline - 4)
        cv2.rectangle(
            out, (x1, label_y1), (x1 + tw + 4, y1), BOX_COLOR, -1
        )
        cv2.putText(
            out, label, (x1 + 2, y1 - baseline - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1, cv2.LINE_AA,
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
    """Run detection over one source, write annotated mp4, return stats."""
    import cv2

    from tests.scripts.demo_source import (
        iter_frames,
        open_source,
        resolve_camera_id,
        warmup_source,
    )

    cam = resolve_camera_id(source, camera_id)

    probe = open_source(source, target_fps=target_fps)
    ok, first_frame = probe.read()
    if not ok:
        probe.release()
        raise RuntimeError(f"Could not read a frame from {source!r}")

    h, w = first_frame.shape[:2]
    probe.release()

    out_path = OUTPUT_DIR / f"{cam}_annotated.mp4"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), target_fps, (w, h)
    )

    frame_count = 0
    total_detections = 0
    busiest_frame_idx = 0
    busiest_media_time_s = 0.0
    busiest_frame_count = -1

    infer_time = 0.0
    pipeline_t_start = time.perf_counter()

    src = warmup_source(
        source,
        target_fps=target_fps,
        detector=detector,
        camera_id=cam,
    )

    for frame, media_ts in iter_frames(src, duration=duration, preview=False):
        t0 = time.perf_counter()
        detections = detector.detect(frame, camera_id=cam, timestamp=media_ts)
        infer_time += time.perf_counter() - t0

        total_detections += len(detections)
        if len(detections) > busiest_frame_count:
            busiest_frame_count = len(detections)
            busiest_frame_idx = frame_count
            busiest_media_time_s = media_ts

        annotated = annotate_frame(cv2, frame, detections)
        writer.write(annotated)
        frame_count += 1

        if preview:
            cv2.imshow("detection", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    if preview:
        cv2.destroyWindow("detection")

    pipeline_elapsed = time.perf_counter() - pipeline_t_start
    writer.release()
    src.release()

    infer_fps = frame_count / infer_time if infer_time > 0 else 0.0
    pipeline_fps = frame_count / pipeline_elapsed if pipeline_elapsed > 0 else 0.0

    return {
        "video": Path(source).name if not source.startswith("rtsp") else source,
        "backend": backend,
        "frames": frame_count,
        "infer_time_s": infer_time,
        "infer_fps": infer_fps,
        "pipeline_elapsed_s": pipeline_elapsed,
        "pipeline_fps": pipeline_fps,
        "total_detections": total_detections,
        "avg_detections_per_frame": total_detections / frame_count if frame_count else 0,
        "busiest_frame_idx": busiest_frame_idx,
        "busiest_media_time_s": busiest_media_time_s,
        "busiest_frame_count": busiest_frame_count,
        "output_path": out_path,
    }


def run_one_video(video_path: Path, detector, backend: str) -> dict:
    return run_one_source(str(video_path), detector, backend)


def warm_up(detector) -> None:
    """Run one throwaway detect() call before timing starts.

    PyTorch's CPU backend (MKL/oneDNN) and ONNX Runtime's CPU EP both pay a
    one-time kernel-autotune / session-warmup cost on their first inference
    call. Without this, that cost silently lands inside whichever video
    happens to be processed first, making it look artificially slow relative
    to the others (this is what was happening to entrance.mp4).
    """
    import numpy as np

    dummy_frame = np.zeros((360, 640, 3), dtype=np.uint8)
    detector.detect(dummy_frame, camera_id="warmup")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        nargs="?",
        help="Optional: video file, rtsp:// URL, or webcam index. Omit to run bundled samples.",
    )
    parser.add_argument(
        "--backend",
        choices=["ultralytics", "onnx"],
        default="ultralytics",
        help="Detection backend to benchmark (default: ultralytics)",
    )
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
    from tests.scripts.demo_source import resolve_duration

    if args.source:
        if not args.source.isdigit() and not args.source.lower().startswith(
            ("rtsp://", "rtsps://", "rtmp://")
        ):
            if not Path(args.source).exists():
                print(f"ERROR: source not found: {args.source}")
                sys.exit(1)
    elif not SAMPLE_DATA.is_dir():
        print(f"ERROR: sample data directory not found at {SAMPLE_DATA}")
        sys.exit(1)

    print(f"Loading detector (backend={args.backend})...")
    detector = create_detector(backend=args.backend)

    print("Warming up model (excluded from timed results)...")
    warm_up(detector)

    results = []
    try:
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
            results.append(stats)
            print(
                f"  {stats['frames']} frames | "
                f"infer: {stats['infer_fps']:.1f} FPS "
                f"({stats['infer_time_s']:.1f}s) | "
                f"full pipeline: {stats['pipeline_fps']:.1f} FPS | "
                f"{stats['total_detections']} total detections"
            )
        else:
            for name in SAMPLE_VIDEOS:
                video_path = SAMPLE_DATA / name
                if not video_path.exists():
                    print(f"  skipping {name} (not found)")
                    continue
                print(f"Processing {name}...")
                stats = run_one_video(video_path, detector, args.backend)
                results.append(stats)
                print(
                    f"  {stats['frames']} frames | "
                    f"infer: {stats['infer_fps']:.1f} FPS "
                    f"({stats['infer_time_s']:.1f}s) | "
                    f"full pipeline (detect+draw+encode): "
                    f"{stats['pipeline_fps']:.1f} FPS "
                    f"({stats['pipeline_elapsed_s']:.1f}s) | "
                    f"{stats['total_detections']} total detections "
                    f"(avg {stats['avg_detections_per_frame']:.1f}/frame)"
                )
    finally:
        detector.release()

    if not results:
        print("No videos processed -- nothing to log.")
        sys.exit(1)

    # ---- Write / append the baseline log -------------------------------- #
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(BASELINE_LOG, "a", encoding="utf-8") as f:
        f.write(f"\n--- run at {timestamp} | backend={args.backend} (warmed up) ---\n")
        for r in results:
            f.write(
                f"{r['video']}: infer={r['infer_fps']:.1f} FPS, "
                f"pipeline={r['pipeline_fps']:.1f} FPS "
                f"({r['frames']} frames), "
                f"{r['total_detections']} detections total\n"
            )

    # ---- Manual eyeball guidance ----------------------------------------- #
    print("\n=== Test Checkpoint 2 -- manual review ===")
    print(f"Backend: {args.backend}")
    print(f"Baseline log: {BASELINE_LOG}")
    print("\nAnnotated videos to review:")
    for r in results:
        busiest_time_s = r["busiest_media_time_s"]
        print(
            f"  {r['output_path']}\n"
            f"    -> check kept frame {r['busiest_frame_idx']} "
            f"(media t={busiest_time_s:.1f}s, busiest at {r['busiest_frame_count']} people) "
            f"for box tracking quality"
        )
    print(
        "\nLook for: boxes staying on real people (not carts/mannequins/reflections), "
        "no wild flicker frame-to-frame, boxes not clipping through people."
    )


if __name__ == "__main__":
    main()