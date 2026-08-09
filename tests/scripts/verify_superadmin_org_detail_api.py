"""E2E API verification for superadmin org detail + org-admin regression."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402
from backend.app.services.passwords import hash_password  # noqa: E402
from database.models import Organization, Superadmin  # noqa: E402
from database.seed import ORG_ID, seed_reference_data  # noqa: E402
from database.session import create_all, session_scope  # noqa: E402


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


def _login(client: TestClient, email: str, password: str) -> dict[str, str]:
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def main() -> None:
    create_all()
    seed_reference_data(force=True)
    _ensure_superadmin()

    client = TestClient(app)
    super_headers = _login(client, "superadmin@test.local", "superadmin-test-pass")
    admin_headers = _login(client, "admin@demo-retail.local", "demo")

    # --- Org detail endpoints ---
    org = client.get(f"/api/organizations/{ORG_ID}", headers=super_headers)
    assert org.status_code == 200, org.text
    print(f"GET /organizations/{ORG_ID} -> 200 {org.json()['name']!r} status={org.json()['status']!r}")

    stores = client.get(f"/api/organizations/{ORG_ID}/stores", headers=super_headers)
    assert stores.status_code == 200, stores.text
    store_list = stores.json()
    assert len(store_list) >= 1
    print(f"GET /organizations/{ORG_ID}/stores -> 200 count={len(store_list)}")

    users = client.get(f"/api/organizations/{ORG_ID}/users", headers=super_headers)
    assert users.status_code == 200, users.text
    user_list = users.json()
    assert any(u["email"] == "admin@demo-retail.local" for u in user_list)
    print(f"GET /organizations/{ORG_ID}/users -> 200 count={len(user_list)}")

    # --- Toggle service (Retail Analytics = org status) ---
    initial_status = org.json()["status"]
    toggle = client.post(f"/api/organizations/{ORG_ID}/toggle", headers=super_headers)
    assert toggle.status_code == 200, toggle.text
    toggled_status = toggle.json()["status"]
    assert toggled_status != initial_status
    print(f"POST /organizations/{ORG_ID}/toggle -> 200 status {initial_status!r} -> {toggled_status!r}")

    toggle_back = client.post(f"/api/organizations/{ORG_ID}/toggle", headers=super_headers)
    assert toggle_back.status_code == 200
    assert toggle_back.json()["status"] == initial_status
    print(f"POST /organizations/{ORG_ID}/toggle (restore) -> 200 status={toggle_back.json()['status']!r}")

    # --- Superadmin user CRUD in org ---
    suffix = uuid.uuid4().hex[:8]
    new_user_id = f"e2e_user_{suffix}"
    new_email = f"e2e_{suffix}@example.com"
    create = client.post(
        "/api/users",
        headers=super_headers,
        json={
            "id": new_user_id,
            "email": new_email,
            "name": "E2E Detail User",
            "role": "user",
            "org_id": ORG_ID,
            "store_id": store_list[0]["id"],
            "password": "detail-test-pass",
        },
    )
    assert create.status_code == 201, create.text
    print(f"POST /users (superadmin create in org) -> 201 id={new_user_id!r}")

    listed = client.get(f"/api/organizations/{ORG_ID}/users", headers=super_headers)
    assert any(u["id"] == new_user_id for u in listed.json())
    print("GET /organizations/{org}/users includes new user -> OK")

    update = client.put(
        f"/api/users/{new_user_id}",
        headers=super_headers,
        json={"name": "E2E Detail User Updated"},
    )
    assert update.status_code == 200, update.text
    assert update.json()["name"] == "E2E Detail User Updated"
    print(f"PUT /users/{new_user_id} -> 200 name updated")

    reset = client.post(
        f"/api/users/{new_user_id}/reset-password",
        headers=super_headers,
        json={"new_password": "new-detail-pass"},
    )
    assert reset.status_code == 204, reset.text
    print(f"POST /users/{new_user_id}/reset-password (superadmin) -> 204")

    login_new = client.post(
        "/api/auth/login",
        json={"email": new_email, "password": "new-detail-pass"},
    )
    assert login_new.status_code == 200, login_new.text
    print("Login with reset password -> 200")

    delete = client.delete(f"/api/users/{new_user_id}", headers=super_headers)
    assert delete.status_code == 204, delete.text
    print(f"DELETE /users/{new_user_id} -> 204")

    # --- Org-admin regression (unchanged flow) ---
    admin_users = client.get("/api/users", headers=admin_headers)
    assert admin_users.status_code == 200, admin_users.text
    print(f"GET /users (org admin) -> 200 count={len(admin_users.json())}")

    admin_reset_target = next(
        u for u in admin_users.json() if u["email"] == "user@demo-retail.local"
    )
    admin_reset = client.post(
        f"/api/users/{admin_reset_target['id']}/reset-password",
        headers=admin_headers,
        json={"new_password": "demo"},
    )
    assert admin_reset.status_code == 204, admin_reset.text
    print(f"POST /users/{admin_reset_target['id']}/reset-password (org admin) -> 204")

    admin_stores = client.get("/api/stores", headers=admin_headers)
    assert admin_stores.status_code == 200, admin_stores.text
    print(f"GET /stores (org admin) -> 200 count={len(admin_stores.json())}")

    # Superadmin still blocked from org-scoped list
    blocked = client.get("/api/users", headers=super_headers)
    assert blocked.status_code == 403, blocked.text
    print("GET /users (superadmin token) -> 403 (expected)")

    print("\nALL ORG DETAIL + REGRESSION CHECKS PASSED")


if __name__ == "__main__":
    main()
