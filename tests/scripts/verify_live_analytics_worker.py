"""Manual verification for continuous live analytics.

Requires Postgres (docker compose) and inference venv with YOLO weights.

Usage (repo root, inference venv active)::

    python tests/scripts/verify_live_analytics_worker.py
"""

from __future__ import annotations

import json
import logging
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import func
from sqlmodel import select

from analytics.modules import MODULE_ENTRY_EXIT, MODULE_ZONES
from inference.pipeline.live_analytics_worker import (
    _start_live_analytics_worker,
    _stop_live_analytics_worker,
    get_io_worker_diagnostics,
    get_running_live_camera_ids,
    list_live_io_thread_names,
    reconcile_live_cameras,
    stop_live_workers_for_org,
)
from database.models import Camera, CountingLine, Event, Organization, Store, Zone
from database.seed import ORG_ID, STORE_ID, seed_reference_data
from database.session import create_all, session_scope


CAMERA_A = "verify_live_a"
CAMERA_B = "verify_live_b"
VIDEO = "sample-data/town.mp4"
TOWN_ZONES = REPO_ROOT / "tests" / "videos" / "town_zones.json"
ENTRANCE_LINE = REPO_ROOT / "tests" / "videos" / "entrance_line.json"


def _seed_camera_geometry(camera_id: str, *, with_counting_line: bool) -> None:
    zone_config = json.loads(TOWN_ZONES.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    with session_scope() as session:
        for z in zone_config.get("zones", []):
            zone_id = f"{camera_id}_{z['zone_id']}"
            session.merge(
                Zone(
                    id=zone_id,
                    camera_id=camera_id,
                    name=z.get("zone_name", z["zone_id"]),
                    polygon_coords=z["polygon_coordinates"],
                    zone_type=z.get("zone_type", "general"),
                    analytics_enabled=z.get("analytics_enabled", True),
                )
            )
        if with_counting_line and ENTRANCE_LINE.is_file():
            line = json.loads(ENTRANCE_LINE.read_text(encoding="utf-8"))
            session.merge(
                CountingLine(
                    id=f"line_{camera_id}",
                    camera_id=camera_id,
                    name=line.get("name", "verify_line"),
                    point_a={"x": line["x1"], "y": line["y1"]},
                    point_b={"x": line["x2"], "y": line["y2"]},
                    direction="left_is_inside",
                    created_at=now,
                )
            )


def _upsert_camera(
    camera_id: str,
    *,
    modules: list[str],
) -> None:
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


def _live_io_threads() -> list[str]:
    return [t.name for t in threading.enumerate() if t.name.startswith("live-io-")]


def _event_breakdown(camera_id: str) -> dict[str, int]:
    with session_scope() as session:
        rows = session.exec(
            select(Event.event_type, func.count())
            .where(Event.camera_id == camera_id)
            .group_by(Event.event_type)
        ).all()
    return {str(event_type): int(count) for event_type, count in rows}


def _event_count(camera_id: str) -> int:
    with session_scope() as session:
        return int(
            session.exec(
                select(func.count())
                .select_from(Event)
                .where(Event.camera_id == camera_id)
            ).one()
        )


def _disable_other_live_cameras(keep: set[str]) -> int:
    """Disable live cameras outside ``keep`` so verification does not reconcile the whole DB."""
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


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
    from database.session import reset_engine

    create_all()
    seed_reference_data(force=True)

    _upsert_camera(CAMERA_A, modules=[MODULE_ENTRY_EXIT, MODULE_ZONES])
    _upsert_camera(CAMERA_B, modules=[MODULE_ZONES])
    _seed_camera_geometry(CAMERA_A, with_counting_line=True)
    _seed_camera_geometry(CAMERA_B, with_counting_line=False)
    n_disabled = _disable_other_live_cameras({CAMERA_A, CAMERA_B})
    print(f"Disabled {n_disabled} other live camera(s) in DB")

    with session_scope() as session:
        org = session.get(Organization, ORG_ID)
        assert org is not None and org.status == "active"
        store = session.get(Store, STORE_ID)
        assert store is not None

    print("Starting live analytics worker (reconcile interval=5s)...")
    _start_live_analytics_worker(5)

    try:
        started, stopped = reconcile_live_cameras()
        print(f"Initial reconcile: started={started}, stopped={stopped}")

        deadline = time.time() + 45
        running: list[str] = []
        while time.time() < deadline:
            running = get_running_live_camera_ids()
            if CAMERA_A in running and CAMERA_B in running:
                break
            time.sleep(1)

        print(f"Running cameras after reconcile: {running}")
        if CAMERA_A not in running or CAMERA_B not in running:
            print("FAIL: worker did not pick up both live cameras within 45s")
            return 1

        print("Waiting 45s for frames to process (YOLO warmup + zone dwell)...")
        time.sleep(45)

        events_a = _event_count(CAMERA_A)
        events_b = _event_count(CAMERA_B)
        print(f"Event counts: {CAMERA_A}={events_a}, {CAMERA_B}={events_b}")
        print(f"Event breakdown {CAMERA_A}: {_event_breakdown(CAMERA_A)}")
        print(f"Event breakdown {CAMERA_B}: {_event_breakdown(CAMERA_B)}")

        if events_a == 0 and events_b == 0:
            print("FAIL: no events persisted for either camera")
            return 1

        with session_scope() as session:
            entry_a = session.exec(
                select(func.count())
                .select_from(Event)
                .where(Event.camera_id == CAMERA_A, Event.event_type == "ENTRY")
            ).one()
            entry_b = session.exec(
                select(func.count())
                .select_from(Event)
                .where(Event.camera_id == CAMERA_B, Event.event_type == "ENTRY")
            ).one()

        print(f"ENTRY events: {CAMERA_A}={entry_a}, {CAMERA_B}={entry_b}")
        if entry_a > 0 and entry_b > 0:
            print("FAIL: camera B should not emit ENTRY (entry_exit disabled)")
            return 1
        if entry_a == 0:
            print(
                "WARN: no ENTRY on camera A yet (may need counting line geometry); "
                "continuing with org-disable check"
            )

        print(
            "I/O threads BEFORE org-disable:",
            sorted(_live_io_threads()),
            "registry:",
            list_live_io_thread_names(),
            "diagnostics:",
            get_io_worker_diagnostics(),
        )

        stopped_count = stop_live_workers_for_org(ORG_ID)
        running_after = get_running_live_camera_ids()
        io_after = _live_io_threads()
        diag_after = get_io_worker_diagnostics()
        print(f"Org disable stop: stopped={stopped_count}, running={running_after}")
        print(
            "I/O threads AFTER org-disable:",
            sorted(io_after),
            "registry:",
            list_live_io_thread_names(),
            "diagnostics:",
            diag_after,
        )
        if io_after:
            print("FAIL: live-io threads still alive after org disable")
            return 1
        if running_after:
            print("FAIL: cameras still running after org disable")
            return 1

        print("PASS: live analytics worker verification succeeded")
        return 0
    finally:
        _stop_live_analytics_worker()
        reset_engine()


if __name__ == "__main__":
    raise SystemExit(main())
