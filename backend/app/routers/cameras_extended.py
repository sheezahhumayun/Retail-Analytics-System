"""Camera admin extensions (Module 12.5)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from database.models import Camera

from ..auth import TokenPayload, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.cameras import CameraProcessResponse, CameraResponse
from ..schemas.extended.cameras import CameraTestResponse, CameraUpdate
from ..services.camera_health import (
    apply_probe_to_camera,
    apply_recorded_file_check_to_camera,
    probe_camera,
)
from ..services.camera_process import (
    ProcessJobState,
    ProcessingRunActiveError,
    get_process_job,
    start_recorded_processing,
)
from ..services.org_scope import require_camera_in_org, require_store_in_org
from .cameras import _camera_response

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.put(
    "/{camera_id}",
    response_model=CameraResponse,
    summary="Update camera",
    description=(
        "Update camera configuration. Admin only. Same fields as POST /api/cameras, "
        "plus `status` (`offline` | `disabled`) as the manual enable/disable switch."
    ),
)
def update_camera(
    camera_id: str,
    body: CameraUpdate,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CameraResponse:
    camera = require_camera_in_org(session, camera_id, admin.org_id)

    if body.store_id is not None:
        require_store_in_org(session, body.store_id, admin.org_id)
        camera.store_id = body.store_id
    if body.name is not None:
        camera.name = body.name
    if body.location is not None:
        camera.location = body.location
    if body.rtsp_url is not None:
        camera.rtsp_url = body.rtsp_url
    if body.source_type is not None:
        camera.source_type = body.source_type
    if body.camera_type is not None:
        camera.camera_type = body.camera_type
    if body.resolution is not None:
        camera.resolution = body.resolution
    if body.fps is not None:
        camera.fps = body.fps
    if body.analytics_modules is not None:
        camera.analytics_modules = body.analytics_modules
    if body.status is not None:
        # Manual admin enable/disable is authoritative: it wins over whatever a
        # concurrently in-flight health probe was about to write, because this
        # write lands within its own transaction and probes re-check the live
        # DB value (see camera_health.refresh_camera_status) before persisting
        # their own result.
        camera.status = body.status

    session.add(camera)
    session.flush()
    session.refresh(camera)
    return _camera_response(camera)


@router.delete(
    "/{camera_id}",
    response_model=CameraResponse,
    summary="Disable camera (soft delete)",
    description="Mark camera status as `disabled` without removing historical data. Admin only.",
)
def disable_camera(
    camera_id: str,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CameraResponse:
    camera = require_camera_in_org(session, camera_id, admin.org_id)
    camera.status = "disabled"
    session.add(camera)
    session.flush()
    session.refresh(camera)
    return _camera_response(camera)


@router.post(
    "/{camera_id}/test",
    response_model=CameraTestResponse,
    summary="Test camera stream",
    description=(
        "Attempt to reach the camera stream URL (TCP handshake for RTSP/HTTP, "
        "file check for local sample paths). Optional OpenCV probe when installed. Admin only."
    ),
)
def test_camera(
    camera_id: str,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CameraTestResponse:
    camera = require_camera_in_org(session, camera_id, admin.org_id)

    result = probe_camera(camera)
    camera_status = None
    session.refresh(camera)
    if camera.status not in ("disabled", "processing"):
        if camera.source_type == "live":
            camera_status = apply_probe_to_camera(camera, result)
        elif camera.source_type == "recorded":
            camera_status = apply_recorded_file_check_to_camera(camera)
            # Keep probe metrics from ``result``; status comes from file existence.
        session.add(camera)
        session.flush()

    return CameraTestResponse(
        status=result.status,
        latency_ms=result.latency_ms,
        resolution=result.resolution,
        fps=result.fps,
        message=result.message,
        camera_status=camera_status,
    )


def _process_response(session: DbSession, camera_id: str) -> CameraProcessResponse:
    job = get_process_job(session, camera_id)
    status_map = {
        ProcessJobState.IDLE: "idle",
        ProcessJobState.RUNNING: "running",
        ProcessJobState.COMPLETED: "completed",
        ProcessJobState.FAILED: "failed",
    }
    return CameraProcessResponse(
        camera_id=camera_id,
        status=status_map[job.state],  # type: ignore[arg-type]
        message=job.message,
        started_at=job.started_at.isoformat() if job.started_at else None,
        finished_at=job.finished_at.isoformat() if job.finished_at else None,
    )


@router.post(
    "/{camera_id}/process",
    response_model=CameraProcessResponse,
    summary="Process recorded video",
    description=(
        "Run inference→analytics→persistence on a recorded camera's video file. "
        "Admin only. Applies only to `source_type=recorded` cameras. "
        "Runs in a background thread (sample videos take 30–60+ seconds)."
    ),
)
def process_recorded_video(
    camera_id: str,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CameraProcessResponse:
    camera = require_camera_in_org(session, camera_id, admin.org_id)
    if camera.source_type != "recorded":
        raise ApiError(
            400,
            "invalid_camera_source",
            "Processing is only available for recorded-video cameras",
        )
    if not camera.rtsp_url:
        raise ApiError(400, "missing_video_path", "No video file path configured for this camera")

    try:
        start_recorded_processing(camera_id)
    except ProcessingRunActiveError as exc:
        raise ApiError(
            409,
            "processing_run_active",
            "A processing run is already active for this camera",
        ) from exc
    return _process_response(session, camera_id)


@router.get(
    "/{camera_id}/process-status",
    response_model=CameraProcessResponse,
    summary="Recorded video processing status",
    description="Poll processing job status for a recorded camera. Admin only.",
)
def recorded_process_status(
    camera_id: str,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CameraProcessResponse:
    camera = require_camera_in_org(session, camera_id, admin.org_id)
    if camera.source_type != "recorded":
        raise ApiError(
            400,
            "invalid_camera_source",
            "Processing status is only available for recorded-video cameras",
        )
    return _process_response(session, camera_id)
