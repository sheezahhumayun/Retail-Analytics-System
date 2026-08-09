"""Tests for processing run persistence, TOCTOU guard, and video playback."""

from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select
from sqlalchemy import text

from backend.app.main import app
from database.models import ProcessingRun, Zone
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope

pytestmark = [pytest.mark.api, pytest.mark.api_extended, pytest.mark.database]


@pytest.fixture(scope="module")
def processing_api_client():
    try:
        create_all()
        seed_reference_data(force=True)
        with session_scope() as session:
            session.exec(
                text(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_processing_runs_one_running_per_camera
                    ON processing_runs (camera_id)
                    WHERE status = 'running'
                    """
                )
            )
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")

    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        reset_engine()


@pytest.fixture(scope="module")
def processing_admin_headers(processing_api_client: TestClient) -> dict[str, str]:
    resp = processing_api_client.post(
        "/api/auth/login",
        json={"email": "admin@demo-retail.local", "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _create_recorded_camera(processing_api_client: TestClient, processing_admin_headers: dict) -> str:
    resp = processing_api_client.post(
        "/api/cameras",
        headers=processing_admin_headers,
        json={
            "store_id": STORE_ID,
            "name": f"Recorded {uuid.uuid4().hex[:8]}",
            "location": "Test aisle",
            "rtsp_url": "sample-data/checkout.mp4",
            "source_type": "recorded",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_zone(processing_api_client: TestClient, processing_admin_headers: dict, camera_id: str) -> str:
    zone_id = f"zone_{uuid.uuid4().hex[:8]}"
    resp = processing_api_client.post(
        "/api/zones",
        headers=processing_admin_headers,
        json={
            "id": zone_id,
            "camera_id": camera_id,
            "name": "Snapshot Zone",
            "type": "general",
            "polygon_points": [[10, 10], [100, 10], [100, 100]],
        },
    )
    assert resp.status_code == 201, resp.text
    return zone_id


def _wait_for_latest_run(camera_id: str, *, timeout_sec: float = 5.0) -> ProcessingRun:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        with session_scope() as session:
            run = session.exec(
                select(ProcessingRun)
                .where(ProcessingRun.camera_id == camera_id)
                .order_by(ProcessingRun.started_at.desc())  # type: ignore[attr-defined]
            ).first()
            if run is not None and run.status in {"completed", "failed"}:
                session.refresh(run)
                session.expunge(run)
                return run
        time.sleep(0.05)
    raise AssertionError(f"Timed out waiting for processing run on camera {camera_id}")


def _subprocess_success(*_args, **_kwargs):
    return type(
        "Completed",
        (),
        {"returncode": 0, "stdout": "ok", "stderr": ""},
    )()


class TestProcessingRuns:
    @patch("backend.app.services.camera_process.subprocess.run", side_effect=_subprocess_success)
    def test_snapshots_match_zones_at_run_start(
        self,
        _mock_run,
        processing_api_client: TestClient,
        processing_admin_headers: dict,
    ):
        camera_id = _create_recorded_camera(processing_api_client, processing_admin_headers)
        zone_id = _create_zone(processing_api_client, processing_admin_headers, camera_id)

        with session_scope() as session:
            zone = session.get(Zone, zone_id)
            assert zone is not None
            expected_polygon = zone.polygon_coords
            expected_name = zone.name
            expected_type = zone.zone_type

        resp = processing_api_client.post(f"/api/cameras/{camera_id}/process", headers=processing_admin_headers)
        assert resp.status_code == 200, resp.text

        run = _wait_for_latest_run(camera_id)
        assert run.status == "completed"
        snap = next(item for item in run.zones_snapshot if item["id"] == zone_id)
        assert snap["polygon_coords"] == expected_polygon
        assert snap["name"] == expected_name
        assert snap["zone_type"] == expected_type

    @patch("backend.app.services.camera_process.subprocess.run", side_effect=_subprocess_success)
    def test_deleted_zone_does_not_change_run_snapshot(
        self,
        _mock_run,
        processing_api_client: TestClient,
        processing_admin_headers: dict,
    ):
        camera_id = _create_recorded_camera(processing_api_client, processing_admin_headers)
        zone_id = _create_zone(processing_api_client, processing_admin_headers, camera_id)

        process_resp = processing_api_client.post(f"/api/cameras/{camera_id}/process", headers=processing_admin_headers)
        assert process_resp.status_code == 200, process_resp.text

        run = _wait_for_latest_run(camera_id)
        run_id = run.id
        snapshot_before = list(run.zones_snapshot)

        delete_resp = processing_api_client.delete(f"/api/zones/{zone_id}", headers=processing_admin_headers)
        assert delete_resp.status_code == 204

        detail_resp = processing_api_client.get(
            f"/api/cameras/{camera_id}/processing-runs/{run_id}",
            headers=processing_admin_headers,
        )
        assert detail_resp.status_code == 200, detail_resp.text
        assert detail_resp.json()["zones_snapshot"] == snapshot_before

        with session_scope() as session:
            zone = session.get(Zone, zone_id)
            assert zone is not None
            assert zone.status == "disabled"

    def test_concurrent_process_returns_409_and_spawns_one_subprocess(
        self,
        processing_api_client: TestClient,
        processing_admin_headers: dict,
    ):
        camera_id = _create_recorded_camera(processing_api_client, processing_admin_headers)
        release = threading.Event()
        spawn_count = {"value": 0}
        lock = threading.Lock()

        def counting_run(*_args, **_kwargs):
            with lock:
                spawn_count["value"] += 1
            if not release.wait(timeout=5):
                raise TimeoutError("subprocess mock timed out waiting for release")
            return _subprocess_success()

        results: list[int] = []

        def post_process():
            resp = processing_api_client.post(f"/api/cameras/{camera_id}/process", headers=processing_admin_headers)
            results.append(resp.status_code)

        with patch("backend.app.services.camera_process.subprocess.run", side_effect=counting_run):
            t1 = threading.Thread(target=post_process)
            t2 = threading.Thread(target=post_process)
            t1.start()
            t2.start()
            t1.join(timeout=10)
            t2.join(timeout=10)

        assert sorted(results) == [200, 409]
        assert spawn_count["value"] == 1

        with session_scope() as session:
            running = session.exec(
                select(ProcessingRun).where(
                    ProcessingRun.camera_id == camera_id,
                    ProcessingRun.status == "running",
                )
            ).all()
            assert len(running) <= 1

        release.set()
        _wait_for_latest_run(camera_id)

    def test_reconcile_orphaned_processing_runs_marks_stale_running_as_failed(
        self,
        processing_api_client: TestClient,
        processing_admin_headers: dict,
    ):
        from backend.app.services.camera_process import (
            RESTART_INTERRUPT_MESSAGE,
            reconcile_orphaned_processing_runs,
        )

        camera_id = _create_recorded_camera(processing_api_client, processing_admin_headers)
        stale_id = f"run_{uuid.uuid4().hex[:12]}"
        started_at = datetime.now(timezone.utc)
        with session_scope() as session:
            session.add(
                ProcessingRun(
                    id=stale_id,
                    camera_id=camera_id,
                    status="running",
                    started_at=started_at,
                    finished_at=None,
                    message="Processing video…",
                    source_path="sample-data/checkout.mp4",
                    zones_snapshot=[],
                    lines_snapshot=[],
                )
            )

        reconciled = reconcile_orphaned_processing_runs()
        assert reconciled >= 1

        with session_scope() as session:
            run = session.get(ProcessingRun, stale_id)
            assert run is not None
            assert run.status == "failed"
            assert run.finished_at is not None
            assert run.message == RESTART_INTERRUPT_MESSAGE

        process_resp = processing_api_client.post(
            f"/api/cameras/{camera_id}/process",
            headers=processing_admin_headers,
        )
        assert process_resp.status_code == 200, process_resp.text

    @patch("backend.app.services.camera_process.subprocess.run", side_effect=_subprocess_success)
    def test_video_range_request_returns_206(
        self,
        _mock_run,
        processing_api_client: TestClient,
        processing_admin_headers: dict,
    ):
        camera_id = _create_recorded_camera(processing_api_client, processing_admin_headers)
        process_resp = processing_api_client.post(f"/api/cameras/{camera_id}/process", headers=processing_admin_headers)
        assert process_resp.status_code == 200, process_resp.text

        run = _wait_for_latest_run(camera_id)
        run_id = run.id

        video_resp = processing_api_client.get(
            f"/api/cameras/{camera_id}/processing-runs/{run_id}/video",
            headers={**processing_admin_headers, "Range": "bytes=0-1023"},
        )
        assert video_resp.status_code == 206, video_resp.text
        assert video_resp.headers.get("content-range", "").startswith("bytes 0-1023/")
        assert len(video_resp.content) == 1024

    def test_missing_source_video_returns_specific_404(
        self,
        processing_api_client: TestClient,
        processing_admin_headers: dict,
    ):
        camera_id = _create_recorded_camera(processing_api_client, processing_admin_headers)
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        with session_scope() as session:
            session.add(
                ProcessingRun(
                    id=run_id,
                    camera_id=camera_id,
                    status="completed",
                    started_at=datetime.now(timezone.utc),
                    finished_at=datetime.now(timezone.utc),
                    message="done",
                    source_path="sample-data/does-not-exist.mp4",
                    zones_snapshot=[],
                    lines_snapshot=[],
                )
            )

        resp = processing_api_client.get(
            f"/api/cameras/{camera_id}/processing-runs/{run_id}/video",
            headers=processing_admin_headers,
        )
        assert resp.status_code == 404, resp.text
        assert resp.json()["error"]["code"] == "source_video_unavailable"
        assert "no longer available" in resp.json()["error"]["message"].lower()

    @patch("backend.app.services.camera_process.subprocess.run", side_effect=_subprocess_success)
    def test_list_and_detail_endpoints(
        self,
        _mock_run,
        processing_api_client: TestClient,
        processing_admin_headers: dict,
    ):
        camera_id = _create_recorded_camera(processing_api_client, processing_admin_headers)
        _create_zone(processing_api_client, processing_admin_headers, camera_id)

        process_resp = processing_api_client.post(f"/api/cameras/{camera_id}/process", headers=processing_admin_headers)
        assert process_resp.status_code == 200, process_resp.text

        _wait_for_latest_run(camera_id)

        list_resp = processing_api_client.get(
            f"/api/cameras/{camera_id}/processing-runs",
            headers=processing_admin_headers,
        )
        assert list_resp.status_code == 200, list_resp.text
        runs = list_resp.json()
        assert len(runs) >= 1
        assert runs[0]["status"] == "completed"

        detail_resp = processing_api_client.get(
            f"/api/cameras/{camera_id}/processing-runs/{runs[0]['id']}",
            headers=processing_admin_headers,
        )
        assert detail_resp.status_code == 200, detail_resp.text
        assert detail_resp.json()["zones_snapshot"]
