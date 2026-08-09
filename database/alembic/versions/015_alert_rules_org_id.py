"""Add org_id to alert_rules for multi-tenant scoping."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "015_alert_rules_org_id"
down_revision: Union[str, None] = "014_user_status"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def _has_index(table: str, index: str) -> bool:
    return index in {i["name"] for i in inspect(op.get_bind()).get_indexes(table)}


def upgrade() -> None:
    if not _has_column("alert_rules", "org_id"):
        op.add_column(
            "alert_rules",
            sa.Column("org_id", sa.String(length=64), nullable=True),
        )
        op.create_foreign_key(
            "fk_alert_rules_org_id",
            "alert_rules",
            "organizations",
            ["org_id"],
            ["id"],
        )
        if not _has_index("alert_rules", "ix_alert_rules_org_id"):
            op.create_index("ix_alert_rules_org_id", "alert_rules", ["org_id"])

    bind = op.get_bind()

    # Derive org_id from store_id where present.
    bind.execute(
        sa.text(
            """
            UPDATE alert_rules ar
            SET org_id = s.org_id
            FROM stores s
            WHERE ar.store_id = s.id
              AND ar.org_id IS NULL
            """
        )
    )

    # Derive from zone -> camera -> store.
    bind.execute(
        sa.text(
            """
            UPDATE alert_rules ar
            SET org_id = s.org_id
            FROM zones z
            JOIN cameras c ON c.id = z.camera_id
            JOIN stores s ON s.id = c.store_id
            WHERE ar.zone_id = z.id
              AND ar.org_id IS NULL
            """
        )
    )

    # Derive from camera_id where present.
    bind.execute(
        sa.text(
            """
            UPDATE alert_rules ar
            SET org_id = s.org_id
            FROM cameras c
            JOIN stores s ON s.id = c.store_id
            WHERE ar.camera_id = c.id
              AND ar.org_id IS NULL
            """
        )
    )

    # Org-wide defaults (no store/zone/camera): single-org backfill only.
    org_count = bind.execute(sa.text("SELECT COUNT(*) FROM organizations")).scalar()
    if org_count == 1:
        sole_org_id = bind.execute(sa.text("SELECT id FROM organizations LIMIT 1")).scalar()
        if sole_org_id:
            bind.execute(
                sa.text(
                    """
                    UPDATE alert_rules
                    SET org_id = :org_id
                    WHERE org_id IS NULL
                    """
                ),
                {"org_id": sole_org_id},
            )


def downgrade() -> None:
    if _has_index("alert_rules", "ix_alert_rules_org_id"):
        op.drop_index("ix_alert_rules_org_id", table_name="alert_rules")
    if _has_column("alert_rules", "org_id"):
        op.drop_constraint("fk_alert_rules_org_id", "alert_rules", type_="foreignkey")
        op.drop_column("alert_rules", "org_id")
