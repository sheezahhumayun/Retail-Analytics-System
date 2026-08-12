"""Verify recording_start wiring via the running HTTP API (not CLI).

Usage: backend/.venv/Scripts/python.exe tests/scripts/verify_api_recording_start.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from sqlalchemy import func
from sqlmodel import select

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.auth import create_access_token
from database.models import Event, OccupancyMetric, User
from database.session import session_scope

API = "http://127.0.0.1:8000/api"
CAMERA_ID = "cam_outside_cam_00a514"
EXPLICIT_START = "2026-08-11T14:00:00+00:00"


def _wetrades_admin_token() -> str:
    with session_scope() as session:
        user = session.exec(
            select(User).where(User.org_id == "wetrades", User.role == "admin")
        ).first()
        if user is None:
            raise RuntimeError("No wetrades org admin user found")
        token, _ = create_access_token(user)
        return token


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _poll_process(token: str, camera_id: str, timeout_s: int = 600) -> dict:
    deadline = time.time() + timeout_s
    last: dict = {}
    while time.time() < deadline:
        resp = requests.get(
            f"{API}/cameras/{camera_id}/process-status",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        last = resp.json()
        if last.get("status") != "running":
            return last
        time.sleep(5)
    raise TimeoutError(f"Processing did not complete within {timeout_s}s: {last}")


def _db_snapshot(camera_id: str, since: datetime | None) -> dict:
    with session_scope() as session:
        ev_stmt = select(Event.timestamp, Event.event_type).where(Event.camera_id == camera_id)
        occ_stmt = select(
            OccupancyMetric.timestamp,
            OccupancyMetric.current_occupancy,
        ).where(OccupancyMetric.camera_id == camera_id)
        if since is not None:
            ev_stmt = ev_stmt.where(Event.timestamp > since)
            occ_stmt = occ_stmt.where(OccupancyMetric.timestamp > since)
        events = session.exec(ev_stmt.order_by(Event.timestamp.desc()).limit(10)).all()
        occupancy = session.exec(occ_stmt.order_by(OccupancyMetric.timestamp.desc()).limit(10)).all()
        ev_bounds = session.exec(
            select(func.min(Event.timestamp), func.max(Event.timestamp)).where(
                Event.camera_id == camera_id,
                *( [Event.timestamp > since] if since else [] ),
            )
        ).one()
        occ_bounds = session.exec(
            select(func.min(OccupancyMetric.timestamp), func.max(OccupancyMetric.timestamp)).where(
                OccupancyMetric.camera_id == camera_id,
                *( [OccupancyMetric.timestamp > since] if since else [] ),
            )
        ).one()
    return {
        "event_bounds": ev_bounds,
        "occ_bounds": occ_bounds,
        "recent_events": events,
        "recent_occupancy": occupancy,
    }


def main() -> int:
    token = _wetrades_admin_token()

    print("=== BASELINE (max timestamps before this run) ===")
    baseline = _db_snapshot(CAMERA_ID, None)
    print("all_event_bounds", baseline["event_bounds"])
    print("all_occ_bounds", baseline["occ_bounds"])

    baseline_event_max = baseline["event_bounds"][1]
    baseline_occ_max = baseline["occ_bounds"][1]
    since = max(
        t for t in (baseline_event_max, baseline_occ_max) if t is not None
    ) if baseline_event_max or baseline_occ_max else None
    print("filter_since", since)

    test_resp = requests.post(
        f"{API}/cameras/{CAMERA_ID}/test",
        headers=_headers(token),
        timeout=60,
    )
    print("\n=== POST /test ===")
    print("status_code", test_resp.status_code)
    print(json.dumps(test_resp.json(), indent=2))

    body = {"recording_start": EXPLICIT_START}
    print("\n=== POST /process (with recording_start) ===")
    print("request_body", json.dumps(body))
    proc_resp = requests.post(
        f"{API}/cameras/{CAMERA_ID}/process",
        headers=_headers(token),
        json=body,
        timeout=60,
    )
    print("status_code", proc_resp.status_code)
    print(json.dumps(proc_resp.json(), indent=2))
    if proc_resp.status_code != 200:
        return 1

    final = _poll_process(token, CAMERA_ID)
    print("final_status", json.dumps(final, indent=2))

    explicit_db = _db_snapshot(CAMERA_ID, since)
    print("\n=== DB after explicit-anchor API run (newer than baseline) ===")
    print("event_bounds", explicit_db["event_bounds"])
    print("occ_bounds", explicit_db["occ_bounds"])
    print("recent_events", explicit_db["recent_events"])
    print("recent_occupancy", explicit_db["recent_occupancy"])

    # step d: no body
    after_explicit_max = explicit_db["event_bounds"][1] or since
    since2 = after_explicit_max if after_explicit_max else since

    print("\n=== POST /process (no body) ===")
    print("request_body", "(empty / omitted)")
    proc2 = requests.post(
        f"{API}/cameras/{CAMERA_ID}/process",
        headers=_headers(token),
        timeout=60,
    )
    print("status_code", proc2.status_code)
    print(json.dumps(proc2.json(), indent=2))
    if proc2.status_code != 200:
        return 1

    final2 = _poll_process(token, CAMERA_ID)
    print("final_status", json.dumps(final2, indent=2))

    default_db = _db_snapshot(CAMERA_ID, since2)
    print("\n=== DB after default-anchor API run (newer than explicit run) ===")
    print("now_utc", datetime.now(timezone.utc))
    print("event_bounds", default_db["event_bounds"])
    print("occ_bounds", default_db["occ_bounds"])
    print("recent_events", default_db["recent_events"])
    print("recent_occupancy", default_db["recent_occupancy"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
