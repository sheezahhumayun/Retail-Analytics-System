"""Add status column to zones, zone_shapes, and counting_lines for soft delete."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "012_zone_line_soft_delete"
down_revision: Union[str, None] = "011_processing_runs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    for table in ("zones", "zone_shapes", "counting_lines"):
        if not _has_column(table, "status"):
            op.add_column(
                table,
                sa.Column("status", sa.String(length=32), nullable=False, server_default="offline"),
            )
            op.alter_column(table, "status", server_default=None)


def downgrade() -> None:
    for table in ("counting_lines", "zone_shapes", "zones"):
        if _has_column(table, "status"):
            op.drop_column(table, "status")
