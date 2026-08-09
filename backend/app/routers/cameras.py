"""Camera CRUD and status endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse, Response, StreamingResponse
from sqlmodel import select

from database.models import Camera, Event, OccupancyMetric

from ..auth import TokenPayload, get_current_user, get_current_user_from_token, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..services.org_scope import (
    cameras_for_org_stmt,
    require_camera_in_org,
    require_store_in_org,
)
from ..services.camera_process import get_latest_completed_processing_run
from ..services.camera_stream import (
    MJPEG_CONTENT_TYPE,
    StreamOpenError,
    async_iter_open_mjpeg_stream,
    capture_snapshot_jpeg,
    open_stream_source,
)
from ..services.local_media_path import resolve_repo_data_path
from ..schemas.cameras import (
    CameraCreate,
    CameraResponse,
    CameraStatusResponse,
)
from ..services.camera_health import (
    refresh_camera_status,
    refresh_recorded_camera_status,
)
from ..services.camera_ids import generate_camera_id

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get(
    "",
    response_model=list[CameraResponse],
    summary="List cameras",
    description="Return cameras, optionally filtered by store.",
)
def list_cameras(
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str | None, Query(description="Filter by store id")] = None,
    include_disabled: Annotated[
        bool,
        Query(
            description=(
                "Include soft-deleted/disabled cameras in the response. "
                "Defaults to False so disabled cameras don't reappear in normal "
                "camera pickers/lists after being disabled or deleted."
            )
        ),
    ] = False,
) -> list[CameraResponse]:
    if store_id is not None:
        require_store_in_org(session, store_id, user.org_id)
    stmt = cameras_for_org_stmt(user.org_id, store_id=store_id)
    if not include_disabled:
        stmt = stmt.where(Camera.status != "disabled")
    cameras = list(session.exec(stmt).all())
    return [_camera_response(camera) for camera in cameras]


@router.post(
    "",
    response_model=CameraResponse,
    status_code=201,
    summary="Create camera",
    description=(
        "Register a new camera for a store. The server assigns a unique `id` "
        "(e.g. `cam_entrance_a1b2c3`); do not send `id` in the request body. Admin only."
    ),
)
def create_camera(
    body: CameraCreate,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CameraResponse:
    require_store_in_org(session, body.store_id, admin.org_id)
    camera_id = generate_camera_id(session, body.name)
    camera = Camera(id=camera_id, **body.model_dump(), status="offline")
    session.add(camera)
    session.flush()
    session.refresh(camera)
    return _camera_response(camera)


def _camera_response(camera: Camera) -> CameraResponse:
    return CameraResponse(
        id=camera.id,
        store_id=camera.store_id,
        name=camera.name,
        location=camera.location,
        rtsp_url=camera.rtsp_url,
        source_type=camera.source_type,  # type: ignore[arg-type]
        last_processed_at=(
            camera.last_processed_at.isoformat() if camera.last_processed_at else None
        ),
        camera_type=camera.camera_type,
        resolution=camera.resolution,
        fps=camera.fps,
        status=camera.status,
        analytics_modules=camera.analytics_modules or [],
    )


@router.get(
    "/{camera_id}/status",
    response_model=CameraStatusResponse,
    summary="Camera health and occupancy",
    description="Return camera online status, last seen event timestamp, and current occupancy.",
)
def camera_status(
    camera_id: str,
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> CameraStatusResponse:
    camera = require_camera_in_org(session, camera_id, user.org_id)

    if camera.status not in ("disabled", "processing"):
        if camera.source_type == "live":
            refresh_camera_status(session, camera)
        elif camera.source_type == "recorded":
            refresh_recorded_camera_status(session, camera)

    last_event = session.exec(
        select(Event)
        .where(Event.camera_id == camera_id)
        .order_by(Event.timestamp.desc())  # type: ignore[attr-defined]
    ).first()

    occ_row = session.exec(
        select(OccupancyMetric)
        .where(OccupancyMetric.camera_id == camera_id)
        .order_by(OccupancyMetric.timestamp.desc())  # type: ignore[attr-defined]
    ).first()

    return CameraStatusResponse(
        id=camera.id,
        name=camera.name,
        store_id=camera.store_id,
        source_type=camera.source_type,  # type: ignore[arg-type]
        status=camera.status,
        last_seen=last_event.timestamp.isoformat() if last_event else None,
        current_occupancy=occ_row.current_occupancy if occ_row else None,
        processed=(
            camera.last_processed_at is not None if camera.source_type == "recorded" else None
        ),
        last_processed_at=(
            camera.last_processed_at.isoformat()
            if camera.source_type == "recorded" and camera.last_processed_at
            else None
        ),
    )


@router.get(
    "/{camera_id}/stream",
    summary="Live camera MJPEG stream",
    description=(
        "Multipart MJPEG preview for ``source_type=live`` cameras. "
        "Authenticate with ``Authorization: Bearer`` or ``?token=<jwt>`` "
        "(required for ``<img>`` tags). Each viewer opens its own RTSP connection."
    ),
    responses={
        200: {
            "content": {"multipart/x-mixed-replace": {}},
            "description": "MJPEG frame stream",
        },
        404: {"description": "Camera not found or not a live source"},
        503: {"description": "Stream could not be opened"},
    },
)
def camera_stream(
    camera_id: str,
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user_from_token)],
) -> StreamingResponse:
    camera = require_camera_in_org(session, camera_id, user.org_id)
    if camera.source_type != "live":
        raise ApiError(
            404,
            "camera_not_live",
            f"Camera '{camera_id}' is not a live source",
        )
    if not camera.rtsp_url:
        raise ApiError(
            400,
            "no_stream_url",
            f"Camera '{camera_id}' has no stream URL configured",
        )

    try:
        source, first_chunk = open_stream_source(camera.rtsp_url)
    except StreamOpenError as exc:
        raise ApiError(
            503,
            "stream_unavailable",
            f"Could not open camera stream: {exc}",
        ) from exc

    return StreamingResponse(
        async_iter_open_mjpeg_stream(source, first_chunk, camera_id=camera.id),
        media_type=MJPEG_CONTENT_TYPE,
        headers={"Cache-Control": "no-store"},
    )


@router.get(
    "/{camera_id}/snapshot",
    summary="Camera reference-frame snapshot",
    description=(
        "Return a single JPEG snapshot for admin UI backgrounds. "
        "Live cameras capture one fresh frame per request (not cached). "
        "Recorded cameras serve the preview frame from the most recent completed "
        "processing run. Authenticate with ``Authorization: Bearer`` or "
        "``?token=<jwt>`` (required for ``<img>`` tags)."
    ),
    responses={
        200: {
            "content": {"image/jpeg": {}},
            "description": "JPEG snapshot",
        },
        404: {"description": "Camera not found or recorded preview not available"},
        503: {"description": "Live stream could not be opened"},
    },
)
def camera_snapshot(
    camera_id: str,
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user_from_token)],
) -> Response:
    camera = require_camera_in_org(session, camera_id, user.org_id)

    if camera.source_type == "live":
        if not camera.rtsp_url:
            raise ApiError(
                400,
                "no_stream_url",
                f"Camera '{camera_id}' has no stream URL configured",
            )
        try:
            jpeg = capture_snapshot_jpeg(camera.rtsp_url)
        except StreamOpenError as exc:
            raise ApiError(
                503,
                "stream_unavailable",
                f"Could not capture camera snapshot: {exc}",
            ) from exc
        return Response(
            content=jpeg,
            media_type="image/jpeg",
            headers={"Cache-Control": "no-store"},
        )

    if camera.source_type != "recorded":
        raise ApiError(
            400,
            "invalid_camera_source",
            f"Camera '{camera_id}' has unsupported source_type '{camera.source_type}'",
        )

    run = get_latest_completed_processing_run(session, camera_id)
    if run is None or not run.preview_frame_path:
        raise ApiError(
            404,
            "preview_not_available",
            "Preview not available yet — process this camera first",
        )

    resolved = resolve_repo_data_path(run.preview_frame_path)
    if not resolved.is_file():
        raise ApiError(
            404,
            "preview_not_available",
            "Preview not available yet — process this camera first",
        )

    return FileResponse(
        path=str(resolved),
        media_type="image/jpeg",
        filename=resolved.name,
        headers={"Cache-Control": "public, max-age=60"},
    )
