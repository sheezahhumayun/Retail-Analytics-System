"""Verify process_recorded_camera excludes disabled zones from live analytics."""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from sqlmodel import select

from analytics.zones import ZoneDetector as RealZoneDetector
from database.models import Camera, Event, Zone, ZoneMetric, ZoneShape
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope
from inference.pipeline.process_recorded import process_recorded_camera
from inference.tracking import PositionRecord, TrackedObject

pytestmark = pytest.mark.database

_POLYGON = [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]]


@pytest.fixture(scope="module")
def db_ready():
    try:
        create_all()
        seed_reference_data(force=True)
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")
    yield
    reset_engine()


def _track_inside(camera_id: str, timestamp: float) -> TrackedObject:
    """Foot point at (50, 50) — inside the shared test polygon."""
    bbox = (40.0, 40.0, 60.0, 60.0)
    history = (
        PositionRecord(center=(50.0, 50.0), timestamp=timestamp - 1.0, bbox=bbox),
        PositionRecord(center=(50.0, 50.0), timestamp=timestamp, bbox=bbox),
    )
    return TrackedObject(
        track_id=1,
        bbox=bbox,
        class_id=0,
        class_name="person",
        confidence=0.9,
        camera_id=camera_id,
        timestamp=timestamp,
        position_history=history,
    )


@contextmanager
def _mock_video_pipeline(camera_id: str):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frames = [(frame, 1000.0 + i) for i in range(6)]

    mock_detector = MagicMock()
    mock_detector.detect.return_value = []
    mock_detector_cm = MagicMock()
    mock_detector_cm.__enter__.return_value = mock_detector
    mock_detector_cm.__exit__.return_value = False

    mock_source = MagicMock()

    frame_idx = {"n": 0}

    def _update(_dets):
        frame_idx["n"] += 1
        n = frame_idx["n"]
        bbox = (40.0, 40.0, 60.0, 60.0)
        history = tuple(
            PositionRecord(center=(50.0, 50.0), timestamp=999.0 + i, bbox=bbox)
            for i in range(1, n + 1)
        )
        if n < 2:
            return []
        return [
            TrackedObject(
                track_id=1,
                bbox=bbox,
                class_id=0,
                class_name="person",
                confidence=0.9,
                camera_id=camera_id,
                timestamp=999.0 + n,
                position_history=history,
            )
        ]

    mock_tracker = MagicMock()
    mock_tracker.update.side_effect = _update

    with (
        patch(
            "inference.pipeline.process_recorded.create_detector",
            return_value=mock_detector_cm,
        ),
        patch(
            "inference.pipeline.process_recorded.warmup_source",
            return_value=mock_source,
        ),
        patch(
            "inference.pipeline.process_recorded.iter_frames",
            return_value=iter(frames),
        ),
        patch(
            "inference.pipeline.process_recorded.Tracker",
            return_value=mock_tracker,
        ),
        patch(
            "inference.pipeline.process_recorded.ZoneDetector",
            side_effect=lambda zones: RealZoneDetector(zones, hysteresis_frames=1),
        ),
    ):
        yield


class TestProcessRecordedSoftDelete:
    def test_disabled_zone_produces_no_analytics_rows(self, db_ready):
        """Path (b): process_recorded_camera zone load at lines 100-109 drives analytics."""
        camera_id = f"cam_recorded_{uuid.uuid4().hex[:8]}"
        active_zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        disabled_zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        with session_scope() as session:
            session.add(
                Camera(
                    id=camera_id,
                    store_id=STORE_ID,
                    name="Process recorded soft-delete test",
                    rtsp_url="sample-data/checkout.mp4",
                    source_type="recorded",
                    analytics_modules=["zones", "dwell"],
                )
            )
            for zone_id, name, status in (
                (active_zone_id, "Active Zone", "offline"),
                (disabled_zone_id, "Disabled Zone", "disabled"),
            ):
                session.add(
                    ZoneShape(
                        id=zone_id,
                        camera_id=camera_id,
                        name=name,
                        shape_type="general",
                        polygon_points=_POLYGON,
                        created_at=now,
                        status=status,
                    )
                )
                session.add(
                    Zone(
                        id=zone_id,
                        camera_id=camera_id,
                        name=name,
                        polygon_coords=_POLYGON,
                        zone_type="general",
                        analytics_enabled=True,
                        status=status,
                    )
                )

        with _mock_video_pipeline(camera_id):
            result = process_recorded_camera(camera_id, backend="ultralytics", target_fps=10.0)

        assert result["status"] == "completed"
        assert result["frames_processed"] == 6

        with session_scope() as session:
            active_events = session.exec(
                select(Event).where(Event.zone_id == active_zone_id)
            ).all()
            disabled_events = session.exec(
                select(Event).where(Event.zone_id == disabled_zone_id)
            ).all()
            active_metrics = session.exec(
                select(ZoneMetric).where(ZoneMetric.zone_id == active_zone_id)
            ).all()
            disabled_metrics = session.exec(
                select(ZoneMetric).where(ZoneMetric.zone_id == disabled_zone_id)
            ).all()

        assert len(active_events) > 0 or len(active_metrics) > 0, (
            "Active zone should produce analytics rows"
        )
        assert disabled_events == []
        assert disabled_metrics == []


class TestProcessRecordedPreviewFrame:
    def test_writes_preview_without_heatmap_module(self, db_ready):
        """Preview frame is saved when run_id is set, even without MODULE_HEATMAP."""
        from pathlib import Path

        camera_id = f"cam_preview_{uuid.uuid4().hex[:8]}"
        run_id = f"run_{uuid.uuid4().hex[:8]}"
        repo_root = Path(__file__).resolve().parents[1]
        rel_path = f"data/frame-previews/{camera_id}/{run_id}.jpg"
        abs_path = repo_root / rel_path
        now = datetime.now(timezone.utc)

        with session_scope() as session:
            session.add(
                Camera(
                    id=camera_id,
                    store_id=STORE_ID,
                    name="Preview frame test",
                    rtsp_url="sample-data/checkout.mp4",
                    source_type="recorded",
                    analytics_modules=["zones", "dwell"],
                )
            )
            zone_id = f"zone_{uuid.uuid4().hex[:8]}"
            session.add(
                ZoneShape(
                    id=zone_id,
                    camera_id=camera_id,
                    name="Zone",
                    shape_type="general",
                    polygon_points=_POLYGON,
                    created_at=now,
                )
            )
            session.add(
                Zone(
                    id=zone_id,
                    camera_id=camera_id,
                    name="Zone",
                    polygon_coords=_POLYGON,
                    zone_type="general",
                    analytics_enabled=True,
                )
            )

        try:
            with _mock_video_pipeline(camera_id):
                result = process_recorded_camera(
                    camera_id,
                    run_id=run_id,
                    backend="ultralytics",
                    target_fps=10.0,
                )

            assert result["status"] == "completed"
            assert result["preview_frame_path"] == rel_path
            assert abs_path.is_file()
            assert abs_path.stat().st_size > 0
        finally:
            if abs_path.is_file():
                abs_path.unlink()
            if abs_path.parent.is_dir():
                abs_path.parent.rmdir()
