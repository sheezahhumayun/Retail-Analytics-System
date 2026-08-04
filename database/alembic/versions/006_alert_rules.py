"""Add alert_rules table for configurable alert thresholds (Module 15, Phase 1)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "006_alert_rules"
down_revision: Union[str, None] = "005_camera_analytics_modules"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create alert_rules table and seed initial thresholds from current hardcoded values."""
    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rule_type", sa.String(length=64), nullable=False),
        sa.Column("store_id", sa.String(length=64), nullable=True),
        sa.Column("zone_id", sa.String(length=64), nullable=True),
        sa.Column("threshold", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False, server_default="warning"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], name="fk_alert_rules_store_id"),
        sa.ForeignKeyConstraint(["zone_id"], ["zones.id"], name="fk_alert_rules_zone_id"),
        sa.PrimaryKeyConstraint("id", name="pk_alert_rules"),
    )
    op.create_index("ix_alert_rules_rule_type", "alert_rules", ["rule_type"])
    op.create_index("ix_alert_rules_store_zone", "alert_rules", ["store_id", "zone_id", "rule_type"])
    op.create_index("ix_alert_rules_enabled", "alert_rules", ["enabled"])
    op.create_index("ix_alert_rules_created_at", "alert_rules", ["created_at"])

    # Seed initial thresholds based on documented values from analytics modules:
    # - Dwell: 60.0 seconds per zone (from analytics/dwell/README.md example)
    # - Queue Length: 5 persons per zone (from analytics/queues/README.md example)
    # - Queue Duration: 120.0 seconds per zone (from analytics/queues/README.md example)
    # All seeded with severity="warning" to match current behavior in database/writer.py
    # All seeded with enabled=true (except high_occupancy which doesn't exist yet)
    #
    # Strategy: Insert THREE TIERS of rules for fallback:
    # 1. Org-wide defaults (store_id=NULL, zone_id=NULL) — applied to all new zones/stores
    # 2. Per-zone defaults (store_id=NULL, zone_id=<id>) — created for all existing zones
    # 3. Per-store overrides (store_id=<id>, zone_id=<id>) — can be customized by admin
    #
    # Phase 2 lookup will check in order: zone-specific → store-specific → org-wide default.
    # This ensures existing zones keep their per-zone rules, but new zones auto-inherit defaults.

    now = datetime.now(timezone.utc)
    conn = op.get_bind()

    # === ORG-WIDE DEFAULTS (store_id=NULL, zone_id=NULL) ===
    # These apply to any future zone that doesn't have an explicit rule.
    conn.execute(
        sa.text(
            """
            INSERT INTO alert_rules (rule_type, store_id, zone_id, threshold, severity, enabled, created_at, updated_at)
            VALUES
              ('DWELL_THRESHOLD', NULL, NULL, 60.0, 'warning', true, :now, :now),
              ('QUEUE_THRESHOLD', NULL, NULL, 5, 'warning', true, :now, :now),
              ('QUEUE_THRESHOLD_DURATION', NULL, NULL, 120.0, 'warning', true, :now, :now)
            """
        ),
        {"now": now},
    )

    # === PER-ZONE DEFAULTS (store_id=NULL, zone_id=<existing_zone_id>) ===
    # Existing zones get explicit rules seeded so they have predictable alerting behavior
    # once Phase 2 reads from the table. Admins can override these per zone if needed.

    conn.execute(
        sa.text(
            """
            INSERT INTO alert_rules (rule_type, store_id, zone_id, threshold, severity, enabled, created_at, updated_at)
            SELECT 'DWELL_THRESHOLD', NULL, z.id, 60.0, 'warning', true, :now, :now
            FROM zones z
            WHERE z.analytics_enabled = true
            """
        ),
        {"now": now},
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO alert_rules (rule_type, store_id, zone_id, threshold, severity, enabled, created_at, updated_at)
            SELECT 'QUEUE_THRESHOLD', NULL, z.id, 5, 'warning', true, :now, :now
            FROM zones z
            WHERE z.analytics_enabled = true
              AND z.zone_type IN ('queue', 'checkout', 'waiting')
            """
        ),
        {"now": now},
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO alert_rules (rule_type, store_id, zone_id, threshold, severity, enabled, created_at, updated_at)
            SELECT 'QUEUE_THRESHOLD_DURATION', NULL, z.id, 120.0, 'warning', true, :now, :now
            FROM zones z
            WHERE z.analytics_enabled = true
              AND z.zone_type IN ('queue', 'checkout', 'waiting')
            """
        ),
        {"now": now},
    )


def downgrade() -> None:
    """Drop alert_rules table."""
    op.drop_index("ix_alert_rules_created_at", table_name="alert_rules")
    op.drop_index("ix_alert_rules_enabled", table_name="alert_rules")
    op.drop_index("ix_alert_rules_store_zone", table_name="alert_rules")
    op.drop_index("ix_alert_rules_rule_type", table_name="alert_rules")
    op.drop_table("alert_rules")
