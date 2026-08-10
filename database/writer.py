"""Persist analytics bus events and roll up aggregate tables (Module 11)."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import date, datetime, timezone as dt_timezone
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import func
from sqlmodel import Session, col, select

from analytics.dwell.types import DwellEvent
from analytics.occupancy.tracker import _normalize_timezone
from analytics.events.types import AnalyticsEvent, AnalyticsEventType
from analytics.modules import (
    ALL_ANALYTICS_MODULES,
    MODULE_ENTRY_EXIT,
    MODULE_OCCUPANCY,
    MODULE_ZONES,
    normalize_modules,
)
from analytics.queues.types import is_queue_zone
from analytics.zones.types import Zone, ZoneEvent, ZoneEventType

from backend.app.services.alert_rules import get_occupancy_severity

from .models import (
    Alert,
    DwellEventRow,
    Event,
    OccupancyMetric,
    QueueMetric,
    Track,
    VisitorMetric,
    ZoneMetric,
)
from .session import get_engine, session_scope


def _utc_from_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=dt_timezone.utc)
    return value.astimezone(dt_timezone.utc)


def _local_parts(ts: datetime, tz: ZoneInfo | dt_timezone) -> tuple[date, int]:
    local = _utc_from_datetime(ts).astimezone(tz)
    return local.date(), local.hour


@dataclass
class DbWriterConfig:
    """Maps pipeline string ids to store / timezone for rollups."""

    store_id: str
    camera_store_map: dict[str, str] = field(default_factory=dict)
    zones: list[Zone] = field(default_factory=list)
    timezone: str = "UTC"
    persist_person_detected: bool = False
    enabled_modules: frozenset[str] = field(
        default_factory=lambda: frozenset(ALL_ANALYTICS_MODULES),
    )
    camera_modules: dict[str, frozenset[str]] = field(default_factory=dict)


class AnalyticsDbWriter:
    """Subscribe to the event bus and write events + aggregate metrics to Postgres.

    Also exposes :meth:`on_dwell_event` and :meth:`on_queue_sample` for data that
    never appears on the bus (completed dwell sessions, queue length samples).
    """

    def __init__(self, config: DbWriterConfig) -> None:
        self._config = config
        self._tz = _normalize_timezone(config.timezone)
        self._default_modules = frozenset(normalize_modules(config.enabled_modules))
        self._camera_modules: dict[str, frozenset[str]] = {
            camera_id: frozenset(normalize_modules(modules))
            for camera_id, modules in config.camera_modules.items()
        }
        self._queue_zone_ids = {
            z.zone_id for z in config.zones if is_queue_zone(z)
        }
        self._camera_occupancy: dict[str, int] = {}
        self._store_occupancy: int = 0
        self._closed = False
        self._lock = threading.Lock()
        self._session = Session(get_engine())
        self._reload_occupancy_from_db()

    def _reload_occupancy_from_db(self) -> None:
        """Restore in-memory occupancy counters from the latest persisted snapshots."""
        camera_ids = set(self._config.camera_store_map.keys())
        if not camera_ids:
            return
        session = self._session
        for camera_id in camera_ids:
            row = session.exec(
                select(OccupancyMetric)
                .where(OccupancyMetric.camera_id == camera_id)
                .order_by(col(OccupancyMetric.timestamp).desc(), col(OccupancyMetric.id).desc())
            ).first()
            if row is not None:
                self._camera_occupancy[camera_id] = row.current_occupancy

        store_id = self._config.store_id
        if store_id:
            store_row = session.exec(
                select(OccupancyMetric)
                .where(
                    OccupancyMetric.store_id == store_id,
                    OccupancyMetric.camera_id.is_(None),  # type: ignore[union-attr]
                )
                .order_by(col(OccupancyMetric.timestamp).desc(), col(OccupancyMetric.id).desc())
            ).first()
            if store_row is not None:
                self._store_occupancy = store_row.current_occupancy
            else:
                self._store_occupancy = sum(self._camera_occupancy.values())

    def close(self) -> None:
        """Release the held DB connection back to the pool."""
        if self._closed:
            return
        self._session.close()
        self._closed = True

    @property
    def config(self) -> DbWriterConfig:
        return self._config

    def subscribe(self, bus) -> None:
        bus.subscribe(self.on_event)

    def unsubscribe(self, bus) -> None:
        bus.unsubscribe(self.on_event)

    def _modules_for_camera(self, camera_id: str) -> frozenset[str]:
        with self._lock:
            if camera_id in self._camera_modules:
                return self._camera_modules[camera_id]
            return self._default_modules

    def add_camera(
        self,
        camera_id: str,
        store_id: str,
        modules: frozenset[str],
        *,
        zones: list[Zone] | None = None,
    ) -> None:
        """Register a camera on a running shared writer (live analytics worker)."""
        normalized = frozenset(normalize_modules(modules))
        with self._lock:
            self._config.camera_store_map[camera_id] = store_id
            self._camera_modules[camera_id] = normalized
            if zones:
                existing_ids = {zone.zone_id for zone in self._config.zones}
                for zone in zones:
                    if zone.zone_id not in existing_ids:
                        self._config.zones.append(zone)
                        existing_ids.add(zone.zone_id)
                    if is_queue_zone(zone):
                        self._queue_zone_ids.add(zone.zone_id)

        occupancy_value: int | None = None
        with session_scope() as session:
            row = session.exec(
                select(OccupancyMetric)
                .where(OccupancyMetric.camera_id == camera_id)
                .order_by(col(OccupancyMetric.timestamp).desc(), col(OccupancyMetric.id).desc())
            ).first()
            if row is not None:
                occupancy_value = row.current_occupancy
        if occupancy_value is not None:
            with self._lock:
                self._camera_occupancy[camera_id] = occupancy_value

    def remove_camera(self, camera_id: str) -> None:
        """Unregister a camera from a running shared writer."""
        with self._lock:
            self._config.camera_store_map.pop(camera_id, None)
            self._camera_modules.pop(camera_id, None)
            self._camera_occupancy.pop(camera_id, None)

    def on_event(self, event: AnalyticsEvent) -> None:
        if (
            event.event_type == AnalyticsEventType.PERSON_DETECTED.value
            and not self._config.persist_person_detected
        ):
            return

        try:
            self._insert_event(self._session, event)
            self._apply_event_aggregates(self._session, event)
            if event.track_id is not None:
                self._upsert_track(self._session, event)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def on_dwell_event(self, dwell: DwellEvent) -> None:
        try:
            self._session.add(
                DwellEventRow(
                    zone_id=dwell.zone_id,
                    track_id=str(dwell.track_id),
                    enter_ts=datetime.fromtimestamp(dwell.enter_timestamp, tz=dt_timezone.utc),
                    exit_ts=datetime.fromtimestamp(dwell.exit_timestamp, tz=dt_timezone.utc),
                    dwell_seconds=dwell.dwell_seconds,
                )
            )
            exit_dt = datetime.fromtimestamp(dwell.exit_timestamp, tz=dt_timezone.utc)
            metric_date, hour = _local_parts(exit_dt, self._tz)
            zm = self._get_or_create_zone_metric(
                self._session, dwell.zone_id, metric_date, hour
            )
            count = zm.dwell_count + 1
            zm.dwell_count = count
            zm.avg_dwell = ((zm.avg_dwell * (count - 1)) + dwell.dwell_seconds) / count
            zm.max_dwell = max(zm.max_dwell, dwell.dwell_seconds)
            if zm.min_dwell is None:
                zm.min_dwell = dwell.dwell_seconds
            else:
                zm.min_dwell = min(zm.min_dwell, dwell.dwell_seconds)
            self._session.add(zm)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def on_queue_sample(
        self,
        *,
        zone_id: str,
        timestamp: float,
        queue_length: int,
        estimated_wait: float,
    ) -> None:
        if zone_id not in self._queue_zone_ids:
            return
        ts = datetime.fromtimestamp(timestamp, tz=dt_timezone.utc)
        try:
            self._session.add(
                QueueMetric(
                    zone_id=zone_id,
                    timestamp=ts,
                    queue_length=queue_length,
                    estimated_wait=estimated_wait,
                )
            )
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def on_zone_event(self, event: ZoneEvent) -> None:
        """Record zone enter traffic and optional queue samples."""
        if event.event_type != ZoneEventType.ZONE_ENTER:
            return
        ts = datetime.fromtimestamp(event.timestamp, tz=dt_timezone.utc)
        metric_date, hour = _local_parts(ts, self._tz)
        try:
            zm = self._get_or_create_zone_metric(
                self._session, event.zone_id, metric_date, hour
            )
            zm.visitors += 1
            self._session.add(zm)
            self._session.commit()
        except Exception:
            self._session.rollback()
            raise

    def _insert_event(self, session: Session, event: AnalyticsEvent) -> None:
        session.add(
            Event(
                camera_id=event.camera_id,
                zone_id=event.zone_id,
                track_id=event.track_id,
                event_type=event.event_type,
                timestamp=_utc_from_datetime(event.timestamp),
                metadata_=dict(event.metadata),
            )
        )

    def _apply_event_aggregates(self, session: Session, event: AnalyticsEvent) -> None:
        et = event.event_type
        ts = _utc_from_datetime(event.timestamp)

        modules = self._modules_for_camera(event.camera_id)

        if et in (AnalyticsEventType.ENTRY.value, AnalyticsEventType.EXIT.value):
            if MODULE_ENTRY_EXIT in modules:
                self._update_visitor_metrics(session, event, ts)
            if MODULE_OCCUPANCY in modules:
                self._update_occupancy_metrics(session, event, ts)

        if et == AnalyticsEventType.ZONE_ENTER.value and event.zone_id is not None:
            if MODULE_ZONES in modules:
                metric_date, hour = _local_parts(ts, self._tz)
                zm = self._get_or_create_zone_metric(session, event.zone_id, metric_date, hour)
                zm.visitors += 1
                session.add(zm)

        if et in (
            AnalyticsEventType.DWELL_THRESHOLD.value,
            AnalyticsEventType.QUEUE_THRESHOLD.value,
            AnalyticsEventType.OCCUPANCY_THRESHOLD.value,
            AnalyticsEventType.CAMERA_OFFLINE.value,
        ):
            self._insert_alert(session, event, ts)

    def _update_visitor_metrics(
        self,
        session: Session,
        event: AnalyticsEvent,
        ts: datetime,
    ) -> None:
        store_id = self._config.camera_store_map.get(event.camera_id, self._config.store_id)
        metric_date, hour = _local_parts(ts, self._tz)
        vm = self._get_or_create_visitor_metric(session, store_id, metric_date, hour)
        if event.event_type == AnalyticsEventType.ENTRY.value:
            vm.entries += 1
        else:
            vm.exits += 1
        session.add(vm)

    def _update_occupancy_metrics(
        self,
        session: Session,
        event: AnalyticsEvent,
        ts: datetime,
    ) -> None:
        camera_id = event.camera_id
        current = self._camera_occupancy.get(camera_id, 0)
        if event.event_type == AnalyticsEventType.ENTRY.value:
            current += 1
        else:
            current = max(0, current - 1)
        self._camera_occupancy[camera_id] = current

        store_id = self._config.camera_store_map.get(camera_id, self._config.store_id)
        store_total = sum(
            self._camera_occupancy.get(cid, 0)
            for cid in self._config.camera_store_map
        ) if self._config.camera_store_map else current
        self._store_occupancy = store_total

        session.add(
            OccupancyMetric(
                camera_id=camera_id,
                store_id=None,
                timestamp=ts,
                current_occupancy=current,
            )
        )
        session.add(
            OccupancyMetric(
                camera_id=None,
                store_id=store_id,
                timestamp=ts,
                current_occupancy=store_total,
            )
        )

    def _insert_alert(self, session: Session, event: AnalyticsEvent, ts: datetime) -> None:
        if event.event_type == AnalyticsEventType.CAMERA_OFFLINE.value:
            severity = "critical"
            camera_id = event.camera_id
            zone_id = event.zone_id
        elif event.event_type == AnalyticsEventType.OCCUPANCY_THRESHOLD.value:
            store_id = str(event.metadata.get("store_id", self._config.store_id))
            severity = get_occupancy_severity(store_id, session=self._session)
            camera_id = None
            zone_id = None
        else:
            # DWELL_THRESHOLD / QUEUE_THRESHOLD: severity still hardcoded; loading
            # from alert_rules would require a per-zone DB lookup here.
            severity = "warning"
            camera_id = event.camera_id
            zone_id = event.zone_id
        session.add(
            Alert(
                alert_type=event.event_type,
                camera_id=camera_id,
                zone_id=zone_id,
                timestamp=ts,
                severity=severity,
                status="open",
                metadata_=dict(event.metadata),
            )
        )

    def _upsert_track(self, session: Session, event: AnalyticsEvent) -> None:
        assert event.track_id is not None
        ts = _utc_from_datetime(event.timestamp)
        existing = session.exec(
            select(Track).where(
                Track.camera_id == event.camera_id,
                Track.track_id == event.track_id,
            )
        ).first()
        if existing is None:
            session.add(
                Track(
                    camera_id=event.camera_id,
                    track_id=event.track_id,
                    first_seen=ts,
                    last_seen=ts,
                )
            )
        else:
            existing.last_seen = ts
            session.add(existing)

    def _get_or_create_visitor_metric(
        self,
        session: Session,
        store_id: str,
        metric_date: date,
        hour: int,
    ) -> VisitorMetric:
        row = session.exec(
            select(VisitorMetric).where(
                VisitorMetric.store_id == store_id,
                VisitorMetric.metric_date == metric_date,
                VisitorMetric.hour == hour,
            )
        ).first()
        if row is not None:
            return row
        row = VisitorMetric(store_id=store_id, metric_date=metric_date, hour=hour)
        session.add(row)
        session.flush()
        return row

    def _get_or_create_zone_metric(
        self,
        session: Session,
        zone_id: str,
        metric_date: date,
        hour: int,
    ) -> ZoneMetric:
        row = session.exec(
            select(ZoneMetric).where(
                ZoneMetric.zone_id == zone_id,
                ZoneMetric.metric_date == metric_date,
                ZoneMetric.hour == hour,
            )
        ).first()
        if row is not None:
            return row
        row = ZoneMetric(zone_id=zone_id, metric_date=metric_date, hour=hour)
        session.add(row)
        session.flush()
        return row


def visitors_by_hour_yesterday(
    session: Session,
    store_id: str,
    *,
    timezone: str = "UTC",
    reference: datetime | None = None,
) -> list[dict[str, Any]]:
    """Dashboard query: visitors (entries) by hour for yesterday in store timezone."""
    tz = _normalize_timezone(timezone)
    ref = reference or datetime.now(dt_timezone.utc)
    local_now = ref.astimezone(tz)
    yesterday = (local_now.date()).fromordinal(local_now.date().toordinal() - 1)

    rows = session.exec(
        select(VisitorMetric)
        .where(
            VisitorMetric.store_id == store_id,
            VisitorMetric.metric_date == yesterday,
        )
        .order_by(VisitorMetric.hour)
    ).all()

    return [
        {
            "hour": row.hour,
            "entries": row.entries,
            "exits": row.exits,
            "visitors": row.entries,
        }
        for row in rows
    ]


def event_count(session: Session) -> int:
    return int(session.exec(select(func.count()).select_from(Event)).one())
