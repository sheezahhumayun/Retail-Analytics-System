"""Report scope tests for analytics_modules gating."""

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


@pytest.fixture
def yesterday() -> str:
    from datetime import datetime, timedelta, timezone

    return (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()


class TestReportModuleScope:
    def test_single_camera_report_module_disabled(
        self, api_client: TestClient, admin_headers: dict, yesterday: str
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
        resp = api_client.get(
            "/api/reports/queues",
            headers=admin_headers,
            params={
                "store_id": "store_main",
                "camera_id": "shop",
                "from": yesterday,
                "to": yesterday,
            },
        )
        assert resp.status_code == 403
        assert resp.json()["error"]["code"] == "analytics_module_disabled"

    def test_store_report_includes_exclusions(
        self, api_client: TestClient, admin_headers: dict, yesterday: str
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
        resp = api_client.get(
            "/api/reports/queues",
            headers=admin_headers,
            params={
                "store_id": "store_main",
                "from": yesterday,
                "to": yesterday,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("footnotes")
        assert any("queue" in note.lower() for note in data["footnotes"])
        assert data.get("exclusions")

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
