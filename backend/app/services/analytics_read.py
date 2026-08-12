"""Gated analytics reads — single code path per metric/scope for any date range."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone as dt_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlmodel import Session, col, select

from database.models import (
    Camera,
    DwellEventRow,
    Event,
    OccupancyMetric,
    QueueMetric,
    Store,
    VisitorMetric,
    Zone,
    ZoneMetric,
)

from ..config import get_settings
from ..exceptions import ApiError
from ..schemas.analytics import (
    DwellSession,
    OccupancyPoint,
    QueueSample,
    TrafficBucket,
    ZoneMetricBucket,
)
from .analytics_comparison import prior_period_bounds, prior_period_comparison_info
from .analytics_modules import (
    MODULE_DWELL,
    MODULE_ENTRY_EXIT,
    MODULE_OCCUPANCY,
    MODULE_QUEUES,
    MODULE_ZONES,
    require_camera_module,
    require_store_module,
    require_zone_module,
)
from .report_eligibility import eligible_cameras_for_store

_ENTRY_EVENT = "ENTRY"
_EXIT_EVENT = "EXIT"
_ZONE_ENTER_EVENT = "ZONE_ENTER"
_ZONE_EXIT_EVENT = "ZONE_EXIT"


def _normalize_timezone(tz: str | ZoneInfo | dt_timezone) -> ZoneInfo | dt_timezone:
    if isinstance(tz, ZoneInfo):
        return tz
    if isinstance(tz, dt_timezone):
        return tz
    if str(tz).upper() == "UTC":
        return dt_timezone.utc
    try:
        return ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        raise ZoneInfoNotFoundError(
            f"{tz!r} requires the tzdata package on Windows (pip install tzdata)"
        ) from None


def _local_parts(ts: datetime, tz: ZoneInfo | dt_timezone) -> tuple[date, int]:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=dt_timezone.utc)
    local = ts.astimezone(tz)
    return local.date(), local.hour


def _traffic_buckets_from_events(
    session: Session,
    *,
    where_clauses: list,
    entry_type: str,
    exit_type: str,
    start: datetime,
    end: datetime,
) -> list[TrafficBucket]:
    """Hourly entry/exit buckets from raw events (camera line or zone boundary)."""
    settings = get_settings()
    tz = _normalize_timezone(settings.store_timezone)
    buckets_map: dict[tuple[date, int], dict[str, int]] = {}
    events = session.exec(
        select(Event).where(
            *where_clauses,
            col(Event.event_type).in_([entry_type, exit_type]),
            Event.timestamp >= start,
            Event.timestamp <= end,
        )
    ).all()
    for event in events:
        metric_date, hour = _local_parts(event.timestamp, tz)
        bucket = buckets_map.setdefault((metric_date, hour), {"entries": 0, "exits": 0})
        if event.event_type == entry_type:
            bucket["entries"] += 1
        else:
            bucket["exits"] += 1

    sorted_keys = sorted(buckets_map.keys())
    return [
        TrafficBucket(
            metric_date=metric_date.isoformat(),
            hour=hour,
            entries=buckets_map[(metric_date, hour)]["entries"],
            exits=buckets_map[(metric_date, hour)]["exits"],
        )
        for metric_date, hour in sorted_keys
    ]


def _traffic_buckets(
    session: Session,
    *,
    camera_ids: list[str],
    start: datetime,
    end: datetime,
) -> list[TrafficBucket]:
    if not camera_ids:
        return []
    return _traffic_buckets_from_events(
        session,
        where_clauses=[col(Event.camera_id).in_(camera_ids)],
        entry_type=_ENTRY_EVENT,
        exit_type=_EXIT_EVENT,
        start=start,
        end=end,
    )


def _zone_traffic_buckets(
    session: Session,
    *,
    zone_id: str,
    start: datetime,
    end: datetime,
) -> list[TrafficBucket]:
    """Zone-scoped traffic from ZONE_ENTER/ZONE_EXIT (same visit semantics as ZoneMetric.visitors)."""
    return _traffic_buckets_from_events(
        session,
        where_clauses=[Event.zone_id == zone_id],
        entry_type=_ZONE_ENTER_EVENT,
        exit_type=_ZONE_EXIT_EVENT,
        start=start,
        end=end,
    )


def _visitor_metric_buckets(
    session: Session,
    *,
    store_id: str,
    start: datetime,
    end: datetime,
) -> list[TrafficBucket]:
    """Store traffic from VisitorMetric rollups — full 24 hours per day, zero-filled."""
    settings = get_settings()
    tz = _normalize_timezone(settings.store_timezone)
    start_date = _local_parts(start, tz)[0]
    end_date = _local_parts(end, tz)[0]
    rows = session.exec(
        select(VisitorMetric).where(
            VisitorMetric.store_id == store_id,
            VisitorMetric.metric_date >= start_date,
            VisitorMetric.metric_date <= end_date,
        )
    ).all()
    by_key = {(r.metric_date, r.hour): r for r in rows}

    buckets: list[TrafficBucket] = []
    current = start_date
    while current <= end_date:
        for hour in range(24):
            row = by_key.get((current, hour))
            buckets.append(
                TrafficBucket(
                    metric_date=current.isoformat(),
                    hour=hour,
                    entries=row.entries if row is not None else 0,
                    exits=row.exits if row is not None else 0,
                )
            )
        current = current.fromordinal(current.toordinal() + 1)
    return buckets


def _zone_buckets(
    session: Session,
    *,
    zone_id: str,
    start: datetime,
    end: datetime,
) -> list[ZoneMetricBucket]:
    rows = session.exec(
        select(ZoneMetric)
        .where(
            ZoneMetric.zone_id == zone_id,
            ZoneMetric.metric_date >= start.date(),
            ZoneMetric.metric_date <= end.date(),
        )
        .order_by(ZoneMetric.metric_date, ZoneMetric.hour)
    ).all()
    return [
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


def _dwell_sessions(
    session: Session,
    *,
    zone_id: str,
    start: datetime,
    end: datetime,
) -> list[DwellSession]:
    rows = session.exec(
        select(DwellEventRow)
        .where(
            DwellEventRow.zone_id == zone_id,
            DwellEventRow.enter_ts >= start,
            DwellEventRow.enter_ts <= end,
        )
        .order_by(DwellEventRow.enter_ts)
    ).all()
    return [
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


def _queue_samples(
    session: Session,
    *,
    zone_id: str,
    start: datetime,
    end: datetime,
) -> list[QueueSample]:
    rows = session.exec(
        select(QueueMetric)
        .where(
            QueueMetric.zone_id == zone_id,
            QueueMetric.timestamp >= start,
            QueueMetric.timestamp <= end,
        )
        .order_by(QueueMetric.timestamp)
    ).all()
    return [
        QueueSample(
            timestamp=r.timestamp.isoformat(),
            queue_length=r.queue_length,
            estimated_wait=r.estimated_wait,
        )
        for r in rows
    ]


def _occupancy_trend(
    session: Session,
    *,
    camera_ids: list[str],
    start: datetime | None,
    end: datetime | None,
    limit: int,
) -> list[OccupancyPoint]:
    if not camera_ids:
        return []
    stmt = select(OccupancyMetric).where(col(OccupancyMetric.camera_id).in_(camera_ids))
    if start is not None:
        stmt = stmt.where(OccupancyMetric.timestamp >= start)
    if end is not None:
        stmt = stmt.where(OccupancyMetric.timestamp <= end)
    stmt = stmt.order_by(col(OccupancyMetric.timestamp).desc()).limit(limit)
    rows = list(reversed(session.exec(stmt).all()))
    return [
        OccupancyPoint(
            timestamp=r.timestamp.isoformat(),
            current_occupancy=r.current_occupancy,
        )
        for r in rows
    ]


@dataclass(frozen=True, slots=True)
class StoreTrafficPeriod:
    buckets: list[TrafficBucket]
    eligible: list[Camera]
    camera_ids: list[str]


@dataclass(frozen=True, slots=True)
class ZoneScopedPeriod:
    zone: Zone
    camera: Camera


def read_store_traffic_period(
    session: Session,
    *,
    store_id: str,
    start: datetime,
    end: datetime,
) -> StoreTrafficPeriod:
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
    require_store_module(session, store_id, MODULE_ENTRY_EXIT)
    eligible = eligible_cameras_for_store(session, store_id, MODULE_ENTRY_EXIT)
    camera_ids = [c.id for c in eligible]
    buckets = _visitor_metric_buckets(session, store_id=store_id, start=start, end=end)
    return StoreTrafficPeriod(buckets=buckets, eligible=eligible, camera_ids=camera_ids)


def read_traffic_for_scope(
    session: Session,
    *,
    store_id: str,
    camera_id: str | None = None,
    zone_id: str | None = None,
    start: datetime,
    end: datetime,
) -> StoreTrafficPeriod:
    """
    Read traffic (entry/exit) at store/camera/zone granularity with module gating.
    
    **Aggregation pattern (reusable for Traffic, Zones, Dwell, Zone Performance):**
    - zone_id specified → aggregate ONLY that zone's traffic (single zone per camera)
    - camera_id specified, no zone_id → aggregate all eligible zones in that camera
    - store_id only → aggregate all eligible zones across all eligible cameras in the store
    
    Module gating: exclude any camera that doesn't have entry_exit enabled.
    
    @return StoreTrafficPeriod with buckets (eligible cameras included for comparison/gating)
    """
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
    
    require_store_module(session, store_id, MODULE_ENTRY_EXIT)
    
    # Resolve which cameras to include
    if zone_id is not None:
        # Zone-level: single zone, single camera (zone's parent camera)
        zone = session.get(Zone, zone_id)
        if zone is None:
            raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
        camera = session.get(Camera, zone.camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{zone.camera_id}' not found")
        require_camera_module(camera, MODULE_ENTRY_EXIT)
        # Zone visit traffic: ZONE_ENTER/EXIT carry zone_id (line ENTRY/EXIT never do).
        # Matches ZoneAnalytics.traffic_by_hour / ZoneMetric.visitors semantics.
        buckets = _zone_traffic_buckets(
            session, zone_id=zone_id, start=start, end=end
        )
        eligible = [camera]
        camera_ids = [camera.id]
    elif camera_id is not None:
        # Camera-level: single camera, all its zones
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        if camera.store_id != store_id:
            raise ApiError(
                400, "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'"
            )
        require_camera_module(camera, MODULE_ENTRY_EXIT)
        eligible = [camera]
        camera_ids = [camera_id]
        buckets = _traffic_buckets(session, camera_ids=camera_ids, start=start, end=end)
    else:
        # Store-level: VisitorMetric rollups (24 zero-filled hours per day).
        eligible = eligible_cameras_for_store(session, store_id, MODULE_ENTRY_EXIT)
        camera_ids = [c.id for c in eligible]
        buckets = _visitor_metric_buckets(session, store_id=store_id, start=start, end=end)

    return StoreTrafficPeriod(buckets=buckets, eligible=eligible, camera_ids=camera_ids)


def read_occupancy_period(
    session: Session,
    *,
    camera_id: str | None,
    store_id: str | None,
    start: datetime | None,
    end: datetime | None,
    limit: int,
) -> tuple[list[OccupancyPoint], list[Camera], str, str]:
    if (camera_id is None) == (store_id is None):
        raise ApiError(
            400,
            "invalid_scope",
            "Provide exactly one of camera_id or store_id",
        )

    if camera_id is not None:
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        require_camera_module(camera, MODULE_OCCUPANCY)
        eligible = [camera]
        scope, scope_id = "camera", camera_id
        camera_ids = [camera_id]
    else:
        assert store_id is not None
        if session.get(Store, store_id) is None:
            raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
        require_store_module(session, store_id, MODULE_OCCUPANCY)
        eligible = eligible_cameras_for_store(session, store_id, MODULE_OCCUPANCY)
        scope, scope_id = "store", store_id
        camera_ids = [c.id for c in eligible]

    trend = _occupancy_trend(
        session,
        camera_ids=camera_ids,
        start=start,
        end=end,
        limit=limit,
    )
    return trend, eligible, scope, scope_id


def _zone_context(session: Session, zone_id: str, module: str) -> ZoneScopedPeriod:
    zone = session.get(Zone, zone_id)
    if zone is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
    require_zone_module(session, zone, module)
    camera = session.get(Camera, zone.camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{zone.camera_id}' not found")
    return ZoneScopedPeriod(zone=zone, camera=camera)


def read_zone_analytics_period(
    session: Session,
    *,
    zone_id: str,
    start: datetime,
    end: datetime,
) -> tuple[list[ZoneMetricBucket], ZoneScopedPeriod]:
    ctx = _zone_context(session, zone_id, MODULE_ZONES)
    buckets = _zone_buckets(session, zone_id=zone_id, start=start, end=end)
    return buckets, ctx


def read_zones_for_scope(
    session: Session,
    *,
    store_id: str,
    camera_id: str | None = None,
    zone_id: str | None = None,
    start: datetime,
    end: datetime,
) -> tuple[list[ZoneMetricBucket], list[Camera]]:
    """
    Read zone metrics at store/camera/zone granularity with module gating.
    
    **Aggregation pattern (same as traffic):**
    - zone_id specified → single zone only
    - camera_id specified, no zone_id → all zones in that camera (excluding queue zones)
    - store_id only → all zones across all cameras in store (excluding queue zones)
    
    Module gating: exclude any camera that doesn't have zones module enabled.
    
    @return Tuple of (aggregated ZoneMetricBucket list, eligible cameras for comparison)
    """
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
    
    require_store_module(session, store_id, MODULE_ZONES)
    
    # Resolve which zones to include and get eligible cameras
    if zone_id is not None:
        # Zone-level: single zone
        zone = session.get(Zone, zone_id)
        if zone is None:
            raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
        camera = session.get(Camera, zone.camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{zone.camera_id}' not found")
        require_camera_module(camera, MODULE_ZONES)
        buckets = _zone_buckets(session, zone_id=zone_id, start=start, end=end)
        eligible = [camera]
    elif camera_id is not None:
        # Camera-level: all zones in that camera (excluding queue zones)
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        if camera.store_id != store_id:
            raise ApiError(
                400, "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'"
            )
        require_camera_module(camera, MODULE_ZONES)
        
        # Get all non-queue zones for this camera (exclude queue zones at query level)
        # Queue zone types: "queue", "checkout", "waiting" (raw zone_type values, before mapping to "checkout_queue")
        zones = session.exec(
            select(Zone).where(
                Zone.camera_id == camera_id,
                Zone.analytics_enabled == True,
                ~Zone.zone_type.in_(["queue", "checkout", "waiting"]),
            )
        ).all()
        
        non_queue_zones = zones
        
        # Aggregate buckets from all non-queue zones
        all_buckets: dict[tuple[date, int], dict[str, int]] = {}
        for zone in non_queue_zones:
            zone_buckets = _zone_buckets(session, zone_id=zone.id, start=start, end=end)
            for bucket in zone_buckets:
                metric_date = datetime.fromisoformat(bucket.metric_date).date()
                key = (metric_date, bucket.hour)
                if key not in all_buckets:
                    all_buckets[key] = {
                        "visitors": 0,
                        "avg_dwell": 0,
                        "max_dwell": 0,
                        "min_dwell": 0,
                        "dwell_count": 0,
                    }
                all_buckets[key]["visitors"] += bucket.visitors
                all_buckets[key]["avg_dwell"] += bucket.avg_dwell
                all_buckets[key]["max_dwell"] = max(all_buckets[key]["max_dwell"], bucket.max_dwell)
                all_buckets[key]["min_dwell"] = min(all_buckets[key]["min_dwell"] or bucket.min_dwell, bucket.min_dwell)
                all_buckets[key]["dwell_count"] += bucket.dwell_count
        
        sorted_keys = sorted(all_buckets.keys())
        buckets = [
            ZoneMetricBucket(
                metric_date=metric_date.isoformat(),
                hour=hour,
                visitors=all_buckets[(metric_date, hour)]["visitors"],
                avg_dwell=all_buckets[(metric_date, hour)]["avg_dwell"] // max(1, all_buckets[(metric_date, hour)]["dwell_count"]),
                max_dwell=all_buckets[(metric_date, hour)]["max_dwell"],
                min_dwell=all_buckets[(metric_date, hour)]["min_dwell"],
                dwell_count=all_buckets[(metric_date, hour)]["dwell_count"],
            )
            for metric_date, hour in sorted_keys
        ]
        eligible = [camera]
    else:
        # Store-level: all zones across all eligible cameras (excluding queue zones)
        eligible = eligible_cameras_for_store(session, store_id, MODULE_ZONES)
        
        # Get all non-queue zones for all eligible cameras
        # Queue zone types: "queue", "checkout", "waiting" (raw zone_type values, before mapping to "checkout_queue")
        zones = session.exec(
            select(Zone).where(
                col(Zone.camera_id).in_([c.id for c in eligible]),
                Zone.analytics_enabled == True,
                ~Zone.zone_type.in_(["queue", "checkout", "waiting"]),
            )
        ).all()
        
        # Aggregate buckets from all non-queue zones
        all_buckets: dict[tuple[date, int], dict[str, int]] = {}
        for zone in zones:
            zone_buckets = _zone_buckets(session, zone_id=zone.id, start=start, end=end)
            for bucket in zone_buckets:
                metric_date = datetime.fromisoformat(bucket.metric_date).date()
                key = (metric_date, bucket.hour)
                if key not in all_buckets:
                    all_buckets[key] = {
                        "visitors": 0,
                        "avg_dwell": 0,
                        "max_dwell": 0,
                        "min_dwell": 0,
                        "dwell_count": 0,
                    }
                all_buckets[key]["visitors"] += bucket.visitors
                all_buckets[key]["avg_dwell"] += bucket.avg_dwell
                all_buckets[key]["max_dwell"] = max(all_buckets[key]["max_dwell"], bucket.max_dwell)
                all_buckets[key]["min_dwell"] = min(all_buckets[key]["min_dwell"] or bucket.min_dwell, bucket.min_dwell)
                all_buckets[key]["dwell_count"] += bucket.dwell_count
        
        sorted_keys = sorted(all_buckets.keys())
        buckets = [
            ZoneMetricBucket(
                metric_date=metric_date.isoformat(),
                hour=hour,
                visitors=all_buckets[(metric_date, hour)]["visitors"],
                avg_dwell=all_buckets[(metric_date, hour)]["avg_dwell"] // max(1, all_buckets[(metric_date, hour)]["dwell_count"]),
                max_dwell=all_buckets[(metric_date, hour)]["max_dwell"],
                min_dwell=all_buckets[(metric_date, hour)]["min_dwell"],
                dwell_count=all_buckets[(metric_date, hour)]["dwell_count"],
            )
            for metric_date, hour in sorted_keys
        ]
    
    return buckets, eligible


def read_dwell_for_scope(
    session: Session,
    *,
    store_id: str,
    camera_id: str | None = None,
    zone_id: str | None = None,
    start: datetime,
    end: datetime,
) -> tuple[list[DwellSession], list[Camera]]:
    """
    Read dwell sessions at store/camera/zone granularity with module gating.
    
    **Aggregation pattern (same as zones/traffic):**
    - zone_id specified → single zone only
    - camera_id specified, no zone_id → all non-queue zones in that camera
    - store_id only → all non-queue zones across all cameras in store
    
    Module gating: exclude any camera that doesn't have dwell module enabled.
    
    @return Tuple of (aggregated DwellSession list, eligible cameras for comparison)
    """
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
    
    require_store_module(session, store_id, MODULE_DWELL)
    
    # Resolve which zones to include and get eligible cameras
    if zone_id is not None:
        # Zone-level: single zone
        zone = session.get(Zone, zone_id)
        if zone is None:
            raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
        camera = session.get(Camera, zone.camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{zone.camera_id}' not found")
        require_camera_module(camera, MODULE_DWELL)
        sessions = _dwell_sessions(session, zone_id=zone_id, start=start, end=end)
        eligible = [camera]
    elif camera_id is not None:
        # Camera-level: all non-queue zones in that camera
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        if camera.store_id != store_id:
            raise ApiError(
                400, "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'"
            )
        require_camera_module(camera, MODULE_DWELL)
        
        # Get all non-queue zones for this camera (exclude queue zones at query level)
        # Queue zone types: "queue", "checkout", "waiting" (raw zone_type values)
        zones = session.exec(
            select(Zone).where(
                Zone.camera_id == camera_id,
                Zone.analytics_enabled == True,
                ~Zone.zone_type.in_(["queue", "checkout", "waiting"]),
            )
        ).all()
        
        # Aggregate sessions from all non-queue zones
        all_sessions: list[DwellSession] = []
        for zone in zones:
            zone_sessions = _dwell_sessions(session, zone_id=zone.id, start=start, end=end)
            all_sessions.extend(zone_sessions)
        
        # Sort by enter timestamp for consistency
        all_sessions.sort(key=lambda s: s.enter_ts)
        sessions = all_sessions
        eligible = [camera]
    else:
        # Store-level: all non-queue zones across all eligible cameras
        eligible = eligible_cameras_for_store(session, store_id, MODULE_DWELL)
        
        # Get all non-queue zones for all eligible cameras
        # Queue zone types: "queue", "checkout", "waiting" (raw zone_type values)
        zones = session.exec(
            select(Zone).where(
                col(Zone.camera_id).in_([c.id for c in eligible]),
                Zone.analytics_enabled == True,
                ~Zone.zone_type.in_(["queue", "checkout", "waiting"]),
            )
        ).all()
        
        # Aggregate sessions from all non-queue zones
        all_sessions: list[DwellSession] = []
        for zone in zones:
            zone_sessions = _dwell_sessions(session, zone_id=zone.id, start=start, end=end)
            all_sessions.extend(zone_sessions)
        
        # Sort by enter timestamp for consistency
        all_sessions.sort(key=lambda s: s.enter_ts)
        sessions = all_sessions
    
    return sessions, eligible


def read_dwell_for_queue_zones(
    session: Session,
    *,
    store_id: str,
    camera_id: str | None = None,
    zone_id: str | None = None,
    start: datetime,
    end: datetime,
) -> tuple[list[DwellSession], list[Camera]]:
    """
    Read dwell sessions for QUEUE ZONES ONLY at store/camera/zone granularity with module gating.
    
    **Aggregation pattern (same as zones/traffic/dwell but QUEUE ZONES ONLY):**
    - zone_id specified → single queue zone only (assumed to be a queue zone)
    - camera_id specified, no zone_id → all QUEUE zones in that camera
    - store_id only → all QUEUE zones across all cameras in store
    
    Module gating: exclude any camera that doesn't have dwell module enabled.
    
    @return Tuple of (aggregated DwellSession list, eligible cameras for comparison)
    """
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
    
    require_store_module(session, store_id, MODULE_DWELL)
    
    # Resolve which zones to include and get eligible cameras
    if zone_id is not None:
        # Zone-level: single queue zone
        zone = session.get(Zone, zone_id)
        if zone is None:
            raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
        camera = session.get(Camera, zone.camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{zone.camera_id}' not found")
        require_camera_module(camera, MODULE_DWELL)
        sessions = _dwell_sessions(session, zone_id=zone_id, start=start, end=end)
        eligible = [camera]
    elif camera_id is not None:
        # Camera-level: all QUEUE zones in that camera
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        if camera.store_id != store_id:
            raise ApiError(
                400, "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'"
            )
        require_camera_module(camera, MODULE_DWELL)
        
        # Get all QUEUE zones for this camera (only queue zone types)
        # Queue zone types: "queue", "checkout", "waiting" (raw zone_type values)
        zones = session.exec(
            select(Zone).where(
                Zone.camera_id == camera_id,
                Zone.analytics_enabled == True,
                Zone.zone_type.in_(["queue", "checkout", "waiting"]),
            )
        ).all()
        
        # Aggregate sessions from all queue zones
        all_sessions: list[DwellSession] = []
        for zone in zones:
            zone_sessions = _dwell_sessions(session, zone_id=zone.id, start=start, end=end)
            all_sessions.extend(zone_sessions)
        
        # Sort by enter timestamp for consistency
        all_sessions.sort(key=lambda s: s.enter_ts)
        sessions = all_sessions
        eligible = [camera]
    else:
        # Store-level: all QUEUE zones across all eligible cameras
        eligible = eligible_cameras_for_store(session, store_id, MODULE_DWELL)
        
        # Get all QUEUE zones for all eligible cameras
        # Queue zone types: "queue", "checkout", "waiting" (raw zone_type values)
        zones = session.exec(
            select(Zone).where(
                col(Zone.camera_id).in_([c.id for c in eligible]),
                Zone.analytics_enabled == True,
                Zone.zone_type.in_(["queue", "checkout", "waiting"]),
            )
        ).all()
        
        # Aggregate sessions from all queue zones
        all_sessions: list[DwellSession] = []
        for zone in zones:
            zone_sessions = _dwell_sessions(session, zone_id=zone.id, start=start, end=end)
            all_sessions.extend(zone_sessions)
        
        # Sort by enter timestamp for consistency
        all_sessions.sort(key=lambda s: s.enter_ts)
        sessions = all_sessions
    
    return sessions, eligible


def read_queue_for_scope(
    session: Session,
    *,
    store_id: str,
    camera_id: str | None = None,
    zone_id: str | None = None,
    start: datetime,
    end: datetime,
) -> tuple[list[QueueSample], list[Camera]]:
    """
    Read queue samples at store/camera/zone granularity with module gating.
    
    **Aggregation pattern (same as zones/traffic/dwell):**
    - zone_id specified → single queue zone only
    - camera_id specified, no zone_id → all queue zones in that camera
    - store_id only → all queue zones across all cameras in store
    
    Module gating: exclude any camera that doesn't have queues module enabled.
    
    @return Tuple of (aggregated QueueSample list, eligible cameras for comparison)
    """
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
    
    require_store_module(session, store_id, MODULE_QUEUES)
    
    # Resolve which zones to include and get eligible cameras
    if zone_id is not None:
        # Zone-level: single queue zone
        zone = session.get(Zone, zone_id)
        if zone is None:
            raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
        camera = session.get(Camera, zone.camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{zone.camera_id}' not found")
        require_camera_module(camera, MODULE_QUEUES)
        samples = _queue_samples(session, zone_id=zone_id, start=start, end=end)
        eligible = [camera]
    elif camera_id is not None:
        # Camera-level: all queue zones in that camera
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        if camera.store_id != store_id:
            raise ApiError(
                400, "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'"
            )
        require_camera_module(camera, MODULE_QUEUES)
        
        # Get all queue zones for this camera (only queue zone types)
        # Queue zone types: "queue", "checkout", "waiting" (raw zone_type values)
        zones = session.exec(
            select(Zone).where(
                Zone.camera_id == camera_id,
                Zone.analytics_enabled == True,
                Zone.zone_type.in_(["queue", "checkout", "waiting"]),
            )
        ).all()
        
        # Aggregate samples from all queue zones
        all_samples: list[QueueSample] = []
        for zone in zones:
            zone_samples = _queue_samples(session, zone_id=zone.id, start=start, end=end)
            all_samples.extend(zone_samples)
        
        # Sort by timestamp for consistency
        all_samples.sort(key=lambda s: s.timestamp)
        samples = all_samples
        eligible = [camera]
    else:
        # Store-level: all queue zones across all eligible cameras
        eligible = eligible_cameras_for_store(session, store_id, MODULE_QUEUES)
        
        # Get all queue zones for all eligible cameras
        # Queue zone types: "queue", "checkout", "waiting" (raw zone_type values)
        zones = session.exec(
            select(Zone).where(
                col(Zone.camera_id).in_([c.id for c in eligible]),
                Zone.analytics_enabled == True,
                Zone.zone_type.in_(["queue", "checkout", "waiting"]),
            )
        ).all()
        
        # Aggregate samples from all queue zones
        all_samples: list[QueueSample] = []
        for zone in zones:
            zone_samples = _queue_samples(session, zone_id=zone.id, start=start, end=end)
            all_samples.extend(zone_samples)
        
        # Sort by timestamp for consistency
        all_samples.sort(key=lambda s: s.timestamp)
        samples = all_samples
    
    return samples, eligible


def read_dwell_period(
    session: Session,
    *,
    zone_id: str,
    start: datetime,
    end: datetime,
) -> tuple[list[DwellSession], ZoneScopedPeriod]:
    ctx = _zone_context(session, zone_id, MODULE_DWELL)
    sessions = _dwell_sessions(session, zone_id=zone_id, start=start, end=end)
    return sessions, ctx


def read_queue_period(
    session: Session,
    *,
    zone_id: str,
    start: datetime,
    end: datetime,
) -> tuple[list[QueueSample], ZoneScopedPeriod]:
    ctx = _zone_context(session, zone_id, MODULE_QUEUES)
    samples = _queue_samples(session, zone_id=zone_id, start=start, end=end)
    return samples, ctx


__all__ = [
    "StoreTrafficPeriod",
    "ZoneScopedPeriod",
    "prior_period_bounds",
    "prior_period_comparison_info",
    "read_dwell_period",
    "read_dwell_for_scope",
    "read_dwell_for_queue_zones",
    "read_occupancy_period",
    "read_queue_period",
    "read_queue_for_scope",
    "read_store_traffic_period",
    "read_zone_analytics_period",
]
