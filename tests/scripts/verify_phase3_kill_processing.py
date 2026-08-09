"""Phase 3 verification — kill in-flight processing when org is disabled."""

from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient
from sqlmodel import select

from backend.app.main import app
from backend.app.services.camera_process import ORG_DISABLE_CANCEL_MESSAGE, _processing_procs
from database.models import Camera, Organization, ProcessingRun, Store, User, Zone
from database.session import create_all, reset_engine, session_scope
from backend.app.services.passwords import hash_password

ORG_ID = "org_phase3_kill"
STORE_ID = "store_phase3_kill"
CAMERA_ID = "cam_phase3_kill"
USER_EMAIL = "phase3kill@test.local"
USER_PASSWORD = "phase3kill-pass"
SUPERADMIN_EMAIL = "superadmin@test.local"
SUPERADMIN_PASSWORD = "superadmin-test-pass"
VIDEO_PATH = "sample-data/store.mp4"


def _ensure_superadmin(session) -> None:
    from database.models import Superadmin

    if session.get(Superadmin, "superadmin_test") is None:
        session.add(
            Superadmin(
                id="superadmin_test",
                name="Test Superadmin",
                email=SUPERADMIN_EMAIL,
                password_hash=hash_password(SUPERADMIN_PASSWORD),
                status="active",
            )
        )


def _seed(session) -> None:
    _ensure_superadmin(session)
    session.merge(Organization(id=ORG_ID, name="Phase3 Kill Verify", status="active"))
    session.merge(Store(id=STORE_ID, org_id=ORG_ID, name="Kill Store", address="1 Test St"))
    session.merge(
        User(
            id="user_phase3_kill",
            org_id=ORG_ID,
            name="Phase3 User",
            email=USER_EMAIL,
            role="admin",
            password_hash=hash_password(USER_PASSWORD),
        )
    )
    session.merge(
        Camera(
            id=CAMERA_ID,
            store_id=STORE_ID,
            name="Kill Camera",
            location="Aisle",
            rtsp_url=VIDEO_PATH,
            source_type="recorded",
        )
    )
    session.merge(
        Zone(
            id="zone_phase3_kill",
            camera_id=CAMERA_ID,
            name="Test Zone",
            zone_type="general",
            polygon_coords=[[10, 10], [100, 10], [100, 100]],
        )
    )


def _print_run(label: str, run: ProcessingRun | None) -> None:
    if run is None:
        print(f"{label}: <no run>")
        return
    print(
        f"{label}: id={run.id} status={run.status!r} message={run.message!r} "
        f"finished_at={run.finished_at}"
    )


def main() -> int:
    create_all()
    with session_scope() as session:
        _seed(session)

    client = TestClient(app)
    try:
        sa_login = client.post(
            "/api/auth/login",
            json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASSWORD},
        )
        assert sa_login.status_code == 200, sa_login.text
        sa_headers = {"Authorization": f"Bearer {sa_login.json()['access_token']}"}

        user_login = client.post(
            "/api/auth/login",
            json={"email": USER_EMAIL, "password": USER_PASSWORD},
        )
        assert user_login.status_code == 200, user_login.text
        user_headers = {"Authorization": f"Bearer {user_login.json()['access_token']}"}

        process_resp = client.post(f"/api/cameras/{CAMERA_ID}/process", headers=user_headers)
        print("\n--- POST /process ---")
        print(f"status={process_resp.status_code} body={process_resp.json()}")
        assert process_resp.status_code == 200, process_resp.text

        with session_scope() as session:
            run = session.exec(
                select(ProcessingRun)
                .where(ProcessingRun.camera_id == CAMERA_ID)
                .order_by(ProcessingRun.started_at.desc())  # type: ignore[attr-defined]
            ).first()
            assert run is not None and run.status == "running"
            run_id = run.id

        pid: int | None = None
        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            proc = _processing_procs.get(CAMERA_ID)
            if proc is not None and proc.poll() is None:
                pid = proc.pid
                break
            time.sleep(0.2)
        print(f"\n--- subprocess PID while running ---")
        print(f"pid={pid} in_registry={CAMERA_ID in _processing_procs}")

        with session_scope() as session:
            run = session.get(ProcessingRun, run_id)
            session.refresh(run)
            _print_run("BEFORE toggle (DB)", run)
            assert run is not None and run.status == "running", run

        assert pid is not None, "processing subprocess never registered or already exited"

        disable = client.post(f"/api/organizations/{ORG_ID}/toggle", headers=sa_headers)
        print("\n--- POST toggle (disable) ---")
        print(f"status={disable.status_code} body={disable.json()}")
        assert disable.status_code == 200, disable.text

        time.sleep(1.0)
        with session_scope() as session:
            run = session.get(ProcessingRun, run_id)
            session.refresh(run)
            _print_run("AFTER toggle (DB)", run)
            assert run is not None
            assert run.status == "failed", run.status
            assert run.message == ORG_DISABLE_CANCEL_MESSAGE, run.message
            assert run.finished_at is not None

        import subprocess as sp

        if sys.platform == "win32":
            check = sp.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                check=False,
            )
            pid_gone = str(pid) not in check.stdout or "No tasks" in check.stdout
            print(f"\n--- tasklist /FI PID eq {pid} ---")
            print(check.stdout.strip())
        else:
            check = sp.run(["ps", "-p", str(pid)], capture_output=True, text=True, check=False)
            pid_gone = check.returncode != 0
            print(f"\n--- ps -p {pid} (exit {check.returncode}) ---")

        print(f"pid_gone={pid_gone}")
        assert pid_gone, f"process {pid} still running after org disable"

        enable = client.post(f"/api/organizations/{ORG_ID}/toggle", headers=sa_headers)
        print("\n--- POST toggle (re-enable) ---")
        print(f"status={enable.status_code} body={enable.json()}")
        assert enable.status_code == 200

        print("\nPhase 3 kill verification: PASS")
        return 0
    finally:
        client.close()
        reset_engine()


if __name__ == "__main__":
    raise SystemExit(main())
