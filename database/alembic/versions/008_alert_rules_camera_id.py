"""Add camera_id to alert_rules for per-camera threshold overrides."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "008_alert_rules_camera_id"
down_revision: Union[str, None] = "007_occupancy_alert"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def upgrade() -> None:
    if not _has_column("alert_rules", "camera_id"):
        op.add_column(
            "alert_rules",
            sa.Column("camera_id", sa.String(length=64), nullable=True),
        )
        op.create_foreign_key(
            "fk_alert_rules_camera_id",
            "alert_rules",
            "cameras",
            ["camera_id"],
            ["id"],
        )
        op.create_index("ix_alert_rules_camera_id", "alert_rules", ["camera_id"])


def downgrade() -> None:
    if _has_column("alert_rules", "camera_id"):
        op.drop_index("ix_alert_rules_camera_id", table_name="alert_rules")
        op.drop_constraint("fk_alert_rules_camera_id", "alert_rules", type_="foreignkey")
        op.drop_column("alert_rules", "camera_id")
