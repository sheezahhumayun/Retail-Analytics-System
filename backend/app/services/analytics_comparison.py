"""Period-over-period comparison helpers for analytics and reports."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone as dt_timezone

from sqlmodel import Session, col, func, select

from database.models import (
    Camera,
    DwellEventRow,
    Event,
    OccupancyMetric,
    QueueMetric,
    ZoneMetric,
)

from ..schemas.analytics import ComparisonInfo


def prior_period_bounds(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    """Same inclusive span as ``start``/``end``, immediately preceding."""
    span_days = max(1, (end.date() - start.date()).days + 1)
    prior_end_date = start.date() - timedelta(days=1)
    prior_start_date = prior_end_date - timedelta(days=span_days - 1)
    prior_start = datetime(
        prior_start_date.year,
        prior_start_date.month,
        prior_start_date.day,
        0,
        0,
        0,
        tzinfo=dt_timezone.utc,
    )
    prior_end = datetime(
        prior_end_date.year,
        prior_end_date.month,
        prior_end_date.day,
        23,
        59,
        59,
        tzinfo=dt_timezone.utc,
    )
    return prior_start, prior_end


def _iso_range(start: datetime, end: datetime) -> tuple[str, str]:
    return start.isoformat(), end.isoformat()


def _camera_collection_start(session: Session, camera: Camera) -> datetime | None:
    candidates: list[datetime] = []
    if camera.last_processed_at is not None:
        ts = camera.last_processed_at
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=dt_timezone.utc)
        candidates.append(ts)

    earliest_event = session.exec(
        select(func.min(Event.timestamp)).where(Event.camera_id == camera.id)
    ).one()
    if earliest_event is not None:
        ts = earliest_event
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=dt_timezone.utc)
        candidates.append(ts)

    if not candidates:
        return None
    return min(candidates)


def _zone_collection_start(session: Session, zone_id: str, camera: Camera) -> datetime | None:
    camera_start = _camera_collection_start(session, camera)
    candidates: list[datetime] = []
    if camera_start is not None:
        candidates.append(camera_start)

    for stmt in (
        select(func.min(ZoneMetric.metric_date)).where(ZoneMetric.zone_id == zone_id),
        select(func.min(DwellEventRow.enter_ts)).where(DwellEventRow.zone_id == zone_id),
        select(func.min(QueueMetric.timestamp)).where(QueueMetric.zone_id == zone_id),
    ):
        value = session.exec(stmt).one()
        if value is None:
            continue
        if isinstance(value, date):
            candidates.append(
                datetime(value.year, value.month, value.day, tzinfo=dt_timezone.utc)
            )
        else:
            ts = value
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=dt_timezone.utc)
            candidates.append(ts)

    if not candidates:
        return None
    return min(candidates)


def prior_period_comparison_info(
    session: Session,
    *,
    prior_start: datetime,
    prior_end: datetime,
    scope_cameras: list[Camera],
    zone_id: str | None = None,
    zone_camera: Camera | None = None,
) -> ComparisonInfo:
    """Return prior-period metadata. Module gating must already have been enforced."""
    prior_from, prior_to = _iso_range(prior_start, prior_end)

    collection_starts: list[datetime] = []
    if zone_id is not None and zone_camera is not None:
        zone_start = _zone_collection_start(session, zone_id, zone_camera)
        if zone_start is not None:
            collection_starts.append(zone_start)
    else:
        for camera in scope_cameras:
            cam_start = _camera_collection_start(session, camera)
            if cam_start is not None:
                collection_starts.append(cam_start)

    if collection_starts and prior_start < min(collection_starts):
        return ComparisonInfo(
            status="insufficient_history",
            from_=prior_from,
            to=prior_to,
            message=(
                "Prior period predates when data collection began for this scope"
            ),
        )

    return ComparisonInfo(status="ok", from_=prior_from, to=prior_to)


# Backwards-compatible alias for reports until migrated.
def build_comparison_info(
    session: Session,
    *,
    module: str,  # noqa: ARG001 — kept for call-site compatibility; gating is elsewhere
    cameras: list[Camera],
    prior_start: datetime,
    prior_end: datetime,
    zone_id: str | None = None,
    zone_camera: Camera | None = None,
) -> ComparisonInfo:
    return prior_period_comparison_info(
        session,
        prior_start=prior_start,
        prior_end=prior_end,
        scope_cameras=cameras,
        zone_id=zone_id,
        zone_camera=zone_camera,
    )
