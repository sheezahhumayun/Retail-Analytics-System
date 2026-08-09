"""Regression tests for organization-scoped API access."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from backend.app.main import app
from database.models import Alert, AlertRule, Camera, Organization, Store, User, Zone, ZoneShape
from database.seed import ORG_ID, STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope

pytestmark = [pytest.mark.api, pytest.mark.database]

OTHER_ORG_ID = "org_other"
OTHER_STORE_ID = "store_other"
OTHER_CAMERA_ID = "cam_other"
OTHER_ZONE_ID = "zone_other"
OTHER_ADMIN_EMAIL = "admin@other-retail.local"


@pytest.fixture(scope="module")
def api_client():
    try:
        create_all()
        seed_reference_data(force=True)
        _seed_other_org()
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")

    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        reset_engine()


def _seed_other_org() -> None:
    with session_scope() as session:
        session.merge(Organization(id=OTHER_ORG_ID, name="Other Retail Co"))
        session.merge(
            Store(
                id=OTHER_STORE_ID,
                org_id=OTHER_ORG_ID,
                name="Other Store",
                address="200 Other St",
            )
        )
        session.merge(
            Camera(
                id=OTHER_CAMERA_ID,
                store_id=OTHER_STORE_ID,
                name="Other Camera",
                location="Back",
                camera_type="fixed",
                status="online",
                analytics_modules=["entry_exit", "zones"],
            )
        )
        session.merge(
            Zone(
                id=OTHER_ZONE_ID,
                camera_id=OTHER_CAMERA_ID,
                name="Other Zone",
                polygon_coords=[[0, 0], [10, 0], [10, 10]],
                zone_type="general",
                analytics_enabled=True,
            )
        )
        session.merge(
            ZoneShape(
                id=OTHER_ZONE_ID,
                camera_id=OTHER_CAMERA_ID,
                name="Other Zone",
                shape_type="general",
                polygon_points=[[0, 0], [10, 0], [10, 10]],
                created_at=datetime.now(timezone.utc),
            )
        )
        session.merge(
            User(
                id="user_other_admin",
                org_id=OTHER_ORG_ID,
                name="Other Admin",
                email=OTHER_ADMIN_EMAIL,
                role="admin",
            )
        )


@pytest.fixture(scope="module")
def org_a_admin_headers(api_client: TestClient) -> dict[str, str]:
    resp = api_client.post(
        "/api/auth/login",
        json={"email": "admin@demo-retail.local", "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture(scope="module")
def org_b_admin_headers(api_client: TestClient) -> dict[str, str]:
    resp = api_client.post(
        "/api/auth/login",
        json={"email": OTHER_ADMIN_EMAIL, "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


class TestOrgIsolation:
    def test_stores_list_excludes_other_org(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.get("/api/stores", headers=org_a_admin_headers)
        assert resp.status_code == 200
        store_ids = {s["id"] for s in resp.json()}
        assert STORE_ID in store_ids
        assert OTHER_STORE_ID not in store_ids

    def test_store_post_rejects_foreign_org_id(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.post(
            "/api/stores",
            headers=org_a_admin_headers,
            json={
                "id": f"store_{uuid.uuid4().hex[:8]}",
                "org_id": OTHER_ORG_ID,
                "name": "Sneaky Store",
            },
        )
        assert resp.status_code == 404

    def test_cameras_list_excludes_other_org(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.get("/api/cameras", headers=org_a_admin_headers)
        assert resp.status_code == 200
        camera_ids = {c["id"] for c in resp.json()}
        assert OTHER_CAMERA_ID not in camera_ids

    def test_camera_status_other_org_forbidden(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.get(
            f"/api/cameras/{OTHER_CAMERA_ID}/status",
            headers=org_a_admin_headers,
        )
        assert resp.status_code == 404

    def test_zones_list_excludes_other_org(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.get("/api/zones", headers=org_a_admin_headers)
        assert resp.status_code == 200
        zone_ids = {z["id"] for z in resp.json()}
        assert OTHER_ZONE_ID not in zone_ids

    def test_zone_get_other_camera_forbidden(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.get(
            f"/api/zones?camera_id={OTHER_CAMERA_ID}",
            headers=org_a_admin_headers,
        )
        assert resp.status_code == 404

    def test_users_list_excludes_other_org(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.get("/api/users", headers=org_a_admin_headers)
        assert resp.status_code == 200
        emails = {u["email"] for u in resp.json()}
        assert OTHER_ADMIN_EMAIL not in emails

    def test_analytics_other_store_forbidden(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        resp = api_client.get(
            "/api/analytics/traffic",
            headers=org_a_admin_headers,
            params={"store_id": OTHER_STORE_ID, "from": yesterday, "to": yesterday},
        )
        assert resp.status_code == 404

    def test_org_b_sees_only_own_stores(
        self, api_client: TestClient, org_b_admin_headers: dict
    ):
        resp = api_client.get("/api/stores", headers=org_b_admin_headers)
        assert resp.status_code == 200
        store_ids = {s["id"] for s in resp.json()}
        assert OTHER_STORE_ID in store_ids
        assert STORE_ID not in store_ids


class TestSingleOrgRegression:
    def test_demo_org_stores_visible(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.get("/api/stores", headers=org_a_admin_headers)
        assert resp.status_code == 200
        assert any(s["id"] == STORE_ID for s in resp.json())

    def test_demo_cameras_visible(
        self, api_client: TestClient, org_a_admin_headers: dict
    ):
        resp = api_client.get(
            "/api/cameras",
            headers=org_a_admin_headers,
            params={"store_id": STORE_ID},
        )
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_store_level_occupancy_alert_org_scoped(
        self, api_client: TestClient, org_a_admin_headers: dict, org_b_admin_headers: dict
    ):
        with session_scope() as session:
            alert = Alert(
                alert_type="OCCUPANCY_THRESHOLD",
                camera_id=None,
                zone_id=None,
                timestamp=datetime.now(timezone.utc),
                severity="warning",
                status="open",
                metadata_={"store_id": STORE_ID, "current_occupancy": 35},
            )
            session.add(alert)
            session.flush()
            alert_id = alert.id

        listing = api_client.get("/api/alerts", headers=org_a_admin_headers)
        assert listing.status_code == 200
        assert any(a["id"] == alert_id for a in listing.json()["alerts"])

        patch_ok = api_client.patch(
            f"/api/alerts/{alert_id}",
            headers=org_a_admin_headers,
            json={"status": "acknowledged"},
        )
        assert patch_ok.status_code == 200, patch_ok.text

        patch_other = api_client.patch(
            f"/api/alerts/{alert_id}",
            headers=org_b_admin_headers,
            json={"status": "resolved"},
        )
        assert patch_other.status_code == 404

        with session_scope() as session:
            row = session.get(Alert, alert_id)
            if row is not None:
                session.delete(row)

    def test_alert_rules_scoped_to_org(
        self, api_client: TestClient, org_a_admin_headers: dict, org_b_admin_headers: dict
    ):
        with session_scope() as session:
            org_a_rules = session.exec(
                select(AlertRule).where(AlertRule.org_id == ORG_ID)
            ).all()
            assert len(org_a_rules) >= 1

        resp_a = api_client.get("/api/admin/alert-rules", headers=org_a_admin_headers)
        assert resp_a.status_code == 200
        resp_b = api_client.get("/api/admin/alert-rules", headers=org_b_admin_headers)
        assert resp_b.status_code == 200
        assert len(resp_b.json()) <= len(resp_a.json())
