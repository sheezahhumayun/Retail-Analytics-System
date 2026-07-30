"""Camera CRUD and status endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from database.models import Camera, Event, OccupancyMetric, Store

from ..auth import TokenPayload, get_current_user, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.cameras import CameraCreate, CameraResponse, CameraStatusResponse

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
) -> list[Camera]:
    stmt = select(Camera).order_by(Camera.name)
    if store_id is not None:
        if session.get(Store, store_id) is None:
            raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
        stmt = stmt.where(Camera.store_id == store_id)
    return list(session.exec(stmt).all())


@router.post(
    "",
    response_model=CameraResponse,
    status_code=201,
    summary="Create camera",
    description="Register a new camera for a store. Requires admin role.",
)
def create_camera(
    body: CameraCreate,
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(require_admin)],
) -> Camera:
    if session.get(Camera, body.id) is not None:
        raise ApiError(409, "camera_exists", f"Camera '{body.id}' already exists")
    store = session.get(Store, body.store_id)
    if store is None:
        raise ApiError(404, "store_not_found", f"Store '{body.store_id}' not found")
    camera = Camera(**body.model_dump(), status="offline")
    session.add(camera)
    session.flush()
    session.refresh(camera)
    return camera


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
        status=camera.status,
        last_seen=last_event.timestamp.isoformat() if last_event else None,
        current_occupancy=occ_row.current_occupancy if occ_row else None,
    )
