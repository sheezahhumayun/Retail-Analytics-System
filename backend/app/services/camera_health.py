"""Camera connectivity probes and persisted status updates."""

from __future__ import annotations

import logging
from typing import Literal

from sqlmodel import Session, select

from database.models import Camera

from ..schemas.extended.cameras import CameraTestResponse
from .camera_test import test_camera_stream

logger = logging.getLogger(__name__)

CameraConnectivityStatus = Literal["online", "offline", "error"]


def connectivity_status_from_test(result: CameraTestResponse) -> CameraConnectivityStatus:
    if result.status == "success":
        return "online"
    return "error"


def probe_camera(camera: Camera) -> CameraTestResponse:
    """Run a lightweight connectivity probe for one camera."""
    if camera.source_type == "recorded":
        return test_camera_stream(camera.rtsp_url)
    return test_camera_stream(camera.rtsp_url)


def apply_probe_to_camera(camera: Camera, result: CameraTestResponse) -> CameraConnectivityStatus:
    """Update ``cameras.status`` from a probe result (skipped when disabled)."""
    if camera.status == "disabled":
        return camera.status  # type: ignore[return-value]
    if camera.source_type == "recorded":
        return camera.status  # type: ignore[return-value]

    new_status = connectivity_status_from_test(result)
    camera.status = new_status
    return new_status


def refresh_camera_status(session: Session, camera: Camera) -> CameraConnectivityStatus:
    """Probe a live camera and persist the resulting status."""
    if camera.status == "disabled" or camera.source_type == "recorded":
        return camera.status  # type: ignore[return-value]

    result = probe_camera(camera)
    status = apply_probe_to_camera(camera, result)
    session.add(camera)
    session.flush()
    return status


def refresh_all_live_camera_statuses(session: Session) -> int:
    """Probe every non-disabled live camera and persist status. Returns update count."""
    cameras = list(
        session.exec(
            select(Camera).where(
                Camera.source_type == "live",
                Camera.status != "disabled",
            )
        ).all()
    )
    updated = 0
    for camera in cameras:
        try:
            refresh_camera_status(session, camera)
            updated += 1
        except Exception:
            logger.exception("Camera health probe failed for %s", camera.id)
    return updated
