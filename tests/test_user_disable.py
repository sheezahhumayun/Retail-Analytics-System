"""User disable / reactivate admin flows."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from database.seed import ORG_ID, seed_reference_data
from database.session import create_all, reset_engine

pytestmark = [pytest.mark.api, pytest.mark.api_extended, pytest.mark.database]


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


class TestUserDisable:
    def test_put_disable_persists_status(
        self, api_client: TestClient, admin_headers: dict
    ):
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        email = f"{user_id}@example.com"
        create = api_client.post(
            "/api/users",
            headers=admin_headers,
            json={
                "id": user_id,
                "email": email,
                "name": "Disable Target",
                "role": "user",
                "org_id": ORG_ID,
                "password": "secret123",
            },
        )
        assert create.status_code == 201, create.text

        disable = api_client.put(
            f"/api/users/{user_id}",
            headers=admin_headers,
            json={"status": "disabled"},
        )
        assert disable.status_code == 200, disable.text
        assert disable.json()["status"] == "disabled"

        listing = api_client.get("/api/users", headers=admin_headers)
        assert listing.status_code == 200
        row = next(u for u in listing.json() if u["id"] == user_id)
        assert row["status"] == "disabled"

        api_client.delete(f"/api/users/{user_id}", headers=admin_headers)

    def test_disabled_user_cannot_login(
        self, api_client: TestClient, admin_headers: dict
    ):
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        email = f"{user_id}@example.com"
        password = "disable-login-test"
        api_client.post(
            "/api/users",
            headers=admin_headers,
            json={
                "id": user_id,
                "email": email,
                "name": "Login Block Target",
                "role": "user",
                "org_id": ORG_ID,
                "password": password,
            },
        )
        disable = api_client.put(
            f"/api/users/{user_id}",
            headers=admin_headers,
            json={"status": "disabled"},
        )
        assert disable.status_code == 200, disable.text

        login = api_client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert login.status_code == 401, login.text
        assert login.json()["error"]["code"] == "account_disabled"
        assert "disabled" in login.json()["error"]["message"].lower()

        api_client.delete(f"/api/users/{user_id}", headers=admin_headers)

    def test_disabled_admin_token_rejected_on_next_request(
        self, api_client: TestClient, admin_headers: dict
    ):
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        email = f"{user_id}@example.com"
        password = "admin-self-disable"
        api_client.post(
            "/api/users",
            headers=admin_headers,
            json={
                "id": user_id,
                "email": email,
                "name": "Self Disable Admin",
                "role": "admin",
                "org_id": ORG_ID,
                "password": password,
            },
        )

        login = api_client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        assert api_client.get("/api/users", headers=headers).status_code == 200

        disable = api_client.put(
            f"/api/users/{user_id}",
            headers=headers,
            json={"status": "disabled"},
        )
        assert disable.status_code == 200, disable.text

        after_disable = api_client.get("/api/users", headers=headers)
        assert after_disable.status_code == 401
        assert after_disable.json()["error"]["code"] == "account_disabled"

        api_client.delete(f"/api/users/{user_id}", headers=admin_headers)

    def test_frontend_display_status_rejected_with_422(
        self, api_client: TestClient, admin_headers: dict
    ):
        """Regression: UI labels like 'Disabled' must not be sent raw to the API."""
        resp = api_client.put(
            "/api/users/user_admin",
            headers=admin_headers,
            json={"status": "Disabled"},
        )
        assert resp.status_code == 422, resp.text
