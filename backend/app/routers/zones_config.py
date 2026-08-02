"""Zone geometry CRUD (Module 12.5 — zone_shapes table)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from database.models import Camera, ZoneShape

from ..auth import TokenPayload, get_current_user, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.extended.zones import ZoneShapeCreate, ZoneShapeResponse, ZoneShapeUpdate

router = APIRouter(prefix="/zones", tags=["Zone configuration"])


def _to_response(row: ZoneShape) -> ZoneShapeResponse:
    return ZoneShapeResponse(
        id=row.id,
        camera_id=row.camera_id,
        name=row.name,
        type=row.shape_type,
        polygon_points=row.polygon_points,
        created_at=row.created_at.isoformat(),
    )


@router.get(
    "",
    response_model=list[ZoneShapeResponse],
    summary="List zone shapes",
    description=(
        "Return configured zone polygons (geometry/config, not analytics metrics). "
        "Omit `camera_id` to list all zones in one call."
    ),
)
def list_zones(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    camera_id: Annotated[str | None, Query(description="Optional camera id filter")] = None,
) -> list[ZoneShapeResponse]:
    stmt = select(ZoneShape).order_by(ZoneShape.name)
    if camera_id is not None:
        if session.get(Camera, camera_id) is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        stmt = stmt.where(ZoneShape.camera_id == camera_id)
    rows = session.exec(stmt).all()
    return [_to_response(r) for r in rows]


@router.post(
    "",
    response_model=ZoneShapeResponse,
    status_code=201,
    summary="Create zone shape",
    description="Create a zone polygon for a camera. Admin only.",
)
def create_zone(
    body: ZoneShapeCreate,
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> ZoneShapeResponse:
    if session.get(ZoneShape, body.id) is not None:
        raise ApiError(409, "zone_exists", f"Zone '{body.id}' already exists")
    if session.get(Camera, body.camera_id) is None:
        raise ApiError(404, "camera_not_found", f"Camera '{body.camera_id}' not found")
    row = ZoneShape(
        id=body.id,
        camera_id=body.camera_id,
        name=body.name,
        shape_type=body.type,
        polygon_points=body.polygon_points,
        created_at=datetime.now(timezone.utc),
    )
    session.add(row)
    session.flush()
    session.refresh(row)
    return _to_response(row)


@router.put(
    "/{zone_id}",
    response_model=ZoneShapeResponse,
    summary="Update zone shape",
    description="Replace zone name, type, or polygon. Admin only.",
)
def update_zone(
    zone_id: str,
    body: ZoneShapeUpdate,
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> ZoneShapeResponse:
    row = session.get(ZoneShape, zone_id)
    if row is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
    if body.name is not None:
        row.name = body.name
    if body.type is not None:
        row.shape_type = body.type
    if body.polygon_points is not None:
        row.polygon_points = body.polygon_points
    session.add(row)
    session.flush()
    session.refresh(row)
    return _to_response(row)


@router.delete(
    "/{zone_id}",
    status_code=204,
    summary="Delete zone shape",
    description="Remove a zone polygon configuration. Admin only.",
)
def delete_zone(
    zone_id: str,
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> None:
    row = session.get(ZoneShape, zone_id)
    if row is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
    session.delete(row)
