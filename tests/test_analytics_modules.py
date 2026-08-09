"""Tests for per-camera analytics module gating."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from database.seed import seed_reference_data
from database.session import create_all, reset_engine

pytestmark = [pytest.mark.api, pytest.mark.database]


@pytest.fixture(scope="module")
def api_client():
    try:
        create_all()
        seed_reference_data(force=True)
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")

    client = TestClient(app)
    try:
        yield client
    finally:
        client.close()
        reset_engine()


@pytest.fixture(scope="module")
def admin_headers(api_client: TestClient) -> dict[str, str]:
    resp = api_client.post(
        "/api/auth/login",
        json={"email": "admin@demo-retail.local", "password": "demo"},
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


class TestAnalyticsModules:
    def test_camera_list_includes_modules(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.get("/api/cameras", headers=admin_headers)
        assert resp.status_code == 200
        entrance = next(c for c in resp.json() if c["id"] == "entrance")
        assert "entry_exit" in entrance["analytics_modules"]
        assert "occupancy" in entrance["analytics_modules"]

    def test_create_rejects_unknown_module(
        self, api_client: TestClient, admin_headers: dict
    ):
        resp = api_client.post(
            "/api/cameras",
            headers=admin_headers,
            json={
                "store_id": "store_main",
                "name": "Bad Modules Cam",
                "rtsp_url": "rtsp://10.0.0.1/stream",
                "analytics_modules": ["entry_exit", "not_a_module"],
            },
        )
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "validation_error"

    def test_queues_disabled_for_camera(
        self, api_client: TestClient, admin_headers: dict
    ):
        update = api_client.put(
            "/api/cameras/shop",
            headers=admin_headers,
            json={
                "analytics_modules": [
                    "entry_exit",
                    "occupancy",
                    "zones",
                    "dwell",
                    "heatmap",
                ],
            },
        )
        assert update.status_code == 200
        assert "queues" not in update.json()["analytics_modules"]

        resp = api_client.get(
            "/api/analytics/queues",
            headers=admin_headers,
            params={
                "store_id": "store_main",
                "zone_id": "queue_lane",
                "from": "2026-01-01",
                "to": "2026-01-02",
            },
        )
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "analytics_module_disabled"

        api_client.put(
            "/api/cameras/shop",
            headers=admin_headers,
            json={
                "analytics_modules": [
                    "entry_exit",
                    "occupancy",
                    "zones",
                    "dwell",
                    "heatmap",
                    "queues",
                ],
            },
        )

    def test_queues_disabled_with_compare_returns_403(
        self, api_client: TestClient, admin_headers: dict
    ):
        api_client.put(
            "/api/cameras/shop",
            headers=admin_headers,
            json={
                "analytics_modules": [
                    "entry_exit",
                    "occupancy",
                    "zones",
                    "dwell",
                    "heatmap",
                ],
            },
        )

        for compare in ("false", "true"):
            resp = api_client.get(
                "/api/analytics/queues",
                headers=admin_headers,
                params={
                    "store_id": "store_main",
                    "zone_id": "queue_lane",
                    "from": "2026-01-01",
                    "to": "2026-01-02",
                    "compare": compare,
                },
            )
            assert resp.status_code == 403, compare
            assert resp.json()["error"]["code"] == "analytics_module_disabled"

        api_client.put(
            "/api/cameras/shop",
            headers=admin_headers,
            json={
                "analytics_modules": [
                    "entry_exit",
                    "occupancy",
                    "zones",
                    "dwell",
                    "heatmap",
                    "queues",
                ],
            },
        )
