"""Raw analytics events endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import select

from database.models import Camera, Event

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession, require_date_range
from ..exceptions import ApiError
from ..schemas.events import EventListResponse, EventResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.get(
    "",
    response_model=EventListResponse,
    summary="List analytics events",
    description="Query raw events table with optional camera and event_type filters.",
)
def list_events(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    date_range: Annotated[tuple, Depends(require_date_range)],
    camera_id: Annotated[str | None, Query(description="Filter by camera")] = None,
    event_type: Annotated[str | None, Query(description="Filter by event type")] = None,
    limit: Annotated[int, Query(ge=1, le=1000, description="Max rows")] = 200,
) -> EventListResponse:
    start, end = date_range

    if camera_id is not None and session.get(Camera, camera_id) is None:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")

    stmt = (
        select(Event)
        .where(Event.timestamp >= start, Event.timestamp <= end)
        .order_by(Event.timestamp.desc())  # type: ignore[attr-defined]
        .limit(limit)
    )
    if camera_id is not None:
        stmt = stmt.where(Event.camera_id == camera_id)
    if event_type is not None:
        stmt = stmt.where(Event.event_type == event_type)

    rows = session.exec(stmt).all()
    events = [
        EventResponse(
            id=r.id,  # type: ignore[arg-type]
            camera_id=r.camera_id,
            zone_id=r.zone_id,
            track_id=r.track_id,
            event_type=r.event_type,
            timestamp=r.timestamp.isoformat(),
            metadata_=r.metadata_ or {},
        )
        for r in rows
    ]
    return EventListResponse(
        from_=start.isoformat(),
        to=end.isoformat(),
        count=len(events),
        events=events,
    )
