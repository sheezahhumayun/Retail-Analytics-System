#!/usr/bin/env python
"""Throwaway verification for Phase 2 Part A — cascade delete + toggle blocks."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import and_, or_, text  # noqa: E402
from sqlmodel import col, select  # noqa: E402

from analytics.modules import infer_default_modules  # noqa: E402
from backend.app.main import app  # noqa: E402
from backend.app.services.passwords import hash_password  # noqa: E402
from database.models import (  # noqa: E402
    Alert,
    AlertRule,
    Camera,
    CountingLine,
    DwellEventRow,
    Event,
    OccupancyMetric,
    Organization,
    ProcessingRun,
    QueueMetric,
    Store,
    Superadmin,
    Track,
    User,
    VisitorMetric,
    Zone,
    ZoneMetric,
    ZoneShape,
)
from database.session import session_scope  # noqa: E402

ORG_ID = "org_cascade_verify"
STORE_ID = "store_cascade_verify"
CAMERA_ID = "cam_cascade_verify"
ZONE_ID = "zone_cascade_verify"
USER_ID = "user_cascade_verify"
USER_EMAIL = "cascade_verify@test.local"
USER_PASSWORD = "cascade-verify-pass"
SUPERADMIN_EMAIL = "superadmin@test.local"
SUPERADMIN_PASSWORD = "superadmin-test-pass"
RECORDED_ORG_ID = "org_toggle_verify"
RECORDED_STORE_ID = "store_toggle_verify"
RECORDED_CAMERA_ID = "cam_toggle_recorded"
RECORDED_USER_EMAIL = "toggle_verify@test.local"
RECORDED_USER_PASSWORD = "toggle-verify-pass"
_POLYGON = [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]]
_NOW = datetime.now(timezone.utc)
_VIDEO = "sample-data/entrance.mp4"


def _ensure_superadmin(session) -> None:
    session.merge(
        Superadmin(
            id="superadmin_test",
            name="Manual Test Superadmin",
            email=SUPERADMIN_EMAIL,
            password_hash=hash_password(SUPERADMIN_PASSWORD),
            status="active",
        )
    )


def _seed_cascade_org(session) -> None:
    session.merge(Organization(id=ORG_ID, name="Cascade Verify Org", status="active"))
    session.merge(
        Store(id=STORE_ID, org_id=ORG_ID, name="Cascade Store", address="1 Cascade St")
    )
    session.merge(
        User(
            id=USER_ID,
            org_id=ORG_ID,
            name="Cascade Admin",
            email=USER_EMAIL,
            role="admin",
            password_hash=hash_password(USER_PASSWORD),
            status="active",
        )
    )
    session.merge(
        Camera(
            id=CAMERA_ID,
            store_id=STORE_ID,
            name="Cascade Camera",
            location="Verify",
            rtsp_url=_VIDEO,
            source_type="recorded",
            camera_type="fixed",
            resolution="640x360",
            fps=10.0,
            status="offline",
            analytics_modules=infer_default_modules(has_counting_line=False, zone_types=["general"]),
        )
    )
    session.merge(
        ZoneShape(
            id=ZONE_ID,
            camera_id=CAMERA_ID,
            name="Cascade Zone Shape",
            shape_type="general",
            polygon_points=_POLYGON,
            created_at=_NOW,
            status="offline",
        )
    )
    session.merge(
        Zone(
            id=ZONE_ID,
            camera_id=CAMERA_ID,
            name="Cascade Zone",
            polygon_coords=_POLYGON,
            zone_type="general",
            analytics_enabled=True,
            status="offline",
        )
    )
    session.flush()
    session.add(
        Event(
            camera_id=CAMERA_ID,
            zone_id=ZONE_ID,
            track_id="track_verify_1",
            event_type="zone_enter",
            timestamp=_NOW,
            metadata_={},
        )
    )
    session.add(
        Alert(
            alert_type="DWELL_THRESHOLD",
            camera_id=CAMERA_ID,
            zone_id=ZONE_ID,
            timestamp=_NOW,
            severity="warning",
            status="open",
            metadata_={"store_id": STORE_ID},
        )
    )
    session.add(
        AlertRule(
            org_id=ORG_ID,
            rule_type="DWELL_THRESHOLD",
            store_id=STORE_ID,
            zone_id=ZONE_ID,
            camera_id=CAMERA_ID,
            threshold=60.0,
            severity="warning",
            enabled=True,
        )
    )


def _seed_toggle_org(session) -> None:
    session.merge(Organization(id=RECORDED_ORG_ID, name="Toggle Verify Org", status="active"))
    session.merge(
        Store(
            id=RECORDED_STORE_ID,
            org_id=RECORDED_ORG_ID,
            name="Toggle Store",
            address="2 Toggle St",
        )
    )
    session.merge(
        User(
            id="user_toggle_verify",
            org_id=RECORDED_ORG_ID,
            name="Toggle Admin",
            email=RECORDED_USER_EMAIL,
            role="admin",
            password_hash=hash_password(RECORDED_USER_PASSWORD),
            status="active",
        )
    )
    session.merge(
        Camera(
            id=RECORDED_CAMERA_ID,
            store_id=RECORDED_STORE_ID,
            name="Toggle Recorded Camera",
            location="Verify",
            rtsp_url=_VIDEO,
            source_type="recorded",
            camera_type="fixed",
            resolution="640x360",
            fps=10.0,
            status="offline",
            analytics_modules=infer_default_modules(has_counting_line=False, zone_types=["general"]),
        )
    )


def _counts_for_org(session, org_id: str) -> dict[str, int]:
    store_ids = select(Store.id).where(Store.org_id == org_id)
    camera_ids = (
        select(Camera.id)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
    )
    zone_ids = (
        select(Zone.id)
        .join(Camera, Zone.camera_id == Camera.id)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
    )
    metadata_store_id = Alert.metadata_["store_id"].as_string()
    return {
        "organizations": len(session.exec(select(Organization).where(Organization.id == org_id)).all()),
        "stores": len(session.exec(select(Store).where(Store.org_id == org_id)).all()),
        "users": len(session.exec(select(User).where(User.org_id == org_id)).all()),
        "cameras": len(session.exec(select(Camera).where(col(Camera.store_id).in_(store_ids))).all()),
        "zone_shapes": len(
            session.exec(select(ZoneShape).where(col(ZoneShape.camera_id).in_(camera_ids))).all()
        ),
        "zones": len(session.exec(select(Zone).where(col(Zone.camera_id).in_(camera_ids))).all()),
        "counting_lines": len(
            session.exec(select(CountingLine).where(col(CountingLine.camera_id).in_(camera_ids))).all()
        ),
        "processing_runs": len(
            session.exec(select(ProcessingRun).where(col(ProcessingRun.camera_id).in_(camera_ids))).all()
        ),
        "events": len(
            session.exec(
                select(Event).where(
                    or_(
                        col(Event.camera_id).in_(camera_ids),
                        col(Event.zone_id).in_(zone_ids),
                    )
                )
            ).all()
        ),
        "alerts": len(
            session.exec(
                select(Alert).where(
                    or_(
                        col(Alert.camera_id).in_(camera_ids),
                        col(Alert.zone_id).in_(zone_ids),
                        and_(
                            Alert.camera_id.is_(None),  # type: ignore[union-attr]
                            Alert.zone_id.is_(None),  # type: ignore[union-attr]
                            metadata_store_id.in_(store_ids),
                        ),
                    )
                )
            ).all()
        ),
        "alert_rules": len(
            session.exec(
                select(AlertRule).where(
                    or_(
                        AlertRule.org_id == org_id,
                        col(AlertRule.store_id).in_(store_ids),
                        col(AlertRule.zone_id).in_(zone_ids),
                        col(AlertRule.camera_id).in_(camera_ids),
                    )
                )
            ).all()
        ),
        "dwell_events": len(
            session.exec(select(DwellEventRow).where(col(DwellEventRow.zone_id).in_(zone_ids))).all()
        ),
        "zone_metrics": len(
            session.exec(select(ZoneMetric).where(col(ZoneMetric.zone_id).in_(zone_ids))).all()
        ),
        "queue_metrics": len(
            session.exec(select(QueueMetric).where(col(QueueMetric.zone_id).in_(zone_ids))).all()
        ),
        "tracks": len(session.exec(select(Track).where(col(Track.camera_id).in_(camera_ids))).all()),
        "visitor_metrics": len(
            session.exec(select(VisitorMetric).where(col(VisitorMetric.store_id).in_(store_ids))).all()
        ),
        "occupancy_metrics": len(
            session.exec(
                select(OccupancyMetric).where(
                    or_(
                        col(OccupancyMetric.store_id).in_(store_ids),
                        col(OccupancyMetric.camera_id).in_(camera_ids),
                    )
                )
            ).all()
        ),
    }


def _print_counts(label: str, counts: dict[str, int]) -> None:
    print(f"\n=== {label} ===")
    for table, count in counts.items():
        print(f"{table:20} {count}")


def _superadmin_headers(client: TestClient) -> dict[str, str]:
    login = client.post(
        "/api/auth/login",
        json={"email": SUPERADMIN_EMAIL, "password": SUPERADMIN_PASSWORD},
    )
    print("\n--- superadmin login ---")
    print(f"status={login.status_code}")
    print(login.text)
    login.raise_for_status()
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def verify_cascade_delete(client: TestClient, headers: dict[str, str]) -> None:
    with session_scope() as session:
        _ensure_superadmin(session)
        _seed_cascade_org(session)
        session.commit()

    with session_scope() as session:
        before = _counts_for_org(session, ORG_ID)
    _print_counts(f"BEFORE DELETE counts for {ORG_ID}", before)

    delete = client.request(
        "DELETE",
        f"/api/organizations/{ORG_ID}",
        headers=headers,
        json={"confirm": ORG_ID},
    )
    print("\n--- DELETE /api/organizations/{org_id} ---")
    print(f"status={delete.status_code}")
    print(delete.text)

    with session_scope() as session:
        after = _counts_for_org(session, ORG_ID)
    _print_counts(f"AFTER DELETE counts for {ORG_ID}", after)


def verify_toggle_blocks(client: TestClient, headers: dict[str, str]) -> None:
    with session_scope() as session:
        _ensure_superadmin(session)
        _seed_toggle_org(session)
        session.commit()

    def org_admin_login() -> dict:
        resp = client.post(
            "/api/auth/login",
            json={"email": RECORDED_USER_EMAIL, "password": RECORDED_USER_PASSWORD},
        )
        print("\n--- org admin login ---")
        print(f"status={resp.status_code}")
        print(resp.text)
        return resp

    def org_admin_process(admin_headers: dict[str, str]) -> None:
        resp = client.post(
            f"/api/cameras/{RECORDED_CAMERA_ID}/process",
            headers=admin_headers,
        )
        print("\n--- POST /api/cameras/{camera_id}/process ---")
        print(f"status={resp.status_code}")
        print(resp.text)

    login_active = org_admin_login()
    assert login_active.status_code == 200, login_active.text
    org_admin_process({"Authorization": f"Bearer {login_active.json()['access_token']}"})

    disable = client.post(f"/api/organizations/{RECORDED_ORG_ID}/toggle", headers=headers)
    print("\n--- POST toggle (disable) ---")
    print(f"status={disable.status_code}")
    print(disable.text)

    login_disabled = org_admin_login()
    org_admin_process(
        {"Authorization": f"Bearer {login_disabled.json()['access_token']}"}
        if login_disabled.status_code == 200
        else {}
    )

    enable = client.post(f"/api/organizations/{RECORDED_ORG_ID}/toggle", headers=headers)
    print("\n--- POST toggle (re-enable) ---")
    print(f"status={enable.status_code}")
    print(enable.text)

    login_reenabled = org_admin_login()
    org_admin_process(
        {"Authorization": f"Bearer {login_reenabled.json()['access_token']}"}
        if login_reenabled.status_code == 200
        else {}
    )


def main() -> None:
    client = TestClient(app)
    try:
        headers = _superadmin_headers(client)
        print("\n################ ITEM 2: CASCADE DELETE ################")
        verify_cascade_delete(client, headers)
        print("\n################ ITEM 3: TOGGLE + BLOCKS ################")
        verify_toggle_blocks(client, headers)
    finally:
        client.close()


if __name__ == "__main__":
    main()
