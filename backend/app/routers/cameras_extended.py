"""Camera admin extensions (Module 12.5)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from database.models import Camera, Store

from ..auth import TokenPayload, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.cameras import CameraResponse
from ..schemas.extended.cameras import CameraTestResponse, CameraUpdate
from ..services.camera_test import test_camera_stream

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.put(
    "/{camera_id}",
    response_model=CameraResponse,
    summary="Update camera",
    description="Update camera configuration. Admin only. Same fields as POST /api/cameras.",
)
def update_camera(
    camera_id: str,
    body: CameraUpdate,
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> Camera:
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")

    if body.store_id is not None:
        if session.get(Store, body.store_id) is None:
            raise ApiError(404, "store_not_found", f"Store '{body.store_id}' not found")
        camera.store_id = body.store_id
    if body.name is not None:
        camera.name = body.name
    if body.location is not None:
        camera.location = body.location
    if body.rtsp_url is not None:
        camera.rtsp_url = body.rtsp_url
    if body.camera_type is not None:
        camera.camera_type = body.camera_type
    if body.resolution is not None:
        camera.resolution = body.resolution
    if body.fps is not None:
        camera.fps = body.fps

    session.add(camera)
    session.flush()
    session.refresh(camera)
    return camera


@router.delete(
    "/{camera_id}",
    response_model=CameraResponse,
    summary="Disable camera (soft delete)",
    description="Mark camera status as `disabled` without removing historical data. Admin only.",
)
def disable_camera(
    camera_id: str,
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> Camera:
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
    camera.status = "disabled"
    session.add(camera)
    session.flush()
    session.refresh(camera)
    return camera


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
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CameraTestResponse:
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
    return test_camera_stream(camera.rtsp_url)
