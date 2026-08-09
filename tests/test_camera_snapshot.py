"""Tests for GET /api/cameras/{id}/snapshot reference-frame endpoint."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.camera_stream import STREAM_RTSP_RECONNECT_KWARGS
from database.models import Camera, ProcessingRun
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope

pytestmark = [pytest.mark.api, pytest.mark.database]

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def snapshot_api_client():
    try:
        create_all()
        seed_reference_data(force=True)
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")

    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        reset_engine()


@pytest.fixture(scope="module")
def snapshot_auth_headers(snapshot_api_client: TestClient) -> dict[str, str]:
    resp = snapshot_api_client.post(
        "/api/auth/login",
        json={"email": "admin@demo-retail.local", "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _create_recorded_camera(client: TestClient, headers: dict) -> str:
    resp = client.post(
        "/api/cameras",
        headers=headers,
        json={
            "store_id": STORE_ID,
            "name": f"Snapshot recorded {uuid.uuid4().hex[:8]}",
            "location": "Test aisle",
            "rtsp_url": "sample-data/checkout.mp4",
            "source_type": "recorded",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


class TestCameraSnapshotLive:
    def test_captures_one_jpeg_using_stream_profile_and_lock(self, snapshot_api_client, snapshot_auth_headers):
        camera_id = f"cam_live_snap_{uuid.uuid4().hex[:8]}"
        resp = snapshot_api_client.post(
            "/api/cameras",
            headers=snapshot_auth_headers,
            json={
                "store_id": STORE_ID,
                "name": "Live snapshot test",
                "location": "Door",
                "rtsp_url": "rtsp://demo.local/entrance",
                "source_type": "live",
            },
        )
        assert resp.status_code == 201, resp.text
        camera_id = resp.json()["id"]

        with patch(
            "backend.app.routers.cameras.capture_snapshot_jpeg",
            return_value=b"\xff\xd8\xff fake-jpeg",
        ) as capture:
            resp = snapshot_api_client.get(
                f"/api/cameras/{camera_id}/snapshot",
                headers=snapshot_auth_headers,
            )

        assert resp.status_code == 200, resp.text
        assert resp.headers["content-type"].startswith("image/jpeg")
        assert resp.content == b"\xff\xd8\xff fake-jpeg"
        capture.assert_called_once_with("rtsp://demo.local/entrance")

    def test_create_stream_source_uses_fast_fail_reconnect_for_rtsp(self):
        from unittest.mock import patch as mock_patch

        from backend.app.services.camera_stream import create_stream_source

        with mock_patch("backend.app.services.camera_stream.create_video_source") as cv_source:
            create_stream_source("rtsp://demo.local/entrance")
            _, kwargs = cv_source.call_args
            assert kwargs["reconnect_threshold"] == STREAM_RTSP_RECONNECT_KWARGS["reconnect_threshold"]
            assert kwargs["reconnect_attempts"] == STREAM_RTSP_RECONNECT_KWARGS["reconnect_attempts"]

    def test_capture_snapshot_jpeg_uses_opencv_io_lock(self):
        frame = np.zeros((90, 160, 3), dtype=np.uint8)
        mock_source = MagicMock()
        mock_source.read.return_value = (True, frame)

        with (
            patch(
                "backend.app.services.camera_stream.create_stream_source",
                return_value=mock_source,
            ),
            patch("backend.app.services.camera_stream.opencv_io") as mock_lock,
            patch(
                "backend.app.services.camera_stream._encode_jpeg_bytes",
                return_value=b"\xff\xd8\xff",
            ),
        ):
            mock_cm = MagicMock()
            mock_cm.__enter__ = MagicMock(return_value=None)
            mock_cm.__exit__ = MagicMock(return_value=False)
            mock_lock.return_value = mock_cm

            from backend.app.services.camera_stream import capture_snapshot_jpeg

            jpeg = capture_snapshot_jpeg("rtsp://demo.local/entrance")

        assert jpeg == b"\xff\xd8\xff"
        assert mock_lock.call_count >= 2
        mock_source.release.assert_called_once()


class TestCameraSnapshotRecorded:
    def test_returns_preview_when_completed_run_has_path(
        self,
        snapshot_api_client,
        snapshot_auth_headers,
        tmp_path,
    ):
        camera_id = _create_recorded_camera(snapshot_api_client, snapshot_auth_headers)
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        rel_path = f"data/frame-previews/{camera_id}/{run_id}.jpg"
        abs_path = REPO_ROOT / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_bytes(b"\xff\xd8\xff recorded-preview")

        now = datetime.now(timezone.utc)
        with session_scope() as session:
            session.add(
                ProcessingRun(
                    id=run_id,
                    camera_id=camera_id,
                    status="completed",
                    started_at=now,
                    finished_at=now,
                    message="ok",
                    source_path="sample-data/checkout.mp4",
                    preview_frame_path=rel_path,
                )
            )

        try:
            resp = snapshot_api_client.get(
                f"/api/cameras/{camera_id}/snapshot",
                headers=snapshot_auth_headers,
            )
            assert resp.status_code == 200, resp.text
            assert resp.headers["content-type"].startswith("image/jpeg")
            assert resp.content == b"\xff\xd8\xff recorded-preview"
        finally:
            if abs_path.is_file():
                abs_path.unlink()

    def test_404_when_no_completed_run(self, snapshot_api_client, snapshot_auth_headers):
        camera_id = _create_recorded_camera(snapshot_api_client, snapshot_auth_headers)
        resp = snapshot_api_client.get(
            f"/api/cameras/{camera_id}/snapshot",
            headers=snapshot_auth_headers,
        )
        assert resp.status_code == 404, resp.text
        body = resp.json()
        assert body["error"]["code"] == "preview_not_available"

    def test_404_when_completed_run_missing_preview_path(
        self,
        snapshot_api_client,
        snapshot_auth_headers,
    ):
        camera_id = _create_recorded_camera(snapshot_api_client, snapshot_auth_headers)
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        with session_scope() as session:
            session.add(
                ProcessingRun(
                    id=run_id,
                    camera_id=camera_id,
                    status="completed",
                    started_at=now,
                    finished_at=now,
                    message="legacy run",
                    source_path="sample-data/checkout.mp4",
                    preview_frame_path=None,
                )
            )

        resp = snapshot_api_client.get(
            f"/api/cameras/{camera_id}/snapshot",
            headers=snapshot_auth_headers,
        )
        assert resp.status_code == 404, resp.text
        assert resp.json()["error"]["code"] == "preview_not_available"

    def test_404_when_preview_file_missing_on_disk(
        self,
        snapshot_api_client,
        snapshot_auth_headers,
    ):
        camera_id = _create_recorded_camera(snapshot_api_client, snapshot_auth_headers)
        run_id = f"run_{uuid.uuid4().hex[:12]}"
        rel_path = f"data/frame-previews/{camera_id}/{run_id}.jpg"
        now = datetime.now(timezone.utc)
        with session_scope() as session:
            session.add(
                ProcessingRun(
                    id=run_id,
                    camera_id=camera_id,
                    status="completed",
                    started_at=now,
                    finished_at=now,
                    message="ok",
                    source_path="sample-data/checkout.mp4",
                    preview_frame_path=rel_path,
                )
            )

        resp = snapshot_api_client.get(
            f"/api/cameras/{camera_id}/snapshot",
            headers=snapshot_auth_headers,
        )
        assert resp.status_code == 404, resp.text
        assert resp.json()["error"]["code"] == "preview_not_available"
