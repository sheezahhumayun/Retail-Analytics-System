"""Tests for recorded-camera file-existence health checks."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlmodel import select

from backend.app.services.camera_health import (
    apply_recorded_file_check_to_camera,
    refresh_all_recorded_camera_statuses,
    refresh_recorded_camera_status,
)
from database.models import Camera
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope

pytestmark = [pytest.mark.database]

VALID_PATH = "sample-data/checkout.mp4"
MISSING_PATH = "sample-data/does-not-exist.mp4"


@pytest.fixture(scope="module")
def seeded_db():
    try:
        create_all()
        seed_reference_data(force=True)
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")
    yield
    reset_engine()


def _upsert_recorded_camera(
    camera_id: str,
    *,
    rtsp_url: str,
    status: str = "offline",
) -> None:
    with session_scope() as session:
        session.merge(
            Camera(
                id=camera_id,
                store_id=STORE_ID,
                name=f"Recorded health {camera_id}",
                rtsp_url=rtsp_url,
                source_type="recorded",
                status=status,
                status_changed_at=datetime.now(timezone.utc),
            )
        )


def _get_status(camera_id: str) -> str:
    with session_scope() as session:
        camera = session.get(Camera, camera_id)
        assert camera is not None
        return camera.status


class TestRecordedCameraHealth:
    def test_existing_file_sets_online(self, seeded_db):
        camera_id = f"cam_rec_health_{uuid.uuid4().hex[:8]}"
        _upsert_recorded_camera(camera_id, rtsp_url=VALID_PATH, status="offline")

        with session_scope() as session:
            camera = session.get(Camera, camera_id)
            assert camera is not None
            apply_recorded_file_check_to_camera(camera)
            session.add(camera)

        assert _get_status(camera_id) == "online"

    def test_missing_file_sets_error(self, seeded_db):
        camera_id = f"cam_rec_health_{uuid.uuid4().hex[:8]}"
        _upsert_recorded_camera(camera_id, rtsp_url=MISSING_PATH, status="online")

        with session_scope() as session:
            camera = session.get(Camera, camera_id)
            assert camera is not None
            apply_recorded_file_check_to_camera(camera)
            session.add(camera)

        assert _get_status(camera_id) == "error"

    def test_disabled_camera_is_not_overwritten(self, seeded_db):
        camera_id = f"cam_rec_health_{uuid.uuid4().hex[:8]}"
        _upsert_recorded_camera(camera_id, rtsp_url=MISSING_PATH, status="disabled")

        with session_scope() as session:
            camera = session.get(Camera, camera_id)
            assert camera is not None
            before = camera.status_changed_at
            apply_recorded_file_check_to_camera(camera)
            session.add(camera)

        assert _get_status(camera_id) == "disabled"
        with session_scope() as session:
            camera = session.get(Camera, camera_id)
            assert camera is not None
            assert camera.status_changed_at == before

    def test_processing_camera_is_not_overwritten(self, seeded_db):
        camera_id = f"cam_rec_health_{uuid.uuid4().hex[:8]}"
        _upsert_recorded_camera(camera_id, rtsp_url=MISSING_PATH, status="processing")

        with session_scope() as session:
            camera = session.get(Camera, camera_id)
            assert camera is not None
            apply_recorded_file_check_to_camera(camera)
            session.add(camera)

        assert _get_status(camera_id) == "processing"

    def test_worker_refresh_updates_recorded_cameras(self, seeded_db):
        camera_id = f"cam_rec_health_{uuid.uuid4().hex[:8]}"
        _upsert_recorded_camera(camera_id, rtsp_url=VALID_PATH, status="offline")

        with session_scope() as session:
            count = refresh_all_recorded_camera_statuses(session)
            assert count >= 1

        assert _get_status(camera_id) == "online"

    def test_refresh_recorded_skips_disabled_in_query(self, seeded_db):
        camera_id = f"cam_rec_health_{uuid.uuid4().hex[:8]}"
        _upsert_recorded_camera(camera_id, rtsp_url=MISSING_PATH, status="disabled")

        with session_scope() as session:
            refresh_recorded_camera_status(session, session.get(Camera, camera_id))

        assert _get_status(camera_id) == "disabled"
