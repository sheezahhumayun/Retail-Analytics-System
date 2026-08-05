"""Camera CRUD and status endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import select

from database.models import Camera, Event, OccupancyMetric, Store

from ..auth import TokenPayload, get_current_user, get_current_user_from_token, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..services.camera_stream import (
    MJPEG_CONTENT_TYPE,
    StreamOpenError,
    async_iter_open_mjpeg_stream,
    open_stream_source,
)
from ..schemas.cameras import (
    CameraCreate,
    CameraResponse,
    CameraStatusResponse,
)
from ..services.camera_health import refresh_camera_status
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
    _user: Annotated[TokenPayload, Depends(get_current_user)],
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
    stmt = select(Camera).order_by(Camera.name)
    if store_id is not None:
        if session.get(Store, store_id) is None:
            raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
        stmt = stmt.where(Camera.store_id == store_id)
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
    _user: Annotated[TokenPayload, Depends(require_admin)],
) -> CameraResponse:
    store = session.get(Store, body.store_id)
    if store is None:
        raise ApiError(404, "store_not_found", f"Store '{body.store_id}' not found")
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
    _user: Annotated[TokenPayload, Depends(get_current_user)],
) -> CameraStatusResponse:
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")

    if camera.source_type == "live" and camera.status != "disabled":
        refresh_camera_status(session, camera)

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
    _user: Annotated[TokenPayload, Depends(get_current_user_from_token)],
) -> StreamingResponse:
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
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
