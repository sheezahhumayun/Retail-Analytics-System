"""Zone geometry CRUD (Module 12.5 — zone_shapes table)."""



from __future__ import annotations



import logging

from datetime import datetime, timezone

from typing import Annotated



from fastapi import APIRouter, Depends, Query

from sqlmodel import select



from database.models import Camera, Zone, ZoneShape



from ..auth import TokenPayload, get_current_user, require_admin

from ..deps import DbSession

from ..exceptions import ApiError

from ..schemas.extended.zones import ZoneShapeCreate, ZoneShapeResponse, ZoneShapeUpdate

from ..services.alert_rules import provision_zone_alert_rules
from ..services.org_scope import (
    require_camera_in_org,
    require_zone_shape_in_org,
    zone_shapes_for_org_stmt,
)



router = APIRouter(prefix="/zones", tags=["Zone configuration"])

logger = logging.getLogger(__name__)





def _shape_type_to_zone_type(shape_type: str) -> str:

    """Map zone_shapes.type to analytics zones.zone_type (inverse of seed _map_zone_shape_type)."""

    if shape_type == "checkout_queue":

        return "queue"

    if shape_type == "entrance":

        return "entrance"

    return "general"





def _to_response(row: ZoneShape) -> ZoneShapeResponse:

    return ZoneShapeResponse(

        id=row.id,

        camera_id=row.camera_id,

        name=row.name,

        type=row.shape_type,

        polygon_points=row.polygon_points,

        created_at=row.created_at.isoformat(),

        status=row.status,

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

    user: Annotated[TokenPayload, Depends(get_current_user)],

    camera_id: Annotated[str | None, Query(description="Optional camera id filter")] = None,

    include_disabled: Annotated[

        bool,

        Query(

            description=(

                "Include soft-deleted/disabled zones in the response. "

                "Defaults to False so disabled zones don't reappear in normal "

                "zone pickers/lists after being disabled or deleted."

            )

        ),

    ] = False,

) -> list[ZoneShapeResponse]:

    if camera_id is not None:

        require_camera_in_org(session, camera_id, user.org_id)

    stmt = zone_shapes_for_org_stmt(user.org_id, camera_id=camera_id)

    if not include_disabled:

        stmt = stmt.where(ZoneShape.status != "disabled")

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

    admin: Annotated[TokenPayload, Depends(require_admin)],

) -> ZoneShapeResponse:

    if session.get(ZoneShape, body.id) is not None:

        raise ApiError(409, "zone_exists", f"Zone '{body.id}' already exists")

    camera = require_camera_in_org(session, body.camera_id, admin.org_id)

    zone_type = _shape_type_to_zone_type(body.type)

    row = ZoneShape(

        id=body.id,

        camera_id=body.camera_id,

        name=body.name,

        shape_type=body.type,

        polygon_points=body.polygon_points,

        created_at=datetime.now(timezone.utc),

    )

    session.add(row)

    session.add(

        Zone(

            id=body.id,

            camera_id=body.camera_id,

            name=body.name,

            polygon_coords=body.polygon_points,

            zone_type=zone_type,

            analytics_enabled=True,

        )

    )

    session.flush()

    try:

        provision_zone_alert_rules(

            body.id,

            zone_type,

            store_id=camera.store_id,

            session=session,

        )

    except Exception:

        logger.warning(

            "Failed to provision alert_rules for zone %s; zone created but thresholds "

            "will fall back to org defaults until rules exist",

            body.id,

            exc_info=True,

        )

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

    row = require_zone_shape_in_org(session, zone_id, _admin.org_id)

    if row.status == "disabled":

        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")

    if body.name is not None:

        row.name = body.name

    if body.type is not None:

        row.shape_type = body.type

    if body.polygon_points is not None:

        row.polygon_points = body.polygon_points

    session.add(row)



    analytics_zone = session.get(Zone, zone_id)

    if analytics_zone is not None:

        if body.name is not None:

            analytics_zone.name = body.name

        if body.type is not None:

            analytics_zone.zone_type = _shape_type_to_zone_type(body.type)

        if body.polygon_points is not None:

            analytics_zone.polygon_coords = body.polygon_points

        session.add(analytics_zone)



    session.flush()

    session.refresh(row)

    return _to_response(row)





@router.delete(

    "/{zone_id}",

    status_code=204,

    summary="Delete zone shape",

    description="Soft-delete a zone polygon configuration. Admin only.",

)

def delete_zone(

    zone_id: str,

    session: DbSession,

    admin: Annotated[TokenPayload, Depends(require_admin)],

) -> None:

    row = require_zone_shape_in_org(session, zone_id, admin.org_id)



    row.status = "disabled"

    session.add(row)



    analytics_zone = session.get(Zone, zone_id)

    if analytics_zone is not None:

        analytics_zone.status = "disabled"

        session.add(analytics_zone)


