"""Seed org-wide CAMERA_OFFLINE_DURATION alert rule default."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010_camera_offline_dur"
down_revision: Union[str, None] = "009_camera_status_changed_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 300s = 5 min — two full 120s health polls plus margin so duration breaches are
# detectable reliably (thresholds under ~150s can miss the first outage window).
DEFAULT_THRESHOLD_SECONDS = 300.0


def upgrade() -> None:
    now = datetime.now(timezone.utc)
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO alert_rules (
                rule_type, store_id, zone_id, camera_id,
                threshold, severity, enabled, created_at, updated_at
            )
            VALUES (
                'CAMERA_OFFLINE_DURATION', NULL, NULL, NULL,
                :threshold, 'critical', true, :now, :now
            )
            """
        ),
        {"now": now, "threshold": DEFAULT_THRESHOLD_SECONDS},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM alert_rules
            WHERE rule_type = 'CAMERA_OFFLINE_DURATION'
              AND store_id IS NULL
              AND zone_id IS NULL
              AND camera_id IS NULL
            """
        ),
    )
