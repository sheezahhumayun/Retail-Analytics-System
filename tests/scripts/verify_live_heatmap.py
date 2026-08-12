"""Verify live worker writes heatmap NPZ files when heatmap module is enabled."""
from __future__ import annotations

import logging
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analytics.modules import MODULE_HEATMAP
from database.models import Camera, Organization, Store
from database.seed import ORG_ID, STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope
from inference.pipeline.live_analytics_worker import (
    _analytics_states,
    _start_live_analytics_worker,
    _stop_live_analytics_worker,
    get_running_live_camera_ids,
    reconcile_live_cameras,
)

CAMERA_ID = "verify_live_heatmap"
VIDEO = "sample-data/town.mp4"
HEATMAP_ROOT = REPO_ROOT / "data" / "heatmaps"


def _upsert_heatmap_camera() -> None:
    with session_scope() as session:
        session.merge(
            Camera(
                id=CAMERA_ID,
                store_id=STORE_ID,
                name="Verify Live Heatmap",
                location="test",
                rtsp_url=VIDEO,
                source_type="live",
                status="online",
                analytics_modules=[MODULE_HEATMAP],
            )
        )


def _disable_other_live_cameras() -> int:
    with session_scope() as session:
        from sqlmodel import select

        cameras = session.exec(
            select(Camera).where(Camera.source_type == "live")
        ).all()
        disabled = 0
        for cam in cameras:
            if cam.id != CAMERA_ID and cam.status != "disabled":
                cam.status = "disabled"
                session.add(cam)
                disabled += 1
        return disabled


def _npz_files(camera_id: str) -> list[Path]:
    cam_dir = HEATMAP_ROOT / camera_id
    if not cam_dir.is_dir():
        return []
    return sorted(cam_dir.rglob("*.npz"))


def _density_sum(path: Path) -> float:
    data = np.load(path, allow_pickle=False)
    return float(data["density"].sum() + data["trajectory"].sum())


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")

    create_all()
    seed_reference_data(force=True)
    _upsert_heatmap_camera()
    n_disabled = _disable_other_live_cameras()
    print(f"Disabled {n_disabled} other live camera(s)")

    with session_scope() as session:
        org = session.get(Organization, ORG_ID)
        assert org is not None and org.status == "active"
        store = session.get(Store, STORE_ID)
        assert store is not None

    # Clean prior test data
    for p in _npz_files(CAMERA_ID):
        p.unlink()

    print("Starting live analytics worker...")
    _start_live_analytics_worker(5)

    try:
        started, stopped = reconcile_live_cameras()
        print(f"Reconcile: started={started}, stopped={stopped}")

        deadline = time.time() + 60
        while time.time() < deadline:
            if CAMERA_ID in get_running_live_camera_ids():
                break
            time.sleep(1)
        else:
            print("FAIL: camera not picked up within 60s")
            return 1

        state = _analytics_states.get(CAMERA_ID)
        print(f"needs_heatmap={getattr(state, 'needs_heatmap', None)}")

        print("Waiting 60s for YOLO + heatmap accumulation...")
        time.sleep(60)

        state = _analytics_states.get(CAMERA_ID)
        engine = getattr(state, "heatmap_engine", None) if state else None
        in_memory_hits = engine._live.total_hits() if engine is not None else 0
        print(f"In-memory hits before shutdown: {in_memory_hits}")

        # Graceful shutdown flush — NPZ only written on hour-roll or flush()
        print("Stopping worker (graceful shutdown flush)...")
        _stop_live_analytics_worker()

        files = _npz_files(CAMERA_ID)
        print(f"NPZ files for {CAMERA_ID}: {len(files)}")
        for f in files:
            data = np.load(f, allow_pickle=False)
            hits = _density_sum(f)
            print(
                f"  {f.relative_to(REPO_ROOT)}: "
                f"spec={int(data['spec_width'])}x{int(data['spec_height'])} "
                f"density_sum={hits:.1f}"
            )

        if not files:
            print("FAIL: no NPZ files written")
            return 1

        total_hits = sum(_density_sum(f) for f in files)
        if total_hits <= 0:
            print("FAIL: NPZ files exist but density is empty")
            return 1

        today = date.today().isoformat()
        today_files = [f for f in files if today in str(f)]
        print(f"Today's buckets ({today}): {len(today_files)}")

        print("PASS: live heatmap generation verified")
        return 0
    except Exception:
        _stop_live_analytics_worker()
        raise
    finally:
        reset_engine()


if __name__ == "__main__":
    raise SystemExit(main())
