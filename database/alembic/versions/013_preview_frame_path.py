"""Add preview_frame_path to processing_runs for recorded-camera snapshots."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "013_preview_frame_path"
down_revision: Union[str, None] = "012_zone_line_soft_delete"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("processing_runs", "preview_frame_path"):
        op.add_column(
            "processing_runs",
            sa.Column("preview_frame_path", sa.String(length=1024), nullable=True),
        )


def downgrade() -> None:
    if _has_column("processing_runs", "preview_frame_path"):
        op.drop_column("processing_runs", "preview_frame_path")
