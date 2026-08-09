"""Alerts endpoint."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from database.models import Alert

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession
from ..schemas.alerts import AlertListResponse, AlertResponse
from ..services.org_scope import alerts_for_org_stmt

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get(
    "",
    response_model=AlertListResponse,
    summary="List alerts",
    description="Return alerts filtered by status and/or severity.",
)
def list_alerts(
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user)],
    status: Annotated[
        Literal["open", "acknowledged", "resolved"] | None,
        Query(description="Filter by alert status"),
    ] = None,
    severity: Annotated[
        Literal["info", "warning", "critical"] | None,
        Query(description="Filter by severity"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> AlertListResponse:
    stmt = alerts_for_org_stmt(user.org_id).order_by(Alert.timestamp.desc()).limit(limit)  # type: ignore[attr-defined]
    if status is not None:
        stmt = stmt.where(Alert.status == status)
    if severity is not None:
        stmt = stmt.where(Alert.severity == severity)

    rows = session.exec(stmt).all()
    alerts = [
        AlertResponse(
            id=r.id,  # type: ignore[arg-type]
            alert_type=r.alert_type,
            camera_id=r.camera_id,
            zone_id=r.zone_id,
            timestamp=r.timestamp.isoformat(),
            severity=r.severity,
            status=r.status,
            metadata_=r.metadata_ or {},
        )
        for r in rows
    ]
    return AlertListResponse(count=len(alerts), alerts=alerts)
