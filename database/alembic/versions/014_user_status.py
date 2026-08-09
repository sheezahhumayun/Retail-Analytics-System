"""Add status column to users for admin disable/reactivate."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "014_user_status"
down_revision: Union[str, None] = "013_preview_frame_path"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("users", "status"):
        op.add_column(
            "users",
            sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        )


def downgrade() -> None:
    if _has_column("users", "status"):
        op.drop_column("users", "status")
