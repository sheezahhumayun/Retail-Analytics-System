"""Verify live analytics via a real backend-started subprocess (step 7)."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlalchemy import func
from sqlmodel import select

from analytics.modules import MODULE_ENTRY_EXIT, MODULE_ZONES
from backend.app.services.passwords import hash_password
from database.models import Camera, CountingLine, Event, Organization, Superadmin, Zone
from database.seed import ORG_ID, STORE_ID, seed_reference_data
from database.session import create_all, session_scope

API = "http://127.0.0.1:8001/api"
CAMERA_A = "verify_live_a"
CAMERA_B = "verify_live_b"
VIDEO = "sample-data/town.mp4"
TOWN_ZONES = REPO_ROOT / "tests" / "videos" / "town_zones.json"
ENTRANCE_LINE = REPO_ROOT / "tests" / "videos" / "entrance_line.json"
SUPERADMIN_EMAIL = "superadmin@test.local"
SUPERADMIN_PASSWORD = "superadmin-test-pass"


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


def _upsert_camera(camera_id: str, *, modules: list[str]) -> None:
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


def _event_count(camera_id: str) -> int:
    with session_scope() as session:
        return int(
            session.exec(
                select(func.count())
                .select_from(Event)
                .where(Event.camera_id == camera_id)
            ).one()
        )


def _ensure_superadmin() -> None:
    with session_scope() as session:
        if session.get(Superadmin, "superadmin_test") is None:
            session.add(
                Superadmin(
                    id="superadmin_test",
                    name="Superadmin Test",
                    email=SUPERADMIN_EMAIL,
                    password_hash=hash_password(SUPERADMIN_PASSWORD),
                )
            )


def _ensure_org_active() -> None:
    with session_scope() as session:
        org = session.get(Organization, ORG_ID)
        assert org is not None
        org.status = "active"
        session.add(org)


def main() -> int:
    print("=== Step 7: verify via real backend (port 8001) ===")

    health = requests.get("http://127.0.0.1:8001/health", timeout=5)
    print(f"GET /health -> {health.status_code} {health.json()}")
    if health.status_code != 200:
        return 1

    create_all()
    seed_reference_data(force=True)
    _ensure_superadmin()
    _ensure_org_active()
    _upsert_camera(CAMERA_A, modules=[MODULE_ENTRY_EXIT, MODULE_ZONES])
    _upsert_camera(CAMERA_B, modules=[MODULE_ZONES])
    _seed_camera_geometry(CAMERA_A, with_counting_line=True)
    _seed_camera_geometry(CAMERA_B, with_counting_line=False)
    n_disabled = _disable_other_live_cameras({CAMERA_A, CAMERA_B})
    print(f"Disabled {n_disabled} other live camera(s)")

    print("Waiting up to 90s for events from backend-spawned worker subprocess...")
    deadline = time.time() + 90
    while time.time() < deadline:
        count_a = _event_count(CAMERA_A)
        count_b = _event_count(CAMERA_B)
        if count_a > 0 or count_b > 0:
            print(f"Events detected: {CAMERA_A}={count_a}, {CAMERA_B}={count_b}")
            break
        time.sleep(2)
    else:
        print("FAIL: no events within 90s")
        return 1

    login = requests.post(
        f"{API}/auth/login",
        json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASSWORD},
        timeout=10,
    )
    print(f"POST /auth/login -> {login.status_code}")
    if login.status_code != 200:
        print(login.text)
        return 1
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    before_disable = _event_count(CAMERA_A) + _event_count(CAMERA_B)
    t0 = time.time()
    toggle = requests.post(f"{API}/organizations/{ORG_ID}/toggle", headers=headers, timeout=10)
    print(f"POST /organizations/{ORG_ID}/toggle -> {toggle.status_code} {toggle.text}")
    if toggle.status_code != 200:
        return 1

    last_count = before_disable
    last_increase_at = t0
    while time.time() - t0 < 20:
        time.sleep(0.5)
        current = _event_count(CAMERA_A) + _event_count(CAMERA_B)
        if current > last_count:
            last_count = current
            last_increase_at = time.time()
        elif time.time() - last_increase_at >= 3:
            break

    stop_seconds = last_increase_at - t0
    print(
        f"Org-disable stop latency: {stop_seconds:.1f}s "
        f"(events before={before_disable}, after={last_count})"
    )

    requests.post(f"{API}/organizations/{ORG_ID}/toggle", headers=headers, timeout=10)

    print("PASS: backend path verification complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
