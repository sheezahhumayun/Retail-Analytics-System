"""Report endpoints (Module 12.5)."""

from __future__ import annotations

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession, require_date_range
from ..exceptions import ApiError
from ..schemas.extended.reports import ReportPayload, ReportType
from ..services.analytics_modules import require_camera_module
from ..services.org_scope import require_camera_in_org, require_store_in_org
from ..services.report_eligibility import REPORT_TYPE_MODULE
from ..services.reports import build_report, report_to_csv, report_to_pdf

router = APIRouter(prefix="/reports", tags=["Reports"])

_VALID_TYPES: set[str] = {"traffic", "occupancy", "zones", "dwell", "queues"}


@router.get(
    "/{report_type}",
    response_model=ReportPayload,
    summary="Analytics report (JSON)",
    description=(
        "Build a report from the same aggregate tables as /api/analytics/*. "
        "Types: traffic, occupancy, zones, dwell, queues."
    ),
)
def get_report(
    report_type: str,
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str, Query(description="Store id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
    camera_id: Annotated[str | None, Query(description="Optional camera filter")] = None,
    compare: Annotated[bool, Query(description="Include prior-period comparison")] = False,
    format: Annotated[Literal["json"], Query(description="Response format")] = "json",
) -> ReportPayload:
    if report_type not in _VALID_TYPES:
        raise ApiError(400, "invalid_report_type", f"Unknown report type: {report_type}")
    require_store_in_org(session, store_id, user.org_id)
    if camera_id is not None:
        camera = require_camera_in_org(session, camera_id, user.org_id)
        if camera.store_id != store_id:
            raise ApiError(
                400,
                "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'",
            )
        require_camera_module(camera, REPORT_TYPE_MODULE[report_type])
    start, end = date_range
    return build_report(
        session,
        report_type,
        store_id=store_id,
        start=start,
        end=end,
        camera_id=camera_id,
        compare=compare,
    )  # type: ignore[arg-type]


@router.get(
    "/{report_type}/export",
    summary="Export report as CSV or PDF",
    description="Stream a CSV or PDF export built from the same aggregate data as the JSON report.",
)
def export_report(
    report_type: str,
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str, Query(description="Store id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
    format: Annotated[Literal["csv", "pdf"], Query(description="Export format")],
    camera_id: Annotated[str | None, Query(description="Optional camera filter")] = None,
    compare: Annotated[bool, Query(description="Include prior-period comparison")] = False,
) -> Response:
    if report_type not in _VALID_TYPES:
        raise ApiError(400, "invalid_report_type", f"Unknown report type: {report_type}")
    require_store_in_org(session, store_id, user.org_id)
    if camera_id is not None:
        camera = require_camera_in_org(session, camera_id, user.org_id)
        if camera.store_id != store_id:
            raise ApiError(
                400,
                "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'",
            )
        require_camera_module(camera, REPORT_TYPE_MODULE[report_type])
    start, end = date_range
    payload = build_report(
        session,
        report_type,
        store_id=store_id,
        start=start,
        end=end,
        camera_id=camera_id,
        compare=compare,
    )  # type: ignore[arg-type]

    if format == "csv":
        content = report_to_csv(payload)
        return Response(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{report_type}.csv"'},
        )

    pdf_bytes = report_to_pdf(payload)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{report_type}.pdf"'},
    )
