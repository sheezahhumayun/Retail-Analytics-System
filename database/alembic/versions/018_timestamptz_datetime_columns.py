"""Normalize datetime columns to timestamp with time zone."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "018_timestamptz_datetime_columns"
down_revision: Union[str, None] = "017_organization_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TIMESTAMPTZ_COLUMNS: tuple[tuple[str, str, bool], ...] = (
    ("processing_runs", "started_at", False),
    ("processing_runs", "finished_at", True),
    ("zone_shapes", "created_at", False),
    ("alert_rules", "created_at", False),
    ("alert_rules", "updated_at", False),
)


def _column_data_type(table: str, column: str) -> str | None:
    row = (
        op.get_bind()
        .execute(
            sa.text(
                """
                SELECT data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table_name
                  AND column_name = :column_name
                """
            ),
            {"table_name": table, "column_name": column},
        )
        .first()
    )
    return row[0] if row is not None else None


def _upgrade_datetime_to_timestamptz(table: str, column: str, *, nullable: bool) -> None:
    if _column_data_type(table, column) != "timestamp without time zone":
        return
    op.alter_column(
        table,
        column,
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=nullable,
        postgresql_using=f"{column} AT TIME ZONE 'UTC'",
    )


def _downgrade_timestamptz_to_naive(table: str, column: str, *, nullable: bool) -> None:
    if _column_data_type(table, column) != "timestamp with time zone":
        return
    op.alter_column(
        table,
        column,
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        existing_nullable=nullable,
        postgresql_using=f"{column} AT TIME ZONE 'UTC'",
    )


def upgrade() -> None:
    for table, column, nullable in _TIMESTAMPTZ_COLUMNS:
        _upgrade_datetime_to_timestamptz(table, column, nullable=nullable)


def downgrade() -> None:
    for table, column, nullable in reversed(_TIMESTAMPTZ_COLUMNS):
        _downgrade_timestamptz_to_naive(table, column, nullable=nullable)
