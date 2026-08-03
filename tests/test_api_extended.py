"""Tests for Module 12.5 — extended Backend REST API."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from database.models import Camera
from database.seed import ORG_ID, STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope

pytestmark = [pytest.mark.api, pytest.mark.api_extended, pytest.mark.database]


@pytest.fixture(scope="module")
def api_client():
    try:
        create_all()
        seed_reference_data(force=True)
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")

    with TestClient(app) as client:
        yield client
    reset_engine()


@pytest.fixture(scope="module")
def admin_headers(api_client: TestClient) -> dict[str, str]:
    resp = api_client.post(
        "/api/auth/login",
        json={"email": "admin@demo-retail.local", "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture(scope="module")
def user_headers(api_client: TestClient) -> dict[str, str]:
    resp = api_client.post(
        "/api/auth/login",
        json={"email": "user@demo-retail.local", "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def yesterday() -> str:
    return (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()


class TestAuthMe:
    def test_me(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.get("/api/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "admin@demo-retail.local"
        assert data["role"] == "admin"
        assert STORE_ID in data["store_ids"]

    def test_me_requires_auth(self, api_client: TestClient):
        assert api_client.get("/api/auth/me").status_code == 401


class TestOrganizations:
    def test_list(self, api_client: TestClient, user_headers: dict):
        resp = api_client.get("/api/organizations", headers=user_headers)
        assert resp.status_code == 200
        orgs = resp.json()
        assert any(o["id"] == ORG_ID for o in orgs)
        assert any(s["id"] == STORE_ID for s in orgs[0]["stores"])


class TestZoneShapes:
    def test_list_seeded(self, api_client: TestClient, user_headers: dict):
        resp = api_client.get("/api/zones?camera_id=town", headers=user_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_all_without_camera_id(self, api_client: TestClient, user_headers: dict):
        resp = api_client.get("/api/zones", headers=user_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_camera_not_found(self, api_client: TestClient, user_headers: dict):
        resp = api_client.get("/api/zones?camera_id=missing", headers=user_headers)
        assert resp.status_code == 404

    def test_create_and_delete(self, api_client: TestClient, admin_headers: dict):
        zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        resp = api_client.post(
            "/api/zones",
            headers=admin_headers,
            json={
                "id": zone_id,
                "camera_id": "town",
                "name": "Test Zone",
                "type": "general",
                "polygon_points": [[0, 0], [10, 0], [10, 10]],
            },
        )
        assert resp.status_code == 201
        assert resp.json()["type"] == "general"

        resp = api_client.put(
            f"/api/zones/{zone_id}",
            headers=admin_headers,
            json={"name": "Renamed"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Renamed"

        assert api_client.delete(f"/api/zones/{zone_id}", headers=admin_headers).status_code == 204

    def test_create_forbidden_for_user(self, api_client: TestClient, user_headers: dict):
        resp = api_client.post(
            "/api/zones",
            headers=user_headers,
            json={
                "id": "zone_fail",
                "camera_id": "town",
                "name": "Nope",
                "type": "general",
                "polygon_points": [[0, 0], [1, 0], [1, 1]],
            },
        )
        assert resp.status_code == 403

    def test_create_invalid_polygon(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.post(
            "/api/zones",
            headers=admin_headers,
            json={
                "id": "zone_bad_poly",
                "camera_id": "town",
                "name": "Bad",
                "type": "general",
                "polygon_points": [[0, 0], [1, 1]],
            },
        )
        assert resp.status_code == 422


class TestCountingLines:
    def test_list_seeded(self, api_client: TestClient, user_headers: dict):
        resp = api_client.get("/api/lines?camera_id=entrance", headers=user_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_all_without_camera_id(self, api_client: TestClient, user_headers: dict):
        resp = api_client.get("/api/lines", headers=user_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_crud_admin(self, api_client: TestClient, admin_headers: dict):
        line_id = f"line_{uuid.uuid4().hex[:8]}"
        create = api_client.post(
            "/api/lines",
            headers=admin_headers,
            json={
                "id": line_id,
                "camera_id": "entrance",
                "name": "Side door",
                "point_a": {"x": 1, "y": 2},
                "point_b": {"x": 3, "y": 4},
                "direction": "right_is_inside",
            },
        )
        assert create.status_code == 201

        update = api_client.put(
            f"/api/lines/{line_id}",
            headers=admin_headers,
            json={"name": "Updated"},
        )
        assert update.status_code == 200

        assert api_client.delete(f"/api/lines/{line_id}", headers=admin_headers).status_code == 204

    def test_create_forbidden_for_user(self, api_client: TestClient, user_headers: dict):
        resp = api_client.post(
            "/api/lines",
            headers=user_headers,
            json={
                "id": "line_fail",
                "camera_id": "entrance",
                "name": "Nope",
                "point_a": {"x": 0, "y": 0},
                "point_b": {"x": 1, "y": 1},
            },
        )
        assert resp.status_code == 403

    def test_not_found(self, api_client: TestClient, admin_headers: dict):
        assert api_client.get("/api/lines?camera_id=missing", headers=admin_headers).status_code == 404


class TestCamerasExtended:
    def test_update_and_soft_delete(self, api_client: TestClient, admin_headers: dict):
        create_resp = api_client.post(
            "/api/cameras",
            headers=admin_headers,
            json={
                "store_id": STORE_ID,
                "name": "Temp",
                "rtsp_url": "rtsp://192.168.1.50:554/stream1",
                "source_type": "live",
            },
        )
        assert create_resp.status_code == 201
        cam_id = create_resp.json()["id"]
        assert cam_id.startswith("cam_")
        resp = api_client.put(
            f"/api/cameras/{cam_id}",
            headers=admin_headers,
            json={"name": "Temp Updated"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Temp Updated"

        resp = api_client.delete(f"/api/cameras/{cam_id}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "disabled"

    def test_test_stream(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.post("/api/cameras/entrance/test", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("success", "error")
        assert "camera_status" in data

    def test_test_stream_updates_persisted_status(
        self, api_client: TestClient, admin_headers: dict,
    ):
        original_url: str | None = None
        with session_scope() as session:
            camera = session.get(Camera, "entrance")
            assert camera is not None
            original_url = camera.rtsp_url
            camera.rtsp_url = "rtsp://127.0.0.1:9/unreachable"
            camera.status = "online"
            session.add(camera)

        resp = api_client.post("/api/cameras/entrance/test", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "error"
        assert resp.json()["camera_status"] == "error"

        with session_scope() as session:
            camera = session.get(Camera, "entrance")
            assert camera is not None
            assert camera.status == "error"
            if original_url is not None:
                camera.rtsp_url = original_url
                camera.status = "online"
                session.add(camera)

    def test_update_forbidden_for_user(self, api_client: TestClient, user_headers: dict):
        resp = api_client.put(
            "/api/cameras/entrance",
            headers=user_headers,
            json={"name": "Hacked"},
        )
        assert resp.status_code == 403

    def test_create_recorded_camera(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.post(
            "/api/cameras",
            headers=admin_headers,
            json={
                "store_id": STORE_ID,
                "name": "Recorded Checkout",
                "location": "Checkout aisle",
                "rtsp_url": "sample-data/checkout.mp4",
                "source_type": "recorded",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["source_type"] == "recorded"
        assert data["last_processed_at"] is None

    def test_process_rejected_for_live_camera(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.post("/api/cameras/entrance/process", headers=admin_headers)
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_camera_source"

    def test_camera_status_includes_source_type(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.get("/api/cameras/entrance/status", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["source_type"] == "live"
        assert data["processed"] is None


class TestAlertsExtended:
    def test_patch_alert(self, api_client: TestClient, user_headers: dict):
        from database.models import Alert

        with session_scope() as session:
            alert = Alert(
                alert_type="TEST_ALERT",
                camera_id="entrance",
                timestamp=datetime.now(timezone.utc),
                severity="warning",
                status="open",
            )
            session.add(alert)
            session.flush()
            alert_id = alert.id

        resp = api_client.patch(
            f"/api/alerts/{alert_id}",
            headers=user_headers,
            json={"status": "acknowledged"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "acknowledged"

    def test_patch_not_found(self, api_client: TestClient, user_headers: dict):
        resp = api_client.patch(
            "/api/alerts/999999999",
            headers=user_headers,
            json={"status": "resolved"},
        )
        assert resp.status_code == 404


class TestReports:
    def test_traffic_json(self, api_client: TestClient, user_headers: dict, yesterday: str):
        resp = api_client.get(
            "/api/reports/traffic",
            headers=user_headers,
            params={"store_id": STORE_ID, "from": yesterday, "to": yesterday},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["header"]["report_type"] == "traffic"
        assert data["kpis"]

    def test_export_csv(self, api_client: TestClient, user_headers: dict, yesterday: str):
        resp = api_client.get(
            "/api/reports/traffic/export",
            headers=user_headers,
            params={
                "store_id": STORE_ID,
                "from": yesterday,
                "to": yesterday,
                "format": "csv",
            },
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert len(resp.content) > 100
        text = resp.text
        assert text.startswith("# report_type=")
        assert "metric,value" in text
        assert "date,hour,entries,exits" in text

    def test_export_csv_zones(self, api_client: TestClient, user_headers: dict, yesterday: str):
        resp = api_client.get(
            "/api/reports/zones/export",
            headers=user_headers,
            params={
                "store_id": STORE_ID,
                "from": yesterday,
                "to": yesterday,
                "format": "csv",
            },
        )
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert len(resp.content) > 80

    def test_export_pdf(self, api_client: TestClient, user_headers: dict, yesterday: str):
        resp = api_client.get(
            "/api/reports/occupancy/export",
            headers=user_headers,
            params={
                "store_id": STORE_ID,
                "from": "2020-01-01",
                "to": "2099-12-31",
                "format": "pdf",
            },
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert len(resp.content) > 3000
        assert resp.content.startswith(b"%PDF")

    def test_export_pdf_traffic(self, api_client: TestClient, user_headers: dict, yesterday: str):
        resp = api_client.get(
            "/api/reports/traffic/export",
            headers=user_headers,
            params={
                "store_id": STORE_ID,
                "from": yesterday,
                "to": yesterday,
                "format": "pdf",
            },
        )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert len(resp.content) > 3000
        assert resp.content.startswith(b"%PDF")

    def test_invalid_type(self, api_client: TestClient, user_headers: dict, yesterday: str):
        resp = api_client.get(
            "/api/reports/not-a-type",
            headers=user_headers,
            params={"store_id": STORE_ID, "from": yesterday, "to": yesterday},
        )
        assert resp.status_code == 400


class TestUsersAdmin:
    def test_list_and_crud(self, api_client: TestClient, admin_headers: dict):
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        create = api_client.post(
            "/api/users",
            headers=admin_headers,
            json={
                "id": user_id,
                "email": f"{user_id}@example.com",
                "name": "Created User",
                "role": "user",
                "org_id": ORG_ID,
                "password": "secret123",
            },
        )
        assert create.status_code == 201

        listing = api_client.get("/api/users", headers=admin_headers)
        assert listing.status_code == 200
        assert any(u["id"] == user_id for u in listing.json())

        update = api_client.put(
            f"/api/users/{user_id}",
            headers=admin_headers,
            json={"name": "Renamed User"},
        )
        assert update.status_code == 200

        reset = api_client.post(
            f"/api/users/{user_id}/reset-password",
            headers=admin_headers,
            json={"new_password": "newsecret"},
        )
        assert reset.status_code == 204

        delete = api_client.delete(f"/api/users/{user_id}", headers=admin_headers)
        assert delete.status_code == 204

    def test_forbidden_for_regular_user(self, api_client: TestClient, user_headers: dict):
        assert api_client.get("/api/users", headers=user_headers).status_code == 403

    def test_create_user_not_found_org(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.post(
            "/api/users",
            headers=admin_headers,
            json={
                "id": "user_bad_org",
                "email": "badorg@example.com",
                "name": "Bad",
                "role": "user",
                "org_id": "missing_org",
                "password": "secret123",
            },
        )
        assert resp.status_code == 404
