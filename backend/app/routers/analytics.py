"""Analytics read endpoints (aggregate tables from Module 11)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from database.models import Camera

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession, parse_date, parse_time, require_date_range
from ..exceptions import ApiError
from ..schemas.analytics import (
    ComparisonInfo,
    DwellResponse,
    HeatmapResponse,
    OccupancyPoint,
    OccupancyResponse,
    QueueAnalyticsResponse,
    QueueSample,
    TrafficResponse,
    ZoneAnalyticsResponse,
    ZoneMetricBucket,
)
from ..services.analytics_modules import MODULE_HEATMAP, require_camera_module
from ..services.analytics_read import (
    prior_period_bounds,
    prior_period_comparison_info,
    read_dwell_period,
    read_dwell_for_scope,
    read_dwell_for_queue_zones,
    read_occupancy_period,
    read_queue_period,
    read_queue_for_scope,
    read_store_traffic_period,
    read_traffic_for_scope,
    read_zone_analytics_period,
    read_zones_for_scope,
)
from ..services.heatmap import fetch_heatmap

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/traffic",
    response_model=TrafficResponse,
    summary="Visitor traffic by hour",
    description=(
        "Hourly entry/exit counts at store/camera/zone granularity. "
        "Provide `store_id` (required). Optionally provide `camera_id` and/or `zone_id` "
        "to scope the aggregation. Query `from` and `to` as ISO dates or datetimes. "
        "Pass `compare=true` to include the equivalent prior period. "
        "Module gating: entry_exit module must be enabled for all cameras in scope."
    ),
)
def traffic(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str, Query(description="Store id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
    camera_id: Annotated[str | None, Query(description="Camera id (optional)")] = None,
    zone_id: Annotated[str | None, Query(description="Zone id (optional)")] = None,
    compare: Annotated[bool, Query(description="Include prior-period comparison")] = False,
) -> TrafficResponse:
    start, end = date_range
    current = read_traffic_for_scope(
        session,
        store_id=store_id,
        camera_id=camera_id,
        zone_id=zone_id,
        start=start,
        end=end,
    )

    comparison: ComparisonInfo | None = None
    prior_buckets = []
    prior_total_entries: int | None = None
    prior_total_exits: int | None = None

    if compare:
        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = prior_period_comparison_info(
            session,
            prior_start=prior_start,
            prior_end=prior_end,
            scope_cameras=current.eligible,
        )
        if comparison.status == "ok":
            prior = read_traffic_for_scope(
                session,
                store_id=store_id,
                camera_id=camera_id,
                zone_id=zone_id,
                start=prior_start,
                end=prior_end,
            )
            prior_buckets = prior.buckets
            prior_total_entries = sum(b.entries for b in prior_buckets)
            prior_total_exits = sum(b.exits for b in prior_buckets)

    return TrafficResponse(
        store_id=store_id,
        from_=start.isoformat(),
        to=end.isoformat(),
        buckets=current.buckets,
        total_entries=sum(b.entries for b in current.buckets),
        total_exits=sum(b.exits for b in current.buckets),
        comparison=comparison,
        prior_buckets=prior_buckets,
        prior_total_entries=prior_total_entries,
        prior_total_exits=prior_total_exits,
    )


@router.get(
    "/occupancy",
    response_model=OccupancyResponse,
    summary="Current occupancy and trend",
    description=(
        "Occupancy time-series. Provide `camera_id` or `store_id` (not both). "
        "Optional `from`/`to` filter the trend; `compare=true` adds the prior period."
    ),
)
def occupancy(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    camera_id: Annotated[str | None, Query()] = None,
    store_id: Annotated[str | None, Query()] = None,
    from_: Annotated[str | None, Query(alias="from")] = None,
    to: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=500, description="Max trend points")] = 100,
    compare: Annotated[bool, Query(description="Include prior-period comparison")] = False,
) -> OccupancyResponse:
    range_start = None
    range_end = None
    if from_ is not None and to is not None:
        range_start, range_end = require_date_range(from_, to)
    elif from_ is not None or to is not None:
        raise ApiError(
            400,
            "invalid_date_range",
            "Provide both from and to, or neither",
        )

    trend, eligible, scope, scope_id = read_occupancy_period(
        session,
        camera_id=camera_id,
        store_id=store_id,
        start=range_start,
        end=range_end,
        limit=limit,
    )
    if not trend:
        empty = OccupancyResponse(scope=scope, scope_id=scope_id, current=0, trend=[])
        if range_start and range_end:
            empty.from_ = range_start.isoformat()
            empty.to = range_end.isoformat()
        return empty

    comparison: ComparisonInfo | None = None
    prior_trend: list[OccupancyPoint] = []
    prior_current: int | None = None

    if compare and range_start is not None and range_end is not None:
        prior_start, prior_end = prior_period_bounds(range_start, range_end)
        comparison = prior_period_comparison_info(
            session,
            prior_start=prior_start,
            prior_end=prior_end,
            scope_cameras=eligible,
        )
        if comparison.status == "ok":
            prior_trend, _, _, _ = read_occupancy_period(
                session,
                camera_id=camera_id,
                store_id=store_id,
                start=prior_start,
                end=prior_end,
                limit=limit,
            )
            prior_current = prior_trend[-1].current_occupancy if prior_trend else 0

    response = OccupancyResponse(
        scope=scope,
        scope_id=scope_id,
        current=trend[-1].current_occupancy,
        trend=trend,
        comparison=comparison,
        prior_trend=prior_trend,
        prior_current=prior_current,
    )
    if range_start and range_end:
        response.from_ = range_start.isoformat()
        response.to = range_end.isoformat()
    return response


@router.get(
    "/zones",
    response_model=ZoneAnalyticsResponse,
    summary="Zone visitor and dwell metrics",
    description=(
        "Zone metrics at store/camera/zone granularity. "
        "Provide `store_id` (required). Optionally provide `camera_id` and/or `zone_id` "
        "to scope the aggregation. Excludes queue-type zones (checkout_queue) from aggregation. "
        "Query `from` and `to` as ISO dates or datetimes. "
        "Pass `compare=true` to include the equivalent prior period. "
        "Module gating: zones module must be enabled for all cameras in scope."
    ),
)
def zone_analytics(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str, Query(description="Store id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
    camera_id: Annotated[str | None, Query(description="Camera id (optional)")] = None,
    zone_id: Annotated[str | None, Query(description="Zone id (optional)")] = None,
    compare: Annotated[bool, Query(description="Include prior-period comparison")] = False,
) -> ZoneAnalyticsResponse:
    start, end = date_range
    
    # Single zone case - use original read_zone_analytics_period for backward compatibility
    if zone_id is not None and camera_id is None:
        buckets, ctx = read_zone_analytics_period(
            session, zone_id=zone_id, start=start, end=end
        )
        eligible_cameras = [ctx.camera]
    else:
        # Multi-zone aggregation (camera-level or store-level)
        buckets, eligible_cameras = read_zones_for_scope(
            session,
            store_id=store_id,
            camera_id=camera_id,
            zone_id=zone_id,
            start=start,
            end=end,
        )

    comparison: ComparisonInfo | None = None
    prior_buckets: list[ZoneMetricBucket] = []
    if compare:
        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = prior_period_comparison_info(
            session,
            prior_start=prior_start,
            prior_end=prior_end,
            scope_cameras=eligible_cameras,
            zone_id=zone_id,
            zone_camera=eligible_cameras[0] if eligible_cameras else None,
        )
        if comparison.status == "ok":
            if zone_id is not None and camera_id is None:
                prior_buckets, _ = read_zone_analytics_period(
                    session, zone_id=zone_id, start=prior_start, end=prior_end
                )
            else:
                prior_buckets, _ = read_zones_for_scope(
                    session,
                    store_id=store_id,
                    camera_id=camera_id,
                    zone_id=zone_id,
                    start=prior_start,
                    end=prior_end,
                )

    return ZoneAnalyticsResponse(
        zone_id=zone_id or "all",
        from_=start.isoformat(),
        to=end.isoformat(),
        buckets=buckets,
        comparison=comparison,
        prior_buckets=prior_buckets,
    )


@router.get(
    "/dwell",
    response_model=DwellResponse,
    summary="Completed dwell sessions",
    description=(
        "Dwell sessions at store/camera/zone granularity. "
        "Provide `store_id` (required). Optionally provide `camera_id` and/or `zone_id` "
        "to scope the aggregation. Excludes queue-type zones from aggregation. "
        "Pass `compare=true` for the equivalent prior period."
    ),
)
def dwell_analytics(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str, Query(description="Store id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
    camera_id: Annotated[str | None, Query(description="Camera id (optional)")] = None,
    zone_id: Annotated[str | None, Query(description="Zone id (optional)")] = None,
    compare: Annotated[bool, Query(description="Include prior-period comparison")] = False,
) -> DwellResponse:
    start, end = date_range
    
    # Single zone case - use original read_dwell_period for backward compatibility
    if zone_id is not None and camera_id is None:
        sessions, ctx = read_dwell_period(session, zone_id=zone_id, start=start, end=end)
        eligible_cameras = [ctx.camera]
    else:
        # Multi-zone aggregation (camera-level or store-level)
        sessions, eligible_cameras = read_dwell_for_scope(
            session,
            store_id=store_id,
            camera_id=camera_id,
            zone_id=zone_id,
            start=start,
            end=end,
        )
    
    avg = sum(s.dwell_seconds for s in sessions) / len(sessions) if sessions else None

    comparison: ComparisonInfo | None = None
    prior_sessions = []
    prior_count: int | None = None
    prior_avg: float | None = None

    if compare:
        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = prior_period_comparison_info(
            session,
            prior_start=prior_start,
            prior_end=prior_end,
            scope_cameras=eligible_cameras,
            zone_id=zone_id,
            zone_camera=eligible_cameras[0] if eligible_cameras else None,
        )
        if comparison.status == "ok":
            if zone_id is not None and camera_id is None:
                prior_sessions, _ = read_dwell_period(
                    session, zone_id=zone_id, start=prior_start, end=prior_end
                )
            else:
                prior_sessions, _ = read_dwell_for_scope(
                    session,
                    store_id=store_id,
                    camera_id=camera_id,
                    zone_id=zone_id,
                    start=prior_start,
                    end=prior_end,
                )
            prior_count = len(prior_sessions)
            prior_avg = (
                sum(s.dwell_seconds for s in prior_sessions) / len(prior_sessions)
                if prior_sessions
                else None
            )

    return DwellResponse(
        zone_id=zone_id or "all",
        from_=start.isoformat(),
        to=end.isoformat(),
        sessions=sessions,
        count=len(sessions),
        avg_dwell_seconds=avg,
        comparison=comparison,
        prior_sessions=prior_sessions,
        prior_count=prior_count,
        prior_avg_dwell_seconds=prior_avg,
    )


@router.get(
    "/dwell-queues",
    response_model=DwellResponse,
    summary="Dwell sessions in queue zones only (waiting time)",
    description=(
        "Dwell sessions for QUEUE ZONES ONLY at store/camera/zone granularity. "
        "Used for calculating average waiting time in queue zones. "
        "Provide `store_id` (required). Optionally provide `camera_id` and/or `zone_id` "
        "to scope the aggregation. Pass `compare=true` for the equivalent prior period."
    ),
)
def dwell_queues_analytics(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str, Query(description="Store id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
    camera_id: Annotated[str | None, Query(description="Camera id (optional)")] = None,
    zone_id: Annotated[str | None, Query(description="Queue zone id (optional)")] = None,
    compare: Annotated[bool, Query(description="Include prior-period comparison")] = False,
) -> DwellResponse:
    start, end = date_range
    
    # Single zone case - use original read_dwell_period for backward compatibility
    if zone_id is not None and camera_id is None:
        sessions, ctx = read_dwell_period(session, zone_id=zone_id, start=start, end=end)
        eligible_cameras = [ctx.camera]
    else:
        # Multi-zone aggregation for QUEUE ZONES ONLY (camera-level or store-level)
        sessions, eligible_cameras = read_dwell_for_queue_zones(
            session,
            store_id=store_id,
            camera_id=camera_id,
            zone_id=zone_id,
            start=start,
            end=end,
        )
    
    avg = sum(s.dwell_seconds for s in sessions) / len(sessions) if sessions else None

    comparison: ComparisonInfo | None = None
    prior_sessions = []
    prior_count: int | None = None
    prior_avg: float | None = None

    if compare:
        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = prior_period_comparison_info(
            session,
            prior_start=prior_start,
            prior_end=prior_end,
            scope_cameras=eligible_cameras,
            zone_id=zone_id,
            zone_camera=eligible_cameras[0] if eligible_cameras else None,
        )
        if comparison.status == "ok":
            if zone_id is not None and camera_id is None:
                prior_sessions, _ = read_dwell_period(
                    session, zone_id=zone_id, start=prior_start, end=prior_end
                )
            else:
                prior_sessions, _ = read_dwell_for_queue_zones(
                    session,
                    store_id=store_id,
                    camera_id=camera_id,
                    zone_id=zone_id,
                    start=prior_start,
                    end=prior_end,
                )
            prior_count = len(prior_sessions)
            prior_avg = (
                sum(s.dwell_seconds for s in prior_sessions) / len(prior_sessions)
                if prior_sessions
                else None
            )

    return DwellResponse(
        zone_id=zone_id or "all",
        from_=start.isoformat(),
        to=end.isoformat(),
        sessions=sessions,
        count=len(sessions),
        avg_dwell_seconds=avg,
        comparison=comparison,
        prior_sessions=prior_sessions,
        prior_count=prior_count,
        prior_avg_dwell_seconds=prior_avg,
    )


@router.get(
    "/heatmap",
    response_model=HeatmapResponse,
    summary="Pre-aggregated heatmap grid",
    description=(
        "Returns merged hour-bucket heatmap data from Module 8 file storage. "
        "Specify `date` (YYYY-MM-DD), `from_time` and `to_time` (HH:MM)."
    ),
)
def heatmap(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    camera_id: Annotated[str, Query(description="Camera id")],
    date: Annotated[str, Query(description="Date YYYY-MM-DD")],
    from_time: Annotated[str, Query(description="Start time HH:MM or HH:MM:SS")] = "00:00",
    to_time: Annotated[str, Query(description="End time HH:MM or HH:MM:SS")] = "23:59",
) -> HeatmapResponse:
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
    require_camera_module(camera, MODULE_HEATMAP)

    metric_date = parse_date(date, param="date")
    start_t = parse_time(from_time, param="from_time")
    end_t = parse_time(to_time, param="to_time")
    return fetch_heatmap(camera_id, metric_date, start_t, end_t)


@router.get(
    "/queues",
    response_model=QueueAnalyticsResponse,
    summary="Queue length and wait time",
    description=(
        "Queue samples at store/camera/zone granularity (queue zones only). "
        "Provide `store_id` (required). Optionally provide `camera_id` and/or `zone_id` "
        "to scope the aggregation. Pass `compare=true` for prior period."
    ),
)
def queue_analytics(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str, Query(description="Store id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
    camera_id: Annotated[str | None, Query(description="Camera id (optional)")] = None,
    zone_id: Annotated[str | None, Query(description="Queue zone id (optional)")] = None,
    compare: Annotated[bool, Query(description="Include prior-period comparison")] = False,
) -> QueueAnalyticsResponse:
    start, end = date_range
    
    # Single zone case - use original read_queue_period for backward compatibility
    if zone_id is not None and camera_id is None:
        samples, ctx = read_queue_period(session, zone_id=zone_id, start=start, end=end)
        eligible_cameras = [ctx.camera]
    else:
        # Multi-zone aggregation (camera-level or store-level, queue zones only)
        samples, eligible_cameras = read_queue_for_scope(
            session,
            store_id=store_id,
            camera_id=camera_id,
            zone_id=zone_id,
            start=start,
            end=end,
        )
    
    avg_len = sum(s.queue_length for s in samples) / len(samples) if samples else None
    max_len = max((s.queue_length for s in samples), default=None)

    comparison: ComparisonInfo | None = None
    prior_samples: list[QueueSample] = []
    prior_avg: float | None = None
    prior_max: int | None = None

    if compare:
        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = prior_period_comparison_info(
            session,
            prior_start=prior_start,
            prior_end=prior_end,
            scope_cameras=eligible_cameras,
            zone_id=zone_id,
            zone_camera=eligible_cameras[0] if eligible_cameras else None,
        )
        if comparison.status == "ok":
            if zone_id is not None and camera_id is None:
                prior_samples, _ = read_queue_period(
                    session, zone_id=zone_id, start=prior_start, end=prior_end
                )
            else:
                prior_samples, _ = read_queue_for_scope(
                    session,
                    store_id=store_id,
                    camera_id=camera_id,
                    zone_id=zone_id,
                    start=prior_start,
                    end=prior_end,
                )
            prior_avg = (
                sum(s.queue_length for s in prior_samples) / len(prior_samples)
                if prior_samples
                else None
            )
            prior_max = max((s.queue_length for s in prior_samples), default=None)

    return QueueAnalyticsResponse(
        zone_id=zone_id or "all",
        from_=start.isoformat(),
        to=end.isoformat(),
        samples=samples,
        avg_queue_length=avg_len,
        max_queue_length=max_len,
        comparison=comparison,
        prior_samples=prior_samples,
        prior_avg_queue_length=prior_avg,
        prior_max_queue_length=prior_max,
    )
