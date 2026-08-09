"""Add status column to organizations for admin disable/toggle."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "017_organization_status"
down_revision: Union[str, None] = "016_superadmins"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("organizations", "status"):
        op.add_column(
            "organizations",
            sa.Column(
                "status",
                sa.String(length=32),
                nullable=False,
                server_default="active",
            ),
        )
        op.alter_column("organizations", "status", server_default=None)


def downgrade() -> None:
    if _has_column("organizations", "status"):
        op.drop_column("organizations", "status")
