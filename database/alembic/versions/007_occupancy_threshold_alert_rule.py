"""Seed OCCUPANCY_THRESHOLD org-wide alert rule (Module 15, Phase 3)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007_occupancy_alert"
down_revision: Union[str, None] = "006_alert_rules"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Insert org-wide OCCUPANCY_THRESHOLD default (placeholder threshold=30)."""
    now = datetime.now(timezone.utc)
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO alert_rules (rule_type, store_id, zone_id, threshold, severity, enabled, created_at, updated_at)
            VALUES ('OCCUPANCY_THRESHOLD', NULL, NULL, 30, 'warning', true, :now, :now)
            """
        ),
        {"now": now},
    )


def downgrade() -> None:
    """Remove OCCUPANCY_THRESHOLD org-wide default."""
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM alert_rules
            WHERE rule_type = 'OCCUPANCY_THRESHOLD'
              AND store_id IS NULL
              AND zone_id IS NULL
            """
        )
    )
