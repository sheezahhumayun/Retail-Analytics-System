"""Initial PRD §31 schema."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "stores",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_stores_org_id", "stores", ["org_id"])

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("org_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_org_id", "users", ["org_id"])

    op.create_table(
        "cameras",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("rtsp_url", sa.String(length=1024), nullable=True),
        sa.Column("camera_type", sa.String(length=64), nullable=False),
        sa.Column("resolution", sa.String(length=32), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cameras_store_id", "cameras", ["store_id"])

    op.create_table(
        "zones",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("camera_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("polygon_coords", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("zone_type", sa.String(length=64), nullable=False),
        sa.Column("analytics_enabled", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_zones_camera_id", "zones", ["camera_id"])

    op.create_table(
        "counting_lines",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("camera_id", sa.String(length=64), nullable=False),
        sa.Column("point_a", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("point_b", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("direction", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_counting_lines_camera_id", "counting_lines", ["camera_id"])

    op.create_table(
        "tracks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("camera_id", sa.String(length=64), nullable=False),
        sa.Column("track_id", sa.String(length=64), nullable=False),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("camera_id", "track_id", name="uq_tracks_camera_track"),
    )
    op.create_index("ix_tracks_camera_id", "tracks", ["camera_id"])
    op.create_index("ix_tracks_track_id", "tracks", ["track_id"])

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("camera_id", sa.String(length=64), nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=True),
        sa.Column("track_id", sa.String(length=64), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_camera_id", "events", ["camera_id"])
    op.create_index("ix_events_zone_id", "events", ["zone_id"])
    op.create_index("ix_events_track_id", "events", ["track_id"])
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_index("ix_events_timestamp", "events", ["timestamp"])
    op.create_index("ix_events_camera_timestamp", "events", ["camera_id", "timestamp"])
    op.create_index("ix_events_zone_timestamp", "events", ["zone_id", "timestamp"])

    op.create_table(
        "visitor_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("store_id", sa.String(length=64), nullable=False),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("entries", sa.Integer(), nullable=False),
        sa.Column("exits", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "metric_date", "hour", name="uq_visitor_metrics_store_hour"),
    )
    op.create_index("ix_visitor_metrics_store_id", "visitor_metrics", ["store_id"])
    op.create_index("ix_visitor_metrics_metric_date", "visitor_metrics", ["metric_date"])
    op.create_index("ix_visitor_metrics_store_date_hour", "visitor_metrics", ["store_id", "metric_date", "hour"])

    op.create_table(
        "occupancy_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("camera_id", sa.String(length=64), nullable=True),
        sa.Column("store_id", sa.String(length=64), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_occupancy", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_occupancy_metrics_camera_id", "occupancy_metrics", ["camera_id"])
    op.create_index("ix_occupancy_metrics_store_id", "occupancy_metrics", ["store_id"])
    op.create_index("ix_occupancy_metrics_timestamp", "occupancy_metrics", ["timestamp"])
    op.create_index("ix_occupancy_metrics_camera_timestamp", "occupancy_metrics", ["camera_id", "timestamp"])
    op.create_index("ix_occupancy_metrics_store_timestamp", "occupancy_metrics", ["store_id", "timestamp"])

    op.create_table(
        "zone_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("hour", sa.Integer(), nullable=False),
        sa.Column("visitors", sa.Integer(), nullable=False),
        sa.Column("avg_dwell", sa.Float(), nullable=False),
        sa.Column("max_dwell", sa.Float(), nullable=False),
        sa.Column("min_dwell", sa.Float(), nullable=True),
        sa.Column("dwell_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("zone_id", "metric_date", "hour", name="uq_zone_metrics_zone_hour"),
    )
    op.create_index("ix_zone_metrics_zone_id", "zone_metrics", ["zone_id"])
    op.create_index("ix_zone_metrics_metric_date", "zone_metrics", ["metric_date"])
    op.create_index("ix_zone_metrics_zone_date_hour", "zone_metrics", ["zone_id", "metric_date", "hour"])

    op.create_table(
        "dwell_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("track_id", sa.String(length=64), nullable=False),
        sa.Column("enter_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exit_ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dwell_seconds", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_dwell_events_zone_id", "dwell_events", ["zone_id"])
    op.create_index("ix_dwell_events_track_id", "dwell_events", ["track_id"])
    op.create_index("ix_dwell_events_zone_enter", "dwell_events", ["zone_id", "enter_ts"])

    op.create_table(
        "queue_metrics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("zone_id", sa.String(length=64), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("queue_length", sa.Integer(), nullable=False),
        sa.Column("estimated_wait", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_queue_metrics_zone_id", "queue_metrics", ["zone_id"])
    op.create_index("ix_queue_metrics_timestamp", "queue_metrics", ["timestamp"])
    op.create_index("ix_queue_metrics_zone_timestamp", "queue_metrics", ["zone_id", "timestamp"])

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("alert_type", sa.String(length=64), nullable=False),
        sa.Column("camera_id", sa.String(length=64), nullable=True),
        sa.Column("zone_id", sa.String(length=64), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), server_default="{}", nullable=False),
        sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_alert_type", "alerts", ["alert_type"])
    op.create_index("ix_alerts_camera_id", "alerts", ["camera_id"])
    op.create_index("ix_alerts_zone_id", "alerts", ["zone_id"])
    op.create_index("ix_alerts_timestamp", "alerts", ["timestamp"])


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("queue_metrics")
    op.drop_table("dwell_events")
    op.drop_table("zone_metrics")
    op.drop_table("occupancy_metrics")
    op.drop_table("visitor_metrics")
    op.drop_table("events")
    op.drop_table("tracks")
    op.drop_table("counting_lines")
    op.drop_table("zones")
    op.drop_table("cameras")
    op.drop_table("users")
    op.drop_table("stores")
    op.drop_table("organizations")
