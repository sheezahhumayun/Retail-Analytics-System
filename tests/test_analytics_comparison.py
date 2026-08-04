"""Tests for period-over-period analytics comparison."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.analytics_comparison import prior_period_bounds
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


class TestPriorPeriodBounds:
    def test_week_span(self):
        start = datetime(2026, 2, 10, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 2, 16, 23, 59, 59, tzinfo=timezone.utc)
        prior_start, prior_end = prior_period_bounds(start, end)
        assert prior_end.date() == start.date() - timedelta(days=1)
        assert (prior_end.date() - prior_start.date()).days == 6


class TestAnalyticsComparison:
    def test_traffic_compare_returns_prior_buckets(
        self, api_client: TestClient, admin_headers: dict
    ):
        resp = api_client.get(
            "/api/analytics/traffic",
            headers=admin_headers,
            params={
                "store_id": "store_main",
                "from": "2026-01-15",
                "to": "2026-01-21",
                "compare": "true",
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert "comparison" in body
        assert body["comparison"]["status"] in ("ok", "insufficient_history", "module_disabled")
        assert "prior_buckets" in body
        assert isinstance(body["prior_buckets"], list)
        if body["comparison"]["status"] == "ok":
            assert body["comparison"]["from"]
            assert body["comparison"]["to"]

    def test_traffic_compare_without_flag_has_no_comparison(
        self, api_client: TestClient, admin_headers: dict
    ):
        resp = api_client.get(
            "/api/analytics/traffic",
            headers=admin_headers,
            params={
                "store_id": "store_main",
                "from": "2026-01-15",
                "to": "2026-01-21",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("comparison") in (None, {})
        assert body.get("prior_buckets", []) == []

    def test_report_compare_includes_prior_columns(
        self, api_client: TestClient, admin_headers: dict
    ):
        resp = api_client.get(
            "/api/reports/traffic",
            headers=admin_headers,
            params={
                "store_id": "store_main",
                "from": "2026-01-15",
                "to": "2026-01-21",
                "compare": "true",
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body.get("comparison") is not None
        if body["table"]:
            assert "prior_entries" in body["table"][0]["columns"]
