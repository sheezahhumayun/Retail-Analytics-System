"""Tests for live MJPEG stream mid-read failure handling."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from backend.app.services.camera_health import persist_camera_stream_error
from backend.app.services.camera_stream import async_iter_open_mjpeg_stream
from database.models import Camera
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope
from inference.video.base import CameraState

pytestmark = [pytest.mark.api, pytest.mark.database]


async def _collect_mjpeg_stream(source, first_chunk: bytes, **kwargs) -> list[bytes]:
    return [
        chunk
        async for chunk in async_iter_open_mjpeg_stream(
            source, first_chunk, **kwargs
        )
    ]


def _run_mjpeg_stream(source, first_chunk: bytes, **kwargs) -> list[bytes]:
    return asyncio.run(_collect_mjpeg_stream(source, first_chunk, **kwargs))


@pytest.fixture(scope="module")
def seeded_db():
    try:
        create_all()
        seed_reference_data(force=True)
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")
    yield
    reset_engine()


class TestMjpegStreamMidReadFailure:
    def test_stops_when_live_source_enters_error_state(self):
        source = MagicMock()
        source.is_live.return_value = True
        frame = np.zeros((90, 160, 3), dtype=np.uint8)
        source.read.side_effect = [(True, frame), (False, None)]
        source.get_state.return_value = CameraState.ERROR

        with patch(
            "backend.app.services.camera_health.persist_camera_stream_error",
            return_value=True,
        ) as persist:
            chunks = _run_mjpeg_stream(source, b"first", camera_id="entrance")

        assert chunks[0] == b"first"
        assert len(chunks) == 2
        source.release.assert_called_once()
        persist.assert_called_once_with("entrance")

    def test_does_not_persist_error_for_file_source_eof(self):
        source = MagicMock()
        source.is_live.return_value = False
        source.read.return_value = (False, None)

        with patch(
            "backend.app.services.camera_health.persist_camera_stream_error",
        ) as persist:
            chunks = _run_mjpeg_stream(source, b"first", camera_id="entrance")

        assert chunks == [b"first"]
        persist.assert_not_called()
        source.release.assert_called_once()


class TestPersistCameraStreamError:
    def test_writes_error_status(self, seeded_db):
        with session_scope() as session:
            camera = session.get(Camera, "entrance")
            assert camera is not None
            camera.status = "online"
            session.add(camera)

        assert persist_camera_stream_error("entrance") is True

        with session_scope() as session:
            camera = session.get(Camera, "entrance")
            assert camera is not None
            assert camera.status == "error"

    def test_skips_disabled_camera(self, seeded_db):
        with session_scope() as session:
            camera = Camera(
                id="stream_err_disabled",
                store_id=STORE_ID,
                name="Disabled",
                rtsp_url="rtsp://demo.local/disabled",
                status="disabled",
            )
            session.merge(camera)

        assert persist_camera_stream_error("stream_err_disabled") is False

        with session_scope() as session:
            camera = session.get(Camera, "stream_err_disabled")
            assert camera is not None
            assert camera.status == "disabled"
