"""Analytics read endpoints (aggregate tables from Module 11)."""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlmodel import col, select

from database.models import (
    DwellEventRow,
    OccupancyMetric,
    QueueMetric,
    Store,
    VisitorMetric,
    Zone,
    ZoneMetric,
)

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession, parse_date, parse_time, require_date_range
from ..exceptions import ApiError
from ..schemas.analytics import (
    DwellResponse,
    DwellSession,
    OccupancyPoint,
    OccupancyResponse,
    QueueAnalyticsResponse,
    QueueSample,
    TrafficBucket,
    TrafficResponse,
    ZoneAnalyticsResponse,
    ZoneMetricBucket,
)
from ..services.heatmap import fetch_heatmap
from ..schemas.analytics import HeatmapResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/traffic",
    response_model=TrafficResponse,
    summary="Visitor traffic by hour",
    description=(
        "Hourly entry/exit counts for a store from `visitor_metrics`. "
        "Query `from` and `to` as ISO dates or datetimes."
    ),
)
def traffic(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    store_id: Annotated[str, Query(description="Store id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
) -> TrafficResponse:
    start, end = date_range
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")

    rows = session.exec(
        select(VisitorMetric)
        .where(
            VisitorMetric.store_id == store_id,
            VisitorMetric.metric_date >= start.date(),
            VisitorMetric.metric_date <= end.date(),
        )
        .order_by(VisitorMetric.metric_date, VisitorMetric.hour)
    ).all()

    buckets = [
        TrafficBucket(
            metric_date=r.metric_date.isoformat(),
            hour=r.hour,
            entries=r.entries,
            exits=r.exits,
        )
        for r in rows
    ]
    return TrafficResponse(
        store_id=store_id,
        from_=start.isoformat(),
        to=end.isoformat(),
        buckets=buckets,
        total_entries=sum(b.entries for b in buckets),
        total_exits=sum(b.exits for b in buckets),
    )


@router.get(
    "/occupancy",
    response_model=OccupancyResponse,
    summary="Current occupancy and trend",
    description="Latest occupancy plus time-series. Provide `camera_id` or `store_id` (not both).",
)
def occupancy(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    camera_id: Annotated[str | None, Query()] = None,
    store_id: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=500, description="Max trend points")] = 100,
) -> OccupancyResponse:
    if (camera_id is None) == (store_id is None):
        raise ApiError(
            400,
            "invalid_scope",
            "Provide exactly one of camera_id or store_id",
        )

    if camera_id is not None:
        from database.models import Camera

        if session.get(Camera, camera_id) is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        stmt = (
            select(OccupancyMetric)
            .where(OccupancyMetric.camera_id == camera_id)
            .order_by(col(OccupancyMetric.timestamp).desc())
            .limit(limit)
        )
        scope, scope_id = "camera", camera_id
    else:
        assert store_id is not None
        if session.get(Store, store_id) is None:
            raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
        stmt = (
            select(OccupancyMetric)
            .where(OccupancyMetric.store_id == store_id)
            .order_by(col(OccupancyMetric.timestamp).desc())
            .limit(limit)
        )
        scope, scope_id = "store", store_id

    rows = list(reversed(session.exec(stmt).all()))
    if not rows:
        return OccupancyResponse(scope=scope, scope_id=scope_id, current=0, trend=[])

    trend = [
        OccupancyPoint(
            timestamp=r.timestamp.isoformat(),
            current_occupancy=r.current_occupancy,
        )
        for r in rows
    ]
    return OccupancyResponse(
        scope=scope,
        scope_id=scope_id,
        current=rows[-1].current_occupancy,
        trend=trend,
    )


@router.get(
    "/zones",
    response_model=ZoneAnalyticsResponse,
    summary="Zone visitor and dwell metrics",
    description="Hourly zone rollups from `zone_metrics`.",
)
def zone_analytics(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    zone_id: Annotated[str, Query(description="Zone id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
) -> ZoneAnalyticsResponse:
    start, end = date_range
    if session.get(Zone, zone_id) is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")

    rows = session.exec(
        select(ZoneMetric)
        .where(
            ZoneMetric.zone_id == zone_id,
            ZoneMetric.metric_date >= start.date(),
            ZoneMetric.metric_date <= end.date(),
        )
        .order_by(ZoneMetric.metric_date, ZoneMetric.hour)
    ).all()

    buckets = [
        ZoneMetricBucket(
            metric_date=r.metric_date.isoformat(),
            hour=r.hour,
            visitors=r.visitors,
            avg_dwell=r.avg_dwell,
            max_dwell=r.max_dwell,
            min_dwell=r.min_dwell,
            dwell_count=r.dwell_count,
        )
        for r in rows
    ]
    return ZoneAnalyticsResponse(
        zone_id=zone_id,
        from_=start.isoformat(),
        to=end.isoformat(),
        buckets=buckets,
    )


@router.get(
    "/dwell",
    response_model=DwellResponse,
    summary="Completed dwell sessions",
    description="Individual dwell events from `dwell_events` for a zone in the given range.",
)
def dwell_analytics(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    zone_id: Annotated[str, Query(description="Zone id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
) -> DwellResponse:
    start, end = date_range
    if session.get(Zone, zone_id) is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")

    rows = session.exec(
        select(DwellEventRow)
        .where(
            DwellEventRow.zone_id == zone_id,
            DwellEventRow.enter_ts >= start,
            DwellEventRow.enter_ts <= end,
        )
        .order_by(DwellEventRow.enter_ts)
    ).all()

    sessions = [
        DwellSession(
            id=r.id,  # type: ignore[arg-type]
            zone_id=r.zone_id,
            track_id=r.track_id,
            enter_ts=r.enter_ts.isoformat(),
            exit_ts=r.exit_ts.isoformat(),
            dwell_seconds=r.dwell_seconds,
        )
        for r in rows
    ]
    avg = sum(s.dwell_seconds for s in sessions) / len(sessions) if sessions else None
    return DwellResponse(
        zone_id=zone_id,
        from_=start.isoformat(),
        to=end.isoformat(),
        sessions=sessions,
        count=len(sessions),
        avg_dwell_seconds=avg,
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
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    camera_id: Annotated[str, Query(description="Camera id")],
    date: Annotated[str, Query(description="Date YYYY-MM-DD")],
    from_time: Annotated[str, Query(description="Start time HH:MM or HH:MM:SS")] = "00:00",
    to_time: Annotated[str, Query(description="End time HH:MM or HH:MM:SS")] = "23:59",
) -> HeatmapResponse:
    metric_date = parse_date(date, param="date")
    start_t = parse_time(from_time, param="from_time")
    end_t = parse_time(to_time, param="to_time")
    return fetch_heatmap(camera_id, metric_date, start_t, end_t)


@router.get(
    "/queues",
    response_model=QueueAnalyticsResponse,
    summary="Queue length and wait time",
    description="Time-series queue samples from `queue_metrics`.",
)
def queue_analytics(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
    zone_id: Annotated[str, Query(description="Queue zone id")],
    date_range: Annotated[tuple, Depends(require_date_range)],
) -> QueueAnalyticsResponse:
    start, end = date_range
    if session.get(Zone, zone_id) is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")

    rows = session.exec(
        select(QueueMetric)
        .where(
            QueueMetric.zone_id == zone_id,
            QueueMetric.timestamp >= start,
            QueueMetric.timestamp <= end,
        )
        .order_by(QueueMetric.timestamp)
    ).all()

    samples = [
        QueueSample(
            timestamp=r.timestamp.isoformat(),
            queue_length=r.queue_length,
            estimated_wait=r.estimated_wait,
        )
        for r in rows
    ]
    avg_len = sum(s.queue_length for s in samples) / len(samples) if samples else None
    max_len = max((s.queue_length for s in samples), default=None)
    return QueueAnalyticsResponse(
        zone_id=zone_id,
        from_=start.isoformat(),
        to=end.isoformat(),
        samples=samples,
        avg_queue_length=avg_len,
        max_queue_length=max_len,
    )
