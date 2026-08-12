"""Print per-camera event-type breakdown while subprocess worker is running."""

from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import func
from sqlmodel import select

from analytics.modules import MODULE_ENTRY_EXIT, MODULE_ZONES
from database.models import Camera, Event, Organization
from database.seed import ORG_ID, STORE_ID, seed_reference_data
from database.session import create_all, session_scope

from tests.scripts.verify_live_analytics_worker import (
    CAMERA_A,
    CAMERA_B,
    _disable_other_live_cameras,
    _event_breakdown,
    _seed_camera_geometry,
    _upsert_camera,
)


def main() -> int:
    create_all()
    seed_reference_data(force=True)
    with session_scope() as session:
        org = session.get(Organization, ORG_ID)
        assert org is not None
        org.status = "active"
        session.add(org)

    _upsert_camera(CAMERA_A, modules=[MODULE_ENTRY_EXIT, MODULE_ZONES])
    _upsert_camera(CAMERA_B, modules=[MODULE_ZONES])
    _seed_camera_geometry(CAMERA_A, with_counting_line=True)
    _seed_camera_geometry(CAMERA_B, with_counting_line=False)
    n_disabled = _disable_other_live_cameras({CAMERA_A, CAMERA_B})
    print(f"Disabled {n_disabled} other live camera(s)")

    print("Waiting 60s for subprocess worker reconcile + processing...")
    time.sleep(60)

    for camera_id in (CAMERA_A, CAMERA_B):
        with session_scope() as session:
            cam = session.get(Camera, camera_id)
            modules = cam.analytics_modules if cam else None
        breakdown = _event_breakdown(camera_id)
        total = sum(breakdown.values())
        print(f"{camera_id} modules={modules} total={total} breakdown={breakdown}")

    entry_a = _event_breakdown(CAMERA_A).get("ENTRY", 0)
    entry_b = _event_breakdown(CAMERA_B).get("ENTRY", 0)
    print(f"ENTRY: {CAMERA_A}={entry_a}, {CAMERA_B}={entry_b}")
    if total == 0:
        return 1
    if entry_b > 0:
        print("FAIL: camera B should not emit ENTRY")
        return 1
    print("PASS: module gating via subprocess entrypoint")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
