"""Snapshot Postgres connections during live-analytics worker lifecycle."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def pg_snapshot(label: str) -> str:
    query = (
        "SELECT pid, usename, application_name, client_addr, state, "
        "backend_start, left(query, 100) AS query_preview "
        "FROM pg_stat_activity WHERE datname = 'retail_analytics' "
        "ORDER BY backend_start;"
    )
    count_query = (
        "SELECT count(*) FROM pg_stat_activity WHERE datname = 'retail_analytics';"
    )
    count = subprocess.check_output(
        [
            "docker",
            "exec",
            "retail-analytics-postgres",
            "psql",
            "-U",
            "retail",
            "-d",
            "retail_analytics",
            "-t",
            "-c",
            count_query,
        ],
        text=True,
    ).strip()
    rows = subprocess.check_output(
        [
            "docker",
            "exec",
            "retail-analytics-postgres",
            "psql",
            "-U",
            "retail",
            "-d",
            "retail_analytics",
            "-c",
            query,
        ],
        text=True,
    )
    return f"\n=== {label} (count={count}) ===\n{rows}"


def main() -> int:
    from inference.pipeline.live_analytics_worker import (
        _start_live_analytics_worker,
        _stop_live_analytics_worker,
        reconcile_live_cameras,
    )
    from analytics.modules import MODULE_ENTRY_EXIT, MODULE_ZONES
    from database.models import Camera
    from database.seed import seed_reference_data
    from database.session import create_all, reset_engine, session_scope
    from sqlmodel import select

    CAMERA_A = "verify_live_a"
    CAMERA_B = "verify_live_b"
    VIDEO = "sample-data/town.mp4"

    def _upsert_camera(camera_id: str, *, modules: list[str]) -> None:
        from database.models import Store
        from database.seed import STORE_ID

        with session_scope() as session:
            session.merge(
                Camera(
                    id=camera_id,
                    store_id=STORE_ID,
                    name=f"Verify Live {camera_id}",
                    location="test",
                    rtsp_url=VIDEO,
                    source_type="live",
                    status="online",
                    analytics_modules=modules,
                )
            )

    def _disable_other_live_cameras(keep: set[str]) -> int:
        with session_scope() as session:
            cameras = session.exec(
                select(Camera).where(Camera.source_type == "live")
            ).all()
            disabled = 0
            for cam in cameras:
                if cam.id not in keep and cam.status != "disabled":
                    cam.status = "disabled"
                    session.add(cam)
                    disabled += 1
            return disabled

    print(pg_snapshot("baseline before any Python DB use"))

    create_all()
    seed_reference_data(force=True)
    _upsert_camera(CAMERA_A, modules=[MODULE_ENTRY_EXIT, MODULE_ZONES])
    _upsert_camera(CAMERA_B, modules=[MODULE_ZONES])
    n_disabled = _disable_other_live_cameras({CAMERA_A, CAMERA_B})
    print(f"Disabled {n_disabled} other live camera(s)")
    print(pg_snapshot("after create_all + seed + disable extras"))

    _start_live_analytics_worker(5)
    print(pg_snapshot("after worker start (writer holds 1 persistent session)"))

    try:
        for i in range(5):
            reconcile_live_cameras()
            print(pg_snapshot(f"after reconcile #{i + 1}"))
            time.sleep(0.5)
    finally:
        _stop_live_analytics_worker()
        reset_engine()
        print(pg_snapshot("after worker stop + reset_engine"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
