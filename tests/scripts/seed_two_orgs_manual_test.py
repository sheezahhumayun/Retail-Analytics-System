#!/usr/bin/env python
"""One-off manual-test seed — two isolated organizations (NOT wired into the app).

Creates org A / org B each with one store, camera, zone, and admin user, then prints
IDs for copy-paste API testing.

Usage (from repo root, Postgres running, migrations applied):

    set DATABASE_URL=postgresql+psycopg2://retail:retail@localhost:5433/retail_analytics
    backend\\.venv\\Scripts\\python.exe tests/scripts/seed_two_orgs_manual_test.py

Re-running is idempotent (merge/upsert on fixed IDs).
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from analytics.modules import infer_default_modules  # noqa: E402
from backend.app.services.passwords import hash_password  # noqa: E402
from database.models import (  # noqa: E402
    Camera,
    Organization,
    Store,
    User,
    Zone,
    ZoneShape,
)
from database.session import session_scope  # noqa: E402
from sqlmodel import col, select  # noqa: E402

ORG_A_ID = "org_test_a"
ORG_B_ID = "org_test_b"
STORE_A_ID = "store_test_a1"
STORE_B_ID = "store_test_b1"
CAMERA_A_ID = "cam_test_a1"
CAMERA_B_ID = "cam_test_b1"
ZONE_A_ID = "zone_test_a1"
ZONE_B_ID = "zone_test_b1"
USER_A_ID = "user_test_a_admin"
USER_B_ID = "user_test_b_admin"
ADMIN_A_EMAIL = "admin_a@test.local"
ADMIN_B_EMAIL = "admin_b@test.local"
ADMIN_PASSWORD = "testpass123"

_POLYGON = [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]]
_NOW = datetime.now(timezone.utc)


def _upsert_org_bundle(
    session,
    *,
    org_id: str,
    org_name: str,
    store_id: str,
    store_name: str,
    camera_id: str,
    camera_name: str,
    rtsp_url: str,
    zone_id: str,
    zone_name: str,
    user_id: str,
    user_email: str,
) -> None:
    session.merge(Organization(id=org_id, name=org_name))
    session.merge(
        Store(
            id=store_id,
            org_id=org_id,
            name=store_name,
            address=f"100 {store_name} St",
        )
    )
    session.merge(
        User(
            id=user_id,
            org_id=org_id,
            name=f"{org_name} Admin",
            email=user_email,
            role="admin",
            password_hash=hash_password(ADMIN_PASSWORD),
            status="active",
        )
    )
    session.merge(
        Camera(
            id=camera_id,
            store_id=store_id,
            name=camera_name,
            location="Manual test",
            rtsp_url=rtsp_url,
            source_type="live",
            camera_type="fixed",
            resolution="640x360",
            fps=10.0,
            status="online",
        )
    )
    session.merge(
        ZoneShape(
            id=zone_id,
            camera_id=camera_id,
            name=zone_name,
            shape_type="general",
            polygon_points=_POLYGON,
            created_at=_NOW,
            status="offline",
        )
    )
    session.merge(
        Zone(
            id=zone_id,
            camera_id=camera_id,
            name=zone_name,
            polygon_coords=_POLYGON,
            zone_type="general",
            analytics_enabled=True,
            status="offline",
        )
    )
    session.flush()

    camera = session.get(Camera, camera_id)
    if camera is not None:
        camera.analytics_modules = infer_default_modules(
            has_counting_line=False,
            zone_types=["general"],
        )
        session.add(camera)


def seed_two_orgs() -> None:
    with session_scope() as session:
        _upsert_org_bundle(
            session,
            org_id=ORG_A_ID,
            org_name="Test Org A",
            store_id=STORE_A_ID,
            store_name="Store A1",
            camera_id=CAMERA_A_ID,
            camera_name="Camera A1",
            rtsp_url="sample-data/entrance.mp4",
            zone_id=ZONE_A_ID,
            zone_name="Zone A1",
            user_id=USER_A_ID,
            user_email=ADMIN_A_EMAIL,
        )
        _upsert_org_bundle(
            session,
            org_id=ORG_B_ID,
            org_name="Test Org B",
            store_id=STORE_B_ID,
            store_name="Store B1",
            camera_id=CAMERA_B_ID,
            camera_name="Camera B1",
            rtsp_url="sample-data/shop.mp4",
            zone_id=ZONE_B_ID,
            zone_name="Zone B1",
            user_id=USER_B_ID,
            user_email=ADMIN_B_EMAIL,
        )
        session.commit()


def _count_for_org(session, model, org_id: str, *, via_store: bool = False) -> int:
    if model is Organization:
        return len(session.exec(select(Organization).where(Organization.id == org_id)).all())
    if via_store:
        store_ids = select(Store.id).where(Store.org_id == org_id)
        if model is Store:
            return len(session.exec(select(Store).where(Store.org_id == org_id)).all())
        if model is Camera:
            return len(
                session.exec(select(Camera).where(col(Camera.store_id).in_(store_ids))).all()
            )
        if model is Zone:
            camera_ids = select(Camera.id).where(col(Camera.store_id).in_(store_ids))
            return len(session.exec(select(Zone).where(col(Zone.camera_id).in_(camera_ids))).all())
        if model is ZoneShape:
            camera_ids = select(Camera.id).where(col(Camera.store_id).in_(store_ids))
            return len(
                session.exec(select(ZoneShape).where(col(ZoneShape.camera_id).in_(camera_ids))).all()
            )
    if model is User:
        return len(session.exec(select(User).where(User.org_id == org_id)).all())
    raise ValueError(f"unsupported count model: {model}")


def verify_and_print() -> None:
    org_ids = (ORG_A_ID, ORG_B_ID)
    rows: list[tuple[str, str, str, int]] = []

    with session_scope() as session:
        for org_id, label in ((ORG_A_ID, "Org A"), (ORG_B_ID, "Org B")):
            rows.append((label, "organizations", org_id, _count_for_org(session, Organization, org_id)))
            rows.append((label, "stores", org_id, _count_for_org(session, Store, org_id, via_store=True)))
            rows.append((label, "users", org_id, _count_for_org(session, User, org_id)))
            rows.append((label, "cameras", org_id, _count_for_org(session, Camera, org_id, via_store=True)))
            rows.append((label, "zones", org_id, _count_for_org(session, Zone, org_id, via_store=True)))
            rows.append(
                (label, "zone_shapes", org_id, _count_for_org(session, ZoneShape, org_id, via_store=True))
            )

        print("\n=== Verification (row counts per org) ===")
        print(f"{'Org':<8} {'Entity':<14} {'Org ID':<14} {'Count':>5}")
        print("-" * 48)
        for org_label, entity, oid, count in rows:
            print(f"{org_label:<8} {entity:<14} {oid:<14} {count:>5}")

        ok = all(count >= 1 for _, entity, _, count in rows if entity != "organizations")
        ok = ok and all(
            count == 1 for _, entity, _, count in rows if entity == "organizations"
        )
        if not ok:
            print("\nERROR: expected at least 1 row per entity per org (exactly 1 organization each).")
            sys.exit(1)
        print("\nOK: both orgs have expected rows.")

    print("\n=== Manual test IDs (copy for API calls) ===")
    print(f"{'Field':<22} {'Org A':<28} {'Org B':<28}")
    print("-" * 80)
    table = [
        ("org_id", ORG_A_ID, ORG_B_ID),
        ("store_id", STORE_A_ID, STORE_B_ID),
        ("camera_id", CAMERA_A_ID, CAMERA_B_ID),
        ("zone_id", ZONE_A_ID, ZONE_B_ID),
        ("admin_email", ADMIN_A_EMAIL, ADMIN_B_EMAIL),
        ("admin_password", ADMIN_PASSWORD, ADMIN_PASSWORD),
    ]
    for field, a, b in table:
        print(f"{field:<22} {a:<28} {b:<28}")
    print("\nLogin: POST /api/auth/login  {\"email\": \"<admin_email>\", \"password\": \"testpass123\"}")


def main() -> None:
    print("Seeding two manual-test organizations...")
    seed_two_orgs()
    print("Seed complete.")
    verify_and_print()


if __name__ == "__main__":
    main()
