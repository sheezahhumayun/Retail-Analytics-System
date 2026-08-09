"""Raw analytics events endpoint."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from database.models import Event

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession, require_date_range
from ..schemas.events import EventListResponse, EventResponse
from ..services.org_scope import events_for_org_stmt, require_camera_in_org

router = APIRouter(prefix="/events", tags=["Events"])


@router.get(
    "",
    response_model=EventListResponse,
    summary="List analytics events",
    description="Query raw events table with optional camera and event_type filters.",
)
def list_events(
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user)],
    date_range: Annotated[tuple, Depends(require_date_range)],
    camera_id: Annotated[str | None, Query(description="Filter by camera")] = None,
    event_type: Annotated[str | None, Query(description="Filter by event type")] = None,
    limit: Annotated[int, Query(ge=1, le=1000, description="Max rows")] = 200,
) -> EventListResponse:
    start, end = date_range

    if camera_id is not None:
        require_camera_in_org(session, camera_id, user.org_id)

    stmt = (
        events_for_org_stmt(user.org_id)
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
