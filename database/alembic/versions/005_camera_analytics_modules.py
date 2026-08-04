"""Add per-camera analytics_modules (PRD §8)."""

from __future__ import annotations

import json
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text

revision: str = "005_camera_analytics_modules"
down_revision: Union[str, None] = "004_camera_source_type"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

QUEUE_ZONE_TYPES = frozenset({"queue", "checkout", "waiting"})


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in inspect(op.get_bind()).get_columns(table)}


def _infer_modules(has_line: bool, zone_types: list[str]) -> list[str]:
    inferred: set[str] = set()
    types = {t.lower() for t in zone_types}

    if has_line:
        inferred.add("entry_exit")
        inferred.add("occupancy")

    if types:
        inferred.add("zones")
        inferred.add("dwell")
        inferred.add("heatmap")

    if types & QUEUE_ZONE_TYPES:
        inferred.add("queues")

    return sorted(inferred)


def upgrade() -> None:
    if not _has_column("cameras", "analytics_modules"):
        op.add_column(
            "cameras",
            sa.Column(
                "analytics_modules",
                sa.dialects.postgresql.JSONB(),
                nullable=False,
                server_default="[]",
            ),
        )

    bind = op.get_bind()
    cameras = bind.execute(text("SELECT id FROM cameras")).fetchall()

    for (camera_id,) in cameras:
        has_line = bind.execute(
            text("SELECT 1 FROM counting_lines WHERE camera_id = :cid LIMIT 1"),
            {"cid": camera_id},
        ).first() is not None

        zone_rows = bind.execute(
            text(
                "SELECT zone_type FROM zones "
                "WHERE camera_id = :cid AND analytics_enabled = true"
            ),
            {"cid": camera_id},
        ).fetchall()
        zone_types = [row[0] for row in zone_rows if row[0]]

        modules = _infer_modules(has_line, zone_types)
        bind.execute(
            text("UPDATE cameras SET analytics_modules = :mods WHERE id = :cid"),
            {"mods": json.dumps(modules), "cid": camera_id},
        )


def downgrade() -> None:
    if _has_column("cameras", "analytics_modules"):
        op.drop_column("cameras", "analytics_modules")
