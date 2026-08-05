"""Add status_changed_at to cameras for offline-duration alerting."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "009_camera_status_changed_at"
down_revision: Union[str, None] = "008_alert_rules_camera_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("cameras", "status_changed_at"):
        op.add_column(
            "cameras",
            sa.Column("status_changed_at", sa.DateTime(timezone=True), nullable=True),
        )
        now = datetime.now(timezone.utc)
        conn = op.get_bind()
        conn.execute(
            sa.text(
                "UPDATE cameras SET status_changed_at = :now WHERE status_changed_at IS NULL"
            ),
            {"now": now},
        )


def downgrade() -> None:
    if _has_column("cameras", "status_changed_at"):
        op.drop_column("cameras", "status_changed_at")
