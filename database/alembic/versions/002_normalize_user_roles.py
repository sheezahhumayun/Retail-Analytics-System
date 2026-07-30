"""Normalize legacy user roles to admin | user."""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "002_normalize_user_roles"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "UPDATE users SET role = 'user' WHERE role IN ('viewer', 'manager')"
    )


def downgrade() -> None:
    # Legacy role values cannot be restored reliably.
    pass
