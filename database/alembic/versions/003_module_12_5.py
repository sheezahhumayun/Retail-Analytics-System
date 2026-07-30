"""Module 12.5 schema: zone_shapes, counting_lines columns, user admin fields."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

revision: str = "003_module_12_5"
down_revision: Union[str, None] = "002_normalize_user_roles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _insp():
    return inspect(op.get_bind())


def _has_table(name: str) -> bool:
    return name in _insp().get_table_names()


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in _insp().get_columns(table)}


def _has_index(table: str, index: str) -> bool:
    return index in {i["name"] for i in _insp().get_indexes(table)}


def _has_fk(table: str, fk_name: str) -> bool:
    return fk_name in {fk["name"] for fk in _insp().get_foreign_keys(table) if fk["name"]}


def upgrade() -> None:
    # Dev DBs may already have these objects from SQLModel create_all() before Alembic runs.
    if not _has_table("zone_shapes"):
        op.create_table(
            "zone_shapes",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("camera_id", sa.String(length=64), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("type", sa.String(length=64), nullable=False),
            sa.Column("polygon_points", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["camera_id"], ["cameras.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("zone_shapes", "ix_zone_shapes_camera_id"):
        op.create_index("ix_zone_shapes_camera_id", "zone_shapes", ["camera_id"])
    if not _has_index("zone_shapes", "ix_zone_shapes_created_at"):
        op.create_index("ix_zone_shapes_created_at", "zone_shapes", ["created_at"])

    if not _has_column("counting_lines", "name"):
        op.add_column(
            "counting_lines",
            sa.Column("name", sa.String(length=255), server_default="main", nullable=False),
        )
        op.alter_column("counting_lines", "name", server_default=None)
    if not _has_column("counting_lines", "created_at"):
        op.add_column(
            "counting_lines",
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("NOW()"),
                nullable=False,
            ),
        )
        op.alter_column("counting_lines", "created_at", server_default=None)

    if not _has_column("users", "store_id"):
        op.add_column("users", sa.Column("store_id", sa.String(length=64), nullable=True))
    if not _has_column("users", "password_hash"):
        op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))
    if not _has_fk("users", "fk_users_store_id"):
        op.create_foreign_key("fk_users_store_id", "users", "stores", ["store_id"], ["id"])
    if not _has_index("users", "ix_users_store_id"):
        op.create_index("ix_users_store_id", "users", ["store_id"])


def downgrade() -> None:
    if _has_index("users", "ix_users_store_id"):
        op.drop_index("ix_users_store_id", table_name="users")
    if _has_fk("users", "fk_users_store_id"):
        op.drop_constraint("fk_users_store_id", "users", type_="foreignkey")
    if _has_column("users", "password_hash"):
        op.drop_column("users", "password_hash")
    if _has_column("users", "store_id"):
        op.drop_column("users", "store_id")
    if _has_column("counting_lines", "created_at"):
        op.drop_column("counting_lines", "created_at")
    if _has_column("counting_lines", "name"):
        op.drop_column("counting_lines", "name")
    if _has_table("zone_shapes"):
        if _has_index("zone_shapes", "ix_zone_shapes_created_at"):
            op.drop_index("ix_zone_shapes_created_at", table_name="zone_shapes")
        if _has_index("zone_shapes", "ix_zone_shapes_camera_id"):
            op.drop_index("ix_zone_shapes_camera_id", table_name="zone_shapes")
        op.drop_table("zone_shapes")
