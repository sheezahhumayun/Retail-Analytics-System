"""Camera connectivity probes and persisted status updates."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal

from sqlmodel import Session, select

from backend.app.services.alert_rules import get_camera_offline_duration_rule
from database.models import Alert, Camera

from ..schemas.extended.cameras import CameraTestResponse
from .camera_test import recorded_source_file_exists, test_camera_stream

logger = logging.getLogger(__name__)

CameraConnectivityStatus = Literal["online", "offline", "error"]

CAMERA_OFFLINE_DURATION_ALERT_TYPE = "CAMERA_OFFLINE_DURATION"

# Automatic health checks must not overwrite these manual/transient statuses.
_HEALTH_SKIP_STATUSES = frozenset({"disabled", "processing"})


def connectivity_status_from_test(result: CameraTestResponse) -> CameraConnectivityStatus:
    if result.status == "success":
        return "online"
    return "error"


def probe_camera(camera: Camera) -> CameraTestResponse:
    """Run a lightweight connectivity probe for one camera."""
    if camera.source_type == "recorded":
        return test_camera_stream(camera.rtsp_url)
    return test_camera_stream(camera.rtsp_url)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _set_camera_status(
    camera: Camera,
    new_status: str,
    *,
    now: datetime | None = None,
) -> bool:
    """Apply a status value; update ``status_changed_at`` only on actual transitions."""
    if camera.status == new_status:
        return False
    ts = now if now is not None else _utc_now()
    camera.status = new_status
    camera.status_changed_at = ts
    return True


def apply_probe_to_camera(
    camera: Camera,
    result: CameraTestResponse,
    *,
    now: datetime | None = None,
) -> CameraConnectivityStatus:
    """Update ``cameras.status`` from a probe result (skipped when disabled/processing)."""
    if camera.status in _HEALTH_SKIP_STATUSES:
        return camera.status  # type: ignore[return-value]

    new_status = connectivity_status_from_test(result)
    _set_camera_status(camera, new_status, now=now)
    return new_status  # type: ignore[return-value]


def apply_recorded_file_check_to_camera(
    camera: Camera,
    *,
    now: datetime | None = None,
) -> CameraConnectivityStatus:
    """Set recorded-camera status from on-disk source file existence."""
    if camera.status in _HEALTH_SKIP_STATUSES:
        return camera.status  # type: ignore[return-value]
    if camera.source_type != "recorded":
        return camera.status  # type: ignore[return-value]

    new_status: CameraConnectivityStatus = (
        "online" if recorded_source_file_exists(camera.rtsp_url) else "error"
    )
    _set_camera_status(camera, new_status, now=now)
    return new_status


def refresh_camera_status(session: Session, camera: Camera) -> CameraConnectivityStatus:
    """Probe a live camera and persist the resulting status.

    The probe itself (network I/O) can take a while, during which an admin
    may have manually disabled the camera via ``PUT /api/cameras/{id}``. To
    keep that manual change authoritative, re-read the row's current status
    right before writing the probe result and bail out if it changed to
    ``disabled`` while we were probing — the manual write wins and this
    probe's result is discarded rather than clobbering it.
    """
    if camera.status in _HEALTH_SKIP_STATUSES or camera.source_type != "live":
        return camera.status  # type: ignore[return-value]

    result = probe_camera(camera)

    session.refresh(camera)
    if camera.status in _HEALTH_SKIP_STATUSES:
        return camera.status  # type: ignore[return-value]

    status = apply_probe_to_camera(camera, result)
    session.add(camera)
    session.flush()
    return status


def refresh_recorded_camera_status(session: Session, camera: Camera) -> CameraConnectivityStatus:
    """Check recorded-camera source file existence and persist status."""
    if camera.status in _HEALTH_SKIP_STATUSES or camera.source_type != "recorded":
        return camera.status  # type: ignore[return-value]

    session.refresh(camera)
    if camera.status in _HEALTH_SKIP_STATUSES:
        return camera.status  # type: ignore[return-value]

    status = apply_recorded_file_check_to_camera(camera)
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
                Camera.status != "processing",
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


def refresh_all_recorded_camera_statuses(session: Session) -> int:
    """Check every non-skipped recorded camera's source file and persist status."""
    cameras = list(
        session.exec(
            select(Camera).where(
                Camera.source_type == "recorded",
                Camera.status != "disabled",
                Camera.status != "processing",
            )
        ).all()
    )
    updated = 0
    for camera in cameras:
        try:
            refresh_recorded_camera_status(session, camera)
            updated += 1
        except Exception:
            logger.exception("Recorded camera file check failed for %s", camera.id)
    return updated


def _normalize_utc(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def evaluate_camera_offline_duration_alerts(session: Session) -> int:
    """Create CAMERA_OFFLINE_DURATION alerts for live cameras down past threshold.

    Skips cameras that already have an open alert of this type. Does not touch
    the inference-pipeline ``CAMERA_OFFLINE`` event path.
    """
    now = _utc_now()
    created = 0

    cameras = list(
        session.exec(
            select(Camera).where(
                Camera.source_type == "live",
                Camera.status != "disabled",
                Camera.status != "online",
            )
        ).all()
    )

    for camera in cameras:
        rule = get_camera_offline_duration_rule(camera.id, camera.store_id, session=session)
        if rule is None:
            continue
        threshold, severity = rule

        if camera.status_changed_at is None:
            camera.status_changed_at = now
            session.add(camera)
            session.flush()
            continue

        changed_at = _normalize_utc(camera.status_changed_at)
        elapsed = (now - changed_at).total_seconds()
        if elapsed < threshold:
            continue

        existing = session.exec(
            select(Alert).where(
                Alert.alert_type == CAMERA_OFFLINE_DURATION_ALERT_TYPE,
                Alert.camera_id == camera.id,
                Alert.status == "open",
            )
        ).first()
        if existing is not None:
            continue

        session.add(
            Alert(
                alert_type=CAMERA_OFFLINE_DURATION_ALERT_TYPE,
                camera_id=camera.id,
                zone_id=None,
                timestamp=now,
                severity=severity,
                status="open",
                metadata_={
                    "threshold_seconds": threshold,
                    "offline_duration_seconds": elapsed,
                    "connectivity_status": camera.status,
                    "status_changed_at": changed_at.isoformat(),
                },
            )
        )
        created += 1

    return created


def persist_camera_stream_error(camera_id: str) -> bool:
    """Persist ``status=error`` when a live MJPEG preview stream dies mid-read.

    Uses the same ``apply_probe_to_camera`` path as Test Camera and the
    background health worker so admin tables and other tiles stay consistent.
    Opens its own DB session because the MJPEG generator runs outside the
    request-scoped session.
    """
    from database.session import session_scope

    error_result = CameraTestResponse(
        status="error",
        message="Stream lost during MJPEG preview",
    )
    with session_scope() as session:
        camera = session.get(Camera, camera_id)
        if camera is None:
            return False
        session.refresh(camera)
        if camera.status == "disabled" or camera.source_type != "live":
            return False
        apply_probe_to_camera(camera, error_result)
        session.add(camera)
    return True
