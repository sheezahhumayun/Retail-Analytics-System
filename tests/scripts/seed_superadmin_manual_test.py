#!/usr/bin/env python
"""One-off manual-test seed — platform superadmin (NOT wired into the app).

Creates a single superadmin account for manual API testing.

Usage (from repo root, Postgres running, migrations applied):

    set DATABASE_URL=postgresql+psycopg2://retail:retail@localhost:5433/retail_analytics
    backend\\.venv\\Scripts\\python.exe tests/scripts/seed_superadmin_manual_test.py

Re-running is idempotent (merge on fixed ID).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.passwords import hash_password  # noqa: E402
from database.models import Superadmin  # noqa: E402
from database.session import session_scope  # noqa: E402
from sqlmodel import select  # noqa: E402

SUPERADMIN_ID = "superadmin_test"
SUPERADMIN_EMAIL = "superadmin@test.local"
SUPERADMIN_PASSWORD = "superadmin-test-pass"
SUPERADMIN_NAME = "Manual Test Superadmin"


def seed_superadmin() -> None:
    with session_scope() as session:
        session.merge(
            Superadmin(
                id=SUPERADMIN_ID,
                name=SUPERADMIN_NAME,
                email=SUPERADMIN_EMAIL,
                password_hash=hash_password(SUPERADMIN_PASSWORD),
                status="active",
            )
        )
        session.commit()


def verify_and_print() -> None:
    with session_scope() as session:
        row = session.exec(
            select(Superadmin).where(Superadmin.email == SUPERADMIN_EMAIL)
        ).first()
        if row is None:
            print("ERROR: superadmin row not found after seed.")
            sys.exit(1)
        count = len(session.exec(select(Superadmin)).all())
        print(f"OK: superadmins table has {count} row(s).")
        print("\n=== Manual test superadmin (copy for API calls) ===")
        print(f"{'id':<22} {row.id}")
        print(f"{'email':<22} {row.email}")
        print(f"{'password':<22} {SUPERADMIN_PASSWORD}")
        print(f"{'account_type':<22} superadmin")
        print(
            "\nLogin: POST /api/auth/login  "
            f'{{"email": "{SUPERADMIN_EMAIL}", "password": "{SUPERADMIN_PASSWORD}"}}'
        )


def main() -> None:
    print("Seeding manual-test superadmin...")
    seed_superadmin()
    print("Seed complete.")
    verify_and_print()


if __name__ == "__main__":
    main()
