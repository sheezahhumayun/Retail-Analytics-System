#!/usr/bin/env python
"""Item 3 only — toggle blocks with pre-disable token."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from fastapi.testclient import TestClient  # noqa: E402
from analytics.modules import infer_default_modules  # noqa: E402
from backend.app.main import app  # noqa: E402
from backend.app.services.passwords import hash_password  # noqa: E402
from database.models import Camera, Organization, Store, Superadmin, User  # noqa: E402
from database.session import session_scope  # noqa: E402

ORG = "org_toggle_verify2"
STORE = "store_toggle_verify2"
CAM = "cam_toggle_verify2"
EMAIL = "toggle2@test.local"
PWD = "toggle2-pass"
VIDEO = "sample-data/entrance.mp4"


def main() -> None:
    with session_scope() as s:
        s.merge(
            Superadmin(
                id="superadmin_test",
                name="SA",
                email="superadmin@test.local",
                password_hash=hash_password("superadmin-test-pass"),
                status="active",
            )
        )
        s.merge(Organization(id=ORG, name="Toggle2", status="active"))
        s.merge(Store(id=STORE, org_id=ORG, name="S", address="x"))
        s.merge(
            User(
                id="u2",
                org_id=ORG,
                name="A",
                email=EMAIL,
                role="admin",
                password_hash=hash_password(PWD),
                status="active",
            )
        )
        s.merge(
            Camera(
                id=CAM,
                store_id=STORE,
                name="C",
                rtsp_url=VIDEO,
                source_type="recorded",
                analytics_modules=infer_default_modules(
                    has_counting_line=False, zone_types=["general"]
                ),
            )
        )
        s.commit()

    client = TestClient(app)
    try:
        sa_token = client.post(
            "/api/auth/login",
            json={"email": "superadmin@test.local", "password": "superadmin-test-pass"},
        ).json()["access_token"]
        sa_headers = {"Authorization": f"Bearer {sa_token}"}

        login = client.post("/api/auth/login", json={"email": EMAIL, "password": PWD})
        print("LOGIN while active:", login.status_code, login.text)
        admin_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        disable = client.post(f"/api/organizations/{ORG}/toggle", headers=sa_headers)
        print("DISABLE:", disable.status_code, disable.text)

        login_disabled = client.post(
            "/api/auth/login", json={"email": EMAIL, "password": PWD}
        )
        print("LOGIN while disabled:", login_disabled.status_code, login_disabled.text)

        process_disabled = client.post(
            f"/api/cameras/{CAM}/process", headers=admin_headers
        )
        print(
            "PROCESS with pre-disable token:",
            process_disabled.status_code,
            process_disabled.text,
        )

        enable = client.post(f"/api/organizations/{ORG}/toggle", headers=sa_headers)
        print("RE-ENABLE:", enable.status_code, enable.text)

        login2 = client.post("/api/auth/login", json={"email": EMAIL, "password": PWD})
        print("LOGIN after re-enable:", login2.status_code, login2.text)
        admin_headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}

        process_active = client.post(
            f"/api/cameras/{CAM}/process", headers=admin_headers2
        )
        print("PROCESS after re-enable:", process_active.status_code, process_active.text)
    finally:
        client.close()


if __name__ == "__main__":
    main()
