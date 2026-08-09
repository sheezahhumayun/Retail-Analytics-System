"""Counting line CRUD (Module 12.5)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from database.models import CountingLine

from ..auth import TokenPayload, get_current_user, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.extended.lines import (
    CountingLineCreate,
    CountingLineResponse,
    CountingLineUpdate,
    Point,
)
from ..services.org_scope import (
    counting_lines_for_org_stmt,
    require_camera_in_org,
    require_line_in_org,
)

router = APIRouter(prefix="/lines", tags=["Counting lines"])


def _to_response(row: CountingLine) -> CountingLineResponse:
    return CountingLineResponse(
        id=row.id,
        camera_id=row.camera_id,
        name=row.name,
        point_a=Point(**row.point_a),
        point_b=Point(**row.point_b),
        direction=row.direction,  # type: ignore[arg-type]
        created_at=row.created_at.isoformat(),
        status=row.status,
    )


@router.get(
    "",
    response_model=list[CountingLineResponse],
    summary="List counting lines",
    description=(
        "Return counting line geometry. "
        "Omit `camera_id` to list all lines in one call."
    ),
)
def list_lines(
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user)],
    camera_id: Annotated[str | None, Query(description="Optional camera id filter")] = None,
    include_disabled: Annotated[
        bool,
        Query(
            description=(
                "Include soft-deleted/disabled counting lines in the response. "
                "Defaults to False so disabled lines don't reappear in normal "
                "line pickers/lists after being disabled or deleted."
            )
        ),
    ] = False,
) -> list[CountingLineResponse]:
    if camera_id is not None:
        require_camera_in_org(session, camera_id, user.org_id)
    stmt = counting_lines_for_org_stmt(user.org_id, camera_id=camera_id)
    if not include_disabled:
        stmt = stmt.where(CountingLine.status != "disabled")
    rows = session.exec(stmt).all()
    return [_to_response(r) for r in rows]


@router.post(
    "",
    response_model=CountingLineResponse,
    status_code=201,
    summary="Create counting line",
    description="Create a counting line for a camera. Admin only.",
)
def create_line(
    body: CountingLineCreate,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CountingLineResponse:
    if session.get(CountingLine, body.id) is not None:
        raise ApiError(409, "line_exists", f"Counting line '{body.id}' already exists")
    require_camera_in_org(session, body.camera_id, admin.org_id)
    row = CountingLine(
        id=body.id,
        camera_id=body.camera_id,
        name=body.name,
        point_a=body.point_a.model_dump(),
        point_b=body.point_b.model_dump(),
        direction=body.direction,
        created_at=datetime.now(timezone.utc),
    )
    session.add(row)
    session.flush()
    session.refresh(row)
    return _to_response(row)


@router.put(
    "/{line_id}",
    response_model=CountingLineResponse,
    summary="Update counting line",
    description="Update counting line geometry or metadata. Admin only.",
)
def update_line(
    line_id: str,
    body: CountingLineUpdate,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> CountingLineResponse:
    row = require_line_in_org(session, line_id, admin.org_id)
    if row.status == "disabled":
        raise ApiError(404, "line_not_found", f"Counting line '{line_id}' not found")
    if body.name is not None:
        row.name = body.name
    if body.point_a is not None:
        row.point_a = body.point_a.model_dump()
    if body.point_b is not None:
        row.point_b = body.point_b.model_dump()
    if body.direction is not None:
        row.direction = body.direction
    session.add(row)
    session.flush()
    session.refresh(row)
    return _to_response(row)


@router.delete(
    "/{line_id}",
    status_code=204,
    summary="Delete counting line",
    description="Soft-delete a counting line configuration. Admin only.",
)
def delete_line(
    line_id: str,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> None:
    row = require_line_in_org(session, line_id, admin.org_id)

    row.status = "disabled"
    session.add(row)
