"""SQLModel entities mirroring PRD §31."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy import Column, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"

    id: str = Field(primary_key=True, max_length=64)
    name: str = Field(max_length=255, nullable=False)


class Store(SQLModel, table=True):
    __tablename__ = "stores"

    id: str = Field(primary_key=True, max_length=64)
    org_id: str = Field(foreign_key="organizations.id", nullable=False, index=True)
    name: str = Field(max_length=255, nullable=False)
    address: str | None = Field(default=None, max_length=512)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True, max_length=64)
    org_id: str = Field(foreign_key="organizations.id", nullable=False, index=True)
    name: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, nullable=False, unique=True)
    role: str = Field(max_length=64, nullable=False, default="viewer")


class Camera(SQLModel, table=True):
    __tablename__ = "cameras"

    id: str = Field(primary_key=True, max_length=64)
    store_id: str = Field(foreign_key="stores.id", nullable=False, index=True)
    name: str = Field(max_length=255, nullable=False)
    location: str | None = Field(default=None, max_length=255)
    rtsp_url: str | None = Field(default=None, max_length=1024)
    camera_type: str = Field(default="fixed", max_length=64)
    resolution: str | None = Field(default=None, max_length=32)
    fps: float | None = Field(default=None)
    status: str = Field(default="offline", max_length=32)


class Zone(SQLModel, table=True):
    __tablename__ = "zones"

    id: str = Field(primary_key=True, max_length=64)
    camera_id: str = Field(foreign_key="cameras.id", nullable=False, index=True)
    name: str = Field(max_length=255, nullable=False)
    polygon_coords: list[Any] = Field(sa_column=Column(JSONB, nullable=False))
    zone_type: str = Field(max_length=64, nullable=False, default="general")
    analytics_enabled: bool = Field(default=True, nullable=False)


class CountingLine(SQLModel, table=True):
    __tablename__ = "counting_lines"

    id: str = Field(primary_key=True, max_length=64)
    camera_id: str = Field(foreign_key="cameras.id", nullable=False, index=True)
    point_a: dict[str, float] = Field(sa_column=Column(JSONB, nullable=False))
    point_b: dict[str, float] = Field(sa_column=Column(JSONB, nullable=False))
    direction: str = Field(max_length=64, nullable=False, default="bidirectional")


class Track(SQLModel, table=True):
    __tablename__ = "tracks"

    id: int | None = Field(default=None, primary_key=True)
    camera_id: str = Field(foreign_key="cameras.id", nullable=False, index=True)
    track_id: str = Field(max_length=64, nullable=False, index=True)
    first_seen: datetime = Field(nullable=False)
    last_seen: datetime = Field(nullable=False)

    __table_args__ = (
        UniqueConstraint("camera_id", "track_id", name="uq_tracks_camera_track"),
    )


class Event(SQLModel, table=True):
    """Raw analytics events — pruned after retention window (PRD §35)."""

    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_camera_timestamp", "camera_id", "timestamp"),
        Index("ix_events_zone_timestamp", "zone_id", "timestamp"),
    )

    id: int | None = Field(default=None, primary_key=True)
    camera_id: str = Field(foreign_key="cameras.id", nullable=False, index=True)
    zone_id: str | None = Field(default=None, foreign_key="zones.id", index=True)
    track_id: str | None = Field(default=None, max_length=64, index=True)
    event_type: str = Field(max_length=64, nullable=False, index=True)
    timestamp: datetime = Field(nullable=False, index=True)
    metadata_: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, nullable=False, server_default="{}"),
    )


class VisitorMetric(SQLModel, table=True):
    __tablename__ = "visitor_metrics"
    __table_args__ = (
        UniqueConstraint("store_id", "metric_date", "hour", name="uq_visitor_metrics_store_hour"),
        Index("ix_visitor_metrics_store_date_hour", "store_id", "metric_date", "hour"),
    )

    id: int | None = Field(default=None, primary_key=True)
    store_id: str = Field(foreign_key="stores.id", nullable=False, index=True)
    metric_date: date = Field(nullable=False, index=True)
    hour: int = Field(nullable=False, ge=0, le=23)
    entries: int = Field(default=0, nullable=False)
    exits: int = Field(default=0, nullable=False)


class OccupancyMetric(SQLModel, table=True):
    __tablename__ = "occupancy_metrics"
    __table_args__ = (
        Index("ix_occupancy_metrics_camera_timestamp", "camera_id", "timestamp"),
        Index("ix_occupancy_metrics_store_timestamp", "store_id", "timestamp"),
    )

    id: int | None = Field(default=None, primary_key=True)
    camera_id: str | None = Field(default=None, foreign_key="cameras.id", index=True)
    store_id: str | None = Field(default=None, foreign_key="stores.id", index=True)
    timestamp: datetime = Field(nullable=False, index=True)
    current_occupancy: int = Field(default=0, nullable=False)


class ZoneMetric(SQLModel, table=True):
    __tablename__ = "zone_metrics"
    __table_args__ = (
        UniqueConstraint("zone_id", "metric_date", "hour", name="uq_zone_metrics_zone_hour"),
        Index("ix_zone_metrics_zone_date_hour", "zone_id", "metric_date", "hour"),
    )

    id: int | None = Field(default=None, primary_key=True)
    zone_id: str = Field(foreign_key="zones.id", nullable=False, index=True)
    metric_date: date = Field(nullable=False, index=True)
    hour: int = Field(nullable=False, ge=0, le=23)
    visitors: int = Field(default=0, nullable=False)
    avg_dwell: float = Field(default=0.0, nullable=False)
    max_dwell: float = Field(default=0.0, nullable=False)
    min_dwell: float | None = Field(default=None)
    dwell_count: int = Field(default=0, nullable=False)


class DwellEventRow(SQLModel, table=True):
    __tablename__ = "dwell_events"
    __table_args__ = (
        Index("ix_dwell_events_zone_enter", "zone_id", "enter_ts"),
    )

    id: int | None = Field(default=None, primary_key=True)
    zone_id: str = Field(foreign_key="zones.id", nullable=False, index=True)
    track_id: str = Field(max_length=64, nullable=False, index=True)
    enter_ts: datetime = Field(nullable=False)
    exit_ts: datetime = Field(nullable=False)
    dwell_seconds: float = Field(nullable=False)


class QueueMetric(SQLModel, table=True):
    __tablename__ = "queue_metrics"
    __table_args__ = (
        Index("ix_queue_metrics_zone_timestamp", "zone_id", "timestamp"),
    )

    id: int | None = Field(default=None, primary_key=True)
    zone_id: str = Field(foreign_key="zones.id", nullable=False, index=True)
    timestamp: datetime = Field(nullable=False, index=True)
    queue_length: int = Field(default=0, nullable=False)
    estimated_wait: float = Field(default=0.0, nullable=False)


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_timestamp", "timestamp"),
    )

    id: int | None = Field(default=None, primary_key=True)
    alert_type: str = Field(max_length=64, nullable=False, index=True)
    camera_id: str | None = Field(default=None, foreign_key="cameras.id", index=True)
    zone_id: str | None = Field(default=None, foreign_key="zones.id", index=True)
    timestamp: datetime = Field(nullable=False)
    severity: str = Field(default="warning", max_length=32, nullable=False)
    status: str = Field(default="open", max_length=32, nullable=False)
    metadata_: dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB, nullable=False, server_default="{}"),
    )
