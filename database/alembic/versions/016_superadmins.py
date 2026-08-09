"""Add superadmins table for platform-level accounts."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "016_superadmins"
down_revision: Union[str, None] = "015_alert_rules_org_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return name in inspect(op.get_bind()).get_table_names()


def _has_index(table: str, index: str) -> bool:
    return index in {i["name"] for i in inspect(op.get_bind()).get_indexes(table)}


def upgrade() -> None:
    if not _has_table("superadmins"):
        op.create_table(
            "superadmins",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column(
                "status",
                sa.String(length=32),
                nullable=False,
                server_default="active",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.alter_column("superadmins", "status", server_default=None)

    if not _has_index("superadmins", "ix_superadmins_email"):
        op.create_index("ix_superadmins_email", "superadmins", ["email"], unique=True)


def downgrade() -> None:
    if _has_index("superadmins", "ix_superadmins_email"):
        op.drop_index("ix_superadmins_email", table_name="superadmins")
    if _has_table("superadmins"):
        op.drop_table("superadmins")
