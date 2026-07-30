"""Alert status updates (Module 12.5)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from database.models import Alert

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.extended.alerts import AlertPatch, AlertPatchResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.patch(
    "/{alert_id}",
    response_model=AlertPatchResponse,
    summary="Update alert status",
    description="Acknowledge or resolve an alert. Any authenticated user.",
)
def patch_alert(
    alert_id: int,
    body: AlertPatch,
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
) -> AlertPatchResponse:
    row = session.get(Alert, alert_id)
    if row is None:
        raise ApiError(404, "alert_not_found", f"Alert '{alert_id}' not found")
    row.status = body.status
    session.add(row)
    session.flush()
    session.refresh(row)
    return AlertPatchResponse(
        id=row.id,  # type: ignore[arg-type]
        alert_type=row.alert_type,
        camera_id=row.camera_id,
        zone_id=row.zone_id,
        timestamp=row.timestamp.isoformat(),
        severity=row.severity,
        status=row.status,
        metadata_=row.metadata_ or {},
    )
