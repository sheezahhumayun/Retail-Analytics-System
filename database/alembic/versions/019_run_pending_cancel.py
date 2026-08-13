"""Add pending/cancel fields to processing_runs for inference poller."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "019_run_pending_cancel"
down_revision: Union[str, None] = "018_timestamptz_datetime_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def _has_index(table: str, index: str) -> bool:
    return index in {i["name"] for i in inspect(op.get_bind()).get_indexes(table)}


def upgrade() -> None:
    if not _has_column("processing_runs", "cancel_requested"):
        op.add_column(
            "processing_runs",
            sa.Column(
                "cancel_requested",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
        op.alter_column("processing_runs", "cancel_requested", server_default=None)

    if not _has_column("processing_runs", "recording_start"):
        op.add_column(
            "processing_runs",
            sa.Column("recording_start", sa.String(length=64), nullable=True),
        )

    if _has_index("processing_runs", "uq_processing_runs_one_running_per_camera"):
        op.drop_index(
            "uq_processing_runs_one_running_per_camera",
            table_name="processing_runs",
        )

    if not _has_index("processing_runs", "uq_processing_runs_one_active_per_camera"):
        op.create_index(
            "uq_processing_runs_one_active_per_camera",
            "processing_runs",
            ["camera_id"],
            unique=True,
            postgresql_where=sa.text("status IN ('running', 'pending')"),
        )


def downgrade() -> None:
    if _has_index("processing_runs", "uq_processing_runs_one_active_per_camera"):
        op.drop_index(
            "uq_processing_runs_one_active_per_camera",
            table_name="processing_runs",
        )

    if not _has_index("processing_runs", "uq_processing_runs_one_running_per_camera"):
        op.create_index(
            "uq_processing_runs_one_running_per_camera",
            "processing_runs",
            ["camera_id"],
            unique=True,
            postgresql_where=sa.text("status = 'running'"),
        )

    if _has_column("processing_runs", "recording_start"):
        op.drop_column("processing_runs", "recording_start")

    if _has_column("processing_runs", "cancel_requested"):
        op.drop_column("processing_runs", "cancel_requested")
