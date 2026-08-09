"""Quick API verification for superadmin frontend auth + org CRUD."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.passwords import hash_password
from database.models import Superadmin
from database.seed import seed_reference_data
from database.session import create_all, session_scope


def _ensure_superadmin() -> None:
    with session_scope() as session:
        if session.get(Superadmin, "superadmin_test") is None:
            session.add(
                Superadmin(
                    id="superadmin_test",
                    name="Test Superadmin",
                    email="superadmin@test.local",
                    password_hash=hash_password("superadmin-test-pass"),
                    status="active",
                )
            )
            session.commit()


def main() -> None:
    create_all()
    seed_reference_data(force=True)
    _ensure_superadmin()

    client = TestClient(app)

    login = client.post(
        "/api/auth/login",
        json={"email": "superadmin@test.local", "password": "superadmin-test-pass"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    assert login.json()["user"]["account_type"] == "superadmin"
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/auth/superadmin/me", headers=headers)
    assert me.status_code == 200, me.text
    me_data = me.json()
    assert me_data["account_type"] == "superadmin"
    assert me_data["org_id"] is None
    print("superadmin/me OK:", me_data["email"])

    admin_login = client.post(
        "/api/auth/login",
        json={"email": "admin@demo-retail.local", "password": "demo"},
    )
    assert admin_login.status_code == 200
    admin_headers = {
        "Authorization": f"Bearer {admin_login.json()['access_token']}"
    }
    org_me = client.get("/api/auth/me", headers=admin_headers)
    assert org_me.status_code == 200
    assert org_me.json()["email"] == "admin@demo-retail.local"
    print("org-admin/me OK")

    blocked = client.get("/api/auth/me", headers=headers)
    assert blocked.status_code == 403
    print("superadmin blocked from /auth/me OK")

    org_id = f"e2e_{uuid.uuid4().hex[:8]}"

    created = client.post(
        "/api/organizations",
        headers=headers,
        json={"id": org_id, "name": "E2E Test Org"},
    )
    assert created.status_code == 201, created.text

    toggled = client.post(
        f"/api/organizations/{org_id}/toggle", headers=headers
    )
    assert toggled.status_code == 200
    assert toggled.json()["status"] == "disabled"

    reenabled = client.post(
        f"/api/organizations/{org_id}/toggle", headers=headers
    )
    assert reenabled.json()["status"] == "active"

    mismatch = client.request(
        "DELETE",
        f"/api/organizations/{org_id}",
        headers=headers,
        json={"confirm": "wrong"},
    )
    assert mismatch.status_code == 400

    deleted = client.request(
        "DELETE",
        f"/api/organizations/{org_id}",
        headers=headers,
        json={"confirm": org_id},
    )
    assert deleted.status_code == 204
    print("org create/toggle/delete OK")
    print("ALL E2E API CHECKS PASSED")


if __name__ == "__main__":
    main()
