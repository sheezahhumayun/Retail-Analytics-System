"""E2E API verification for superadmin store CRUD + All Stores user assignment."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from backend.app.main import app  # noqa: E402
from backend.app.services.passwords import hash_password  # noqa: E402
from database.models import Superadmin  # noqa: E402
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

    suffix = uuid.uuid4().hex[:8]
    store_id = f"e2e_store_{suffix}"

    # Superadmin create store
    created = client.post(
        "/api/stores",
        headers=super_headers,
        json={
            "id": store_id,
            "org_id": ORG_ID,
            "name": f"E2E Store {suffix}",
            "address": "123 Test Lane",
        },
    )
    assert created.status_code == 201, created.text
    print(f"POST /stores (superadmin) -> 201 id={store_id!r}")

    listed = client.get(f"/api/organizations/{ORG_ID}/stores", headers=super_headers)
    assert any(s["id"] == store_id for s in listed.json())
    print("GET /organizations/{org}/stores includes new store -> OK")

    updated = client.put(
        f"/api/stores/{store_id}",
        headers=super_headers,
        json={"name": f"E2E Store Renamed {suffix}", "address": "456 Updated Ave"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["name"] == f"E2E Store Renamed {suffix}"
    print(f"PUT /stores/{store_id} -> 200 name updated")

    # User with specific store
    user_store_id = f"e2e_user_store_{suffix}"
    user_store_email = f"e2e_store_{suffix}@example.com"
    create_user_store = client.post(
        "/api/users",
        headers=super_headers,
        json={
            "id": user_store_id,
            "email": user_store_email,
            "name": "E2E Store User",
            "role": "user",
            "org_id": ORG_ID,
            "store_id": store_id,
            "password": "detail-test-pass",
        },
    )
    assert create_user_store.status_code == 201, create_user_store.text
    assert create_user_store.json()["store_id"] == store_id
    print("POST /users with store_id -> 201")

    # User with All Stores (null store_id)
    user_all_id = f"e2e_user_all_{suffix}"
    user_all_email = f"e2e_all_{suffix}@example.com"
    create_user_all = client.post(
        "/api/users",
        headers=super_headers,
        json={
            "id": user_all_id,
            "email": user_all_email,
            "name": "E2E All Stores User",
            "role": "user",
            "org_id": ORG_ID,
            "store_id": None,
            "password": "detail-test-pass",
        },
    )
    assert create_user_all.status_code == 201, create_user_all.text
    assert create_user_all.json()["store_id"] is None
    print("POST /users with store_id=null -> 201")

    # Re-edit All Stores user to clear store (explicit null in update)
    reedit = client.put(
        f"/api/users/{user_store_id}",
        headers=super_headers,
        json={"store_id": None},
    )
    assert reedit.status_code == 200, reedit.text
    assert reedit.json()["store_id"] is None
    print(f"PUT /users/{user_store_id} store_id=null -> 200")

    # Delete empty store
    deleted = client.delete(f"/api/stores/{store_id}", headers=super_headers)
    assert deleted.status_code == 204, deleted.text
    print(f"DELETE /stores/{store_id} -> 204")

    # Org admin store create still works (own org only)
    admin_store_id = f"admin_store_{suffix}"
    admin_create = client.post(
        "/api/stores",
        headers=admin_headers,
        json={
            "id": admin_store_id,
            "org_id": ORG_ID,
            "name": f"Admin Store {suffix}",
        },
    )
    assert admin_create.status_code == 201, admin_create.text
    print("POST /stores (org admin) -> 201")

    wrong_org = client.post(
        "/api/stores",
        headers=admin_headers,
        json={
            "id": f"wrong_org_{suffix}",
            "org_id": "other_org",
            "name": "Should Fail",
        },
    )
    assert wrong_org.status_code == 404, wrong_org.text
    print("POST /stores (org admin wrong org_id) -> 404")

    # Cleanup admin-created store
    client.delete(f"/api/stores/{admin_store_id}", headers=admin_headers)

    # Cleanup users
    client.delete(f"/api/users/{user_store_id}", headers=super_headers)
    client.delete(f"/api/users/{user_all_id}", headers=super_headers)

    print("\nALL STORE CRUD + ALL STORES CHECKS PASSED")


if __name__ == "__main__":
    main()
