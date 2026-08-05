"""Tests for Module 12 — Backend REST API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, reset_engine

pytestmark = [pytest.mark.api, pytest.mark.database]


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
def auth_headers(api_client: TestClient) -> dict[str, str]:
    resp = api_client.post(
        "/api/auth/login",
        json={"email": "admin@demo-retail.local", "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def user_auth_headers(api_client: TestClient) -> dict[str, str]:
    resp = api_client.post(
        "/api/auth/login",
        json={"email": "user@demo-retail.local", "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    def test_login_success(self, api_client: TestClient):
        resp = api_client.post(
            "/api/auth/login",
            json={"email": "admin@demo-retail.local", "password": "demo"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["token_type"] == "bearer"
        assert data["user"]["role"] == "admin"

    def test_login_bad_password(self, api_client: TestClient):
        resp = api_client.post(
            "/api/auth/login",
            json={"email": "admin@demo-retail.local", "password": "wrong"},
        )
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "invalid_credentials"

    def test_protected_route_requires_auth(self, api_client: TestClient):
        resp = api_client.get("/api/stores")
        assert resp.status_code == 401


class TestStores:
    def test_list_stores(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get("/api/stores", headers=auth_headers)
        assert resp.status_code == 200
        stores = resp.json()
        assert any(s["id"] == STORE_ID for s in stores)

    def test_create_store(self, api_client: TestClient, auth_headers: dict):
        import uuid

        store_id = f"store_api_{uuid.uuid4().hex[:8]}"
        resp = api_client.post(
            "/api/stores",
            headers=auth_headers,
            json={
                "id": store_id,
                "org_id": "org_demo",
                "name": "API Test Store",
                "address": "1 Test Lane",
            },
        )
        assert resp.status_code == 201
        assert resp.json()["id"] == store_id


class TestCameras:
    def test_list_cameras(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get("/api/cameras", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_camera_status(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get("/api/cameras/entrance/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "entrance"
        assert "status" in data

    def test_camera_not_found(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get("/api/cameras/does-not-exist/status", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "camera_not_found"

    def test_create_camera_bad_rtsp(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.post(
            "/api/cameras",
            headers=auth_headers,
            json={
                "store_id": STORE_ID,
                "name": "Bad",
                "rtsp_url": "not-a-valid-url!!!",
            },
        )
        assert resp.status_code == 422

    def test_create_camera_generates_id(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.post(
            "/api/cameras",
            headers=auth_headers,
            json={
                "store_id": STORE_ID,
                "name": "Back Lot Camera",
                "location": "Rear entrance",
                "rtsp_url": "rtsp://192.168.1.50:554/stream1",
                "source_type": "live",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"]
        assert data["id"].startswith("cam_")
        assert data["name"] == "Back Lot Camera"
        assert data["store_id"] == STORE_ID

    def test_create_camera_forbidden_for_regular_user(
        self, api_client: TestClient, user_auth_headers: dict
    ):
        resp = api_client.post(
            "/api/cameras",
            headers=user_auth_headers,
            json={
                "store_id": STORE_ID,
                "name": "Should Fail",
                "rtsp_url": "sample-data/town.mp4",
            },
        )
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "forbidden"

    def _create_camera(self, api_client: TestClient, auth_headers: dict, name: str) -> str:
        resp = api_client.post(
            "/api/cameras",
            headers=auth_headers,
            json={
                "store_id": STORE_ID,
                "name": name,
                "rtsp_url": "rtsp://192.168.1.51:554/stream1",
                "source_type": "live",
            },
        )
        assert resp.status_code == 201, resp.text
        return resp.json()["id"]

    def test_delete_camera_is_soft_delete_excluded_from_default_list(
        self, api_client: TestClient, auth_headers: dict
    ):
        camera_id = self._create_camera(api_client, auth_headers, "Soft Delete Target")

        resp = api_client.delete(f"/api/cameras/{camera_id}", headers=auth_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == "disabled"

        # Bug 2 regression: default list must exclude soft-deleted cameras so
        # they don't reappear after a reload.
        default_list = api_client.get("/api/cameras", headers=auth_headers).json()
        assert camera_id not in {c["id"] for c in default_list}

        # But an admin can still opt in to see disabled cameras (e.g. to
        # re-enable them from the management UI).
        full_list = api_client.get(
            "/api/cameras", headers=auth_headers, params={"include_disabled": True}
        ).json()
        assert camera_id in {c["id"] for c in full_list}

    def test_put_status_disable_and_reenable_camera(
        self, api_client: TestClient, auth_headers: dict
    ):
        camera_id = self._create_camera(api_client, auth_headers, "Toggle Target")

        # Bug 1 regression: PUT must actually accept a status/enable field and
        # persist it — this used to be silently dropped from the update body.
        disable_resp = api_client.put(
            f"/api/cameras/{camera_id}",
            headers=auth_headers,
            json={"status": "disabled"},
        )
        assert disable_resp.status_code == 200, disable_resp.text
        assert disable_resp.json()["status"] == "disabled"

        default_list = api_client.get("/api/cameras", headers=auth_headers).json()
        assert camera_id not in {c["id"] for c in default_list}

        reenable_resp = api_client.put(
            f"/api/cameras/{camera_id}",
            headers=auth_headers,
            json={"status": "offline"},
        )
        assert reenable_resp.status_code == 200, reenable_resp.text
        assert reenable_resp.json()["status"] == "offline"

        default_list = api_client.get("/api/cameras", headers=auth_headers).json()
        assert camera_id in {c["id"] for c in default_list}

    def test_put_status_rejects_probe_derived_values(
        self, api_client: TestClient, auth_headers: dict
    ):
        camera_id = self._create_camera(api_client, auth_headers, "Rejects Online Target")

        resp = api_client.put(
            f"/api/cameras/{camera_id}",
            headers=auth_headers,
            json={"status": "online"},
        )
        assert resp.status_code == 422

    def test_camera_stream_requires_auth(self, api_client: TestClient):
        resp = api_client.get("/api/cameras/entrance/stream")
        assert resp.status_code == 401
        assert resp.json()["error"]["code"] == "not_authenticated"

    def test_camera_stream_accepts_token_query_param(
        self, api_client: TestClient, auth_headers: dict
    ):
        token = auth_headers["Authorization"].split(" ", 1)[1]
        mock_source = MagicMock()
        mock_source.is_live.return_value = False
        mock_source.read.return_value = (False, None)
        first_chunk = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n\xff\xd8\xff"

        with patch(
            "backend.app.routers.cameras.open_stream_source",
            return_value=(mock_source, first_chunk),
        ):
            with api_client.stream(
                "GET",
                f"/api/cameras/entrance/stream?token={token}",
            ) as resp:
                assert resp.status_code == 200, resp.text
                assert "multipart/x-mixed-replace" in resp.headers.get(
                    "content-type", ""
                )
                chunk = next(resp.iter_bytes(chunk_size=256))
                assert chunk.startswith(b"--frame")
        mock_source.release.assert_called()

    def test_camera_stream_not_found(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get(
            "/api/cameras/does-not-exist/stream",
            headers=auth_headers,
        )
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "camera_not_found"

    def test_camera_stream_rejects_recorded_source(
        self, api_client: TestClient, auth_headers: dict
    ):
        create = api_client.post(
            "/api/cameras",
            headers=auth_headers,
            json={
                "store_id": STORE_ID,
                "name": "Recorded Stream Block",
                "rtsp_url": "sample-data/checkout.mp4",
                "source_type": "recorded",
            },
        )
        assert create.status_code == 201, create.text
        camera_id = create.json()["id"]

        resp = api_client.get(f"/api/cameras/{camera_id}/stream", headers=auth_headers)
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "camera_not_live"


class TestAnalytics:
    def test_traffic(self, api_client: TestClient, auth_headers: dict):
        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        resp = api_client.get(
            "/api/analytics/traffic",
            headers=auth_headers,
            params={"store_id": STORE_ID, "from": yesterday, "to": yesterday},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["store_id"] == STORE_ID
        assert len(data["buckets"]) == 24
        assert data["total_entries"] > 0

    def test_traffic_bad_store(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get(
            "/api/analytics/traffic",
            headers=auth_headers,
            params={"store_id": "nope", "from": "2026-01-01", "to": "2026-01-02"},
        )
        assert resp.status_code == 404

    def test_traffic_bad_date_range(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get(
            "/api/analytics/traffic",
            headers=auth_headers,
            params={"store_id": STORE_ID, "from": "2026-01-10", "to": "2026-01-01"},
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_date_range"

    def test_occupancy_by_store(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get(
            "/api/analytics/occupancy",
            headers=auth_headers,
            params={"store_id": STORE_ID},
        )
        assert resp.status_code == 200
        assert resp.json()["scope"] == "store"

    def test_occupancy_requires_scope(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get("/api/analytics/occupancy", headers=auth_headers)
        assert resp.status_code == 400

    def test_zones(self, api_client: TestClient, auth_headers: dict):
        yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()
        resp = api_client.get(
            "/api/analytics/zones",
            headers=auth_headers,
            params={"store_id": STORE_ID, "zone_id": "store1", "from": yesterday, "to": yesterday},
        )
        assert resp.status_code == 200
        assert resp.json()["zone_id"] == "store1"

    def test_dwell(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get(
            "/api/analytics/dwell",
            headers=auth_headers,
            params={
                "store_id": STORE_ID,
                "zone_id": "store1",
                "from": "2020-01-01",
                "to": "2099-12-31",
            },
        )
        assert resp.status_code == 200
        assert "sessions" in resp.json()

    def test_queues_empty(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get(
            "/api/analytics/queues",
            headers=auth_headers,
            params={
                "store_id": STORE_ID,
                "zone_id": "queue_lane",
                "from": "2099-01-01",
                "to": "2099-01-02",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["samples"] == []


class TestEventsAndAlerts:
    def test_events(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get(
            "/api/events",
            headers=auth_headers,
            params={
                "from": "2020-01-01",
                "to": "2099-12-31",
                "camera_id": "entrance",
            },
        )
        assert resp.status_code == 200
        assert "events" in resp.json()

    def test_events_bad_camera(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get(
            "/api/events",
            headers=auth_headers,
            params={
                "from": "2020-01-01",
                "to": "2099-12-31",
                "camera_id": "missing-cam",
            },
        )
        assert resp.status_code == 404

    def test_alerts(self, api_client: TestClient, auth_headers: dict):
        resp = api_client.get("/api/alerts", headers=auth_headers)
        assert resp.status_code == 200
        assert "alerts" in resp.json()


class TestOpenAPI:
    def test_openapi_lists_endpoints(self, api_client: TestClient):
        resp = api_client.get("/openapi.json")
        assert resp.status_code == 200
        paths = resp.json()["paths"]
        for path in (
            "/api/stores",
            "/api/cameras",
            "/api/cameras/{camera_id}/status",
            "/api/analytics/traffic",
            "/api/analytics/occupancy",
            "/api/analytics/zones",
            "/api/analytics/dwell",
            "/api/analytics/heatmap",
            "/api/analytics/queues",
            "/api/events",
            "/api/alerts",
        ):
            assert path in paths, f"Missing {path} in OpenAPI spec"
