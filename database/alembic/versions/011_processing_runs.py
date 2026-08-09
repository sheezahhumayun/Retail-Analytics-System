"""Add processing_runs table for recorded-video job history."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "011_processing_runs"
down_revision: Union[str, None] = "010_camera_offline_dur"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_index(table: str, index: str) -> bool:
    return index in {i["name"] for i in inspect(op.get_bind()).get_indexes(table)}


def upgrade() -> None:
    if not _has_table("processing_runs"):
        op.create_table(
            "processing_runs",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("camera_id", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("message", sa.Text(), nullable=True),
            sa.Column("source_path", sa.String(length=1024), nullable=False),
            sa.Column(
                "zones_snapshot",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default="[]",
            ),
            sa.Column(
                "lines_snapshot",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default="[]",
            ),
            sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.alter_column("processing_runs", "zones_snapshot", server_default=None)
        op.alter_column("processing_runs", "lines_snapshot", server_default=None)

    if not _has_index("processing_runs", "ix_processing_runs_camera_id"):
        op.create_index("ix_processing_runs_camera_id", "processing_runs", ["camera_id"])
    if not _has_index("processing_runs", "ix_processing_runs_started_at"):
        op.create_index("ix_processing_runs_started_at", "processing_runs", ["started_at"])

    # Partial unique index: one running job per camera (Postgres-specific DDL).
    if not _has_index("processing_runs", "uq_processing_runs_one_running_per_camera"):
        op.create_index(
            "uq_processing_runs_one_running_per_camera",
            "processing_runs",
            ["camera_id"],
            unique=True,
            postgresql_where=sa.text("status = 'running'"),
        )


def downgrade() -> None:
    if _has_index("processing_runs", "uq_processing_runs_one_running_per_camera"):
        op.drop_index(
            "uq_processing_runs_one_running_per_camera",
            table_name="processing_runs",
        )
    if _has_index("processing_runs", "ix_processing_runs_started_at"):
        op.drop_index("ix_processing_runs_started_at", table_name="processing_runs")
    if _has_index("processing_runs", "ix_processing_runs_camera_id"):
        op.drop_index("ix_processing_runs_camera_id", table_name="processing_runs")
    if _has_table("processing_runs"):
        op.drop_table("processing_runs")
