"""Reproduce store.mp4 -> town.mp4 spec-mismatch via process_recorded (no crash)."""
from __future__ import annotations

import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analytics.heatmaps import HeatmapStore, HourBucketKey
from analytics.modules import MODULE_HEATMAP
from database.models import Camera
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, session_scope
from inference.pipeline.process_recorded import process_recorded_camera

CAMERA_ID = "verify_recorded_spec"
STORE_MP4 = REPO_ROOT / "sample-data" / "store.mp4"
TOWN_MP4 = REPO_ROOT / "sample-data" / "town.mp4"
HEATMAP_ROOT = REPO_ROOT / "data" / "heatmaps"


def _upsert_camera(video_path: str) -> None:
    with session_scope() as session:
        session.merge(
            Camera(
                id=CAMERA_ID,
                store_id=STORE_ID,
                name="Verify Recorded Spec",
                location="test",
                rtsp_url=video_path,
                source_type="recorded",
                status="online",
                analytics_modules=[MODULE_HEATMAP],
            )
        )


def _latest_bucket(camera_id: str) -> tuple[Path, float, int, int] | None:
    files = sorted((HEATMAP_ROOT / camera_id).rglob("*.npz")) if (HEATMAP_ROOT / camera_id).is_dir() else []
    if not files:
        return None
    path = files[-1]
    data = np.load(path, allow_pickle=False)
    hits = float(data["density"].sum() + data["trajectory"].sum())
    return path, hits, int(data["spec_width"]), int(data["spec_height"])


def main() -> int:
    if not STORE_MP4.is_file() or not TOWN_MP4.is_file():
        print("FAIL: sample videos missing")
        return 1

    create_all()
    seed_reference_data(force=True)

    cam_dir = HEATMAP_ROOT / CAMERA_ID
    if cam_dir.is_dir():
        shutil.rmtree(cam_dir)

    print("Run 1: store.mp4 (expected ~640x361)...")
    _upsert_camera("sample-data/store.mp4")
    r1 = process_recorded_camera(CAMERA_ID, backend="ultralytics", target_fps=10.0)
    print(f"  result: {r1.get('status', r1)}")
    b1 = _latest_bucket(CAMERA_ID)
    if b1 is None:
        print("FAIL: no NPZ after run 1")
        return 1
    path1, hits1, w1, h1 = b1
    print(f"  bucket: {path1.relative_to(REPO_ROOT)} spec={w1}x{h1} hits={hits1:.1f}")

    print("Run 2: town.mp4 (expected ~640x360, must not crash)...")
    _upsert_camera("sample-data/town.mp4")
    try:
        r2 = process_recorded_camera(CAMERA_ID, backend="ultralytics", target_fps=10.0)
    except Exception as exc:
        print(f"FAIL: run 2 raised {exc!r}")
        return 1
    print(f"  result: {r2.get('status', r2)}")
    b2 = _latest_bucket(CAMERA_ID)
    if b2 is None:
        print("FAIL: no NPZ after run 2")
        return 1
    path2, hits2, w2, h2 = b2
    print(f"  bucket: {path2.relative_to(REPO_ROOT)} spec={w2}x{h2} hits={hits2:.1f}")

    if w2 == w1 and h2 == h1:
        print("WARN: specs identical (videos may have same downscaled size on this machine)")
    else:
        print(f"Spec changed {w1}x{h1} -> {w2}x{h2} — overwrite succeeded (no crash)")

    print("PASS: recorded reprocess with different resolution completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
