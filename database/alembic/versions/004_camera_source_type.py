"""Add camera source_type and last_processed_at for recorded-video cameras."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "004_camera_source_type"
down_revision: Union[str, None] = "003_module_12_5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("cameras", "source_type"):
        op.add_column(
            "cameras",
            sa.Column(
                "source_type",
                sa.String(length=16),
                nullable=False,
                server_default="live",
            ),
        )
    if not _has_column("cameras", "last_processed_at"):
        op.add_column(
            "cameras",
            sa.Column("last_processed_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    if _has_column("cameras", "last_processed_at"):
        op.drop_column("cameras", "last_processed_at")
    if _has_column("cameras", "source_type"):
        op.drop_column("cameras", "source_type")
