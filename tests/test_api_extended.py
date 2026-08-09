"""Tests for Module 12.5 — extended Backend REST API."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select

from backend.app.main import app
from database.models import Camera, CountingLine, ProcessingRun, User, Zone, ZoneMetric, ZoneShape
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

    def test_update_keeps_analytics_zone_in_sync(
        self, api_client: TestClient, admin_headers: dict
    ):
        zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        initial_points = [[0, 0], [10, 0], [10, 10]]
        updated_points = [[5, 5], [50, 5], [50, 50], [5, 50]]

        create_resp = api_client.post(
            "/api/zones",
            headers=admin_headers,
            json={
                "id": zone_id,
                "camera_id": "town",
                "name": "Sync Test Zone",
                "type": "general",
                "polygon_points": initial_points,
            },
        )
        assert create_resp.status_code == 201, create_resp.text

        update_resp = api_client.put(
            f"/api/zones/{zone_id}",
            headers=admin_headers,
            json={
                "name": "Sync Test Zone Renamed",
                "type": "checkout_queue",
                "polygon_points": updated_points,
            },
        )
        assert update_resp.status_code == 200, update_resp.text
        updated = update_resp.json()
        assert updated["name"] == "Sync Test Zone Renamed"
        assert updated["type"] == "checkout_queue"
        assert updated["polygon_points"] == updated_points

        with session_scope() as session:
            shape = session.get(ZoneShape, zone_id)
            analytics = session.get(Zone, zone_id)
            assert shape is not None
            assert analytics is not None
            assert shape.name == analytics.name == "Sync Test Zone Renamed"
            assert shape.polygon_points == analytics.polygon_coords == updated_points
            assert analytics.zone_type == "queue"

        api_client.delete(f"/api/zones/{zone_id}", headers=admin_headers)

    def test_delete_soft_disables_analytics_zone(
        self, api_client: TestClient, admin_headers: dict
    ):
        zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        create_resp = api_client.post(
            "/api/zones",
            headers=admin_headers,
            json={
                "id": zone_id,
                "camera_id": "town",
                "name": "Delete Sync Zone",
                "type": "entrance",
                "polygon_points": [[0, 0], [10, 0], [10, 10]],
            },
        )
        assert create_resp.status_code == 201, create_resp.text

        with session_scope() as session:
            assert session.get(ZoneShape, zone_id) is not None
            assert session.get(Zone, zone_id) is not None

        delete_resp = api_client.delete(f"/api/zones/{zone_id}", headers=admin_headers)
        assert delete_resp.status_code == 204

        with session_scope() as session:
            shape = session.get(ZoneShape, zone_id)
            analytics = session.get(Zone, zone_id)
            assert shape is not None
            assert analytics is not None
            assert shape.status == "disabled"
            assert analytics.status == "disabled"

        list_resp = api_client.get("/api/zones", headers=admin_headers)
        assert list_resp.status_code == 200
        assert zone_id not in {z["id"] for z in list_resp.json()}

        include_resp = api_client.get(
            "/api/zones",
            headers=admin_headers,
            params={"include_disabled": True},
        )
        assert include_resp.status_code == 200
        disabled = next(z for z in include_resp.json() if z["id"] == zone_id)
        assert disabled["status"] == "disabled"

    def test_delete_soft_disables_zone_preserves_zone_metrics(
        self, api_client: TestClient, admin_headers: dict
    ):
        """Soft-deleting a queue zone must keep zone_metrics rows queryable."""
        zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)

        create_resp = api_client.post(
            "/api/zones",
            headers=admin_headers,
            json={
                "id": zone_id,
                "camera_id": "town",
                "name": "Queue Metrics Soft Delete",
                "type": "checkout_queue",
                "polygon_points": [[0, 0], [10, 0], [10, 10]],
            },
        )
        assert create_resp.status_code == 201, create_resp.text

        with session_scope() as session:
            zone = session.get(Zone, zone_id)
            assert zone is not None
            assert zone.zone_type == "queue"
            session.add(
                ZoneMetric(
                    zone_id=zone_id,
                    metric_date=yesterday,
                    hour=12,
                    visitors=42,
                    avg_dwell=30.0,
                    max_dwell=90.0,
                    min_dwell=5.0,
                    dwell_count=6,
                )
            )

        delete_resp = api_client.delete(f"/api/zones/{zone_id}", headers=admin_headers)
        assert delete_resp.status_code == 204, delete_resp.text

        with session_scope() as session:
            shape = session.get(ZoneShape, zone_id)
            analytics = session.get(Zone, zone_id)
            assert shape is not None
            assert analytics is not None
            assert shape.status == "disabled"
            assert analytics.status == "disabled"
            metrics = session.exec(
                select(ZoneMetric).where(ZoneMetric.zone_id == zone_id)
            ).all()
            assert len(metrics) == 1
            assert metrics[0].visitors == 42

        list_resp = api_client.get("/api/zones", headers=admin_headers)
        assert zone_id not in {z["id"] for z in list_resp.json()}

        include_resp = api_client.get(
            "/api/zones",
            headers=admin_headers,
            params={"include_disabled": True},
        )
        assert any(z["id"] == zone_id for z in include_resp.json())

    def test_processing_run_excludes_disabled_zone(
        self, api_client: TestClient, admin_headers: dict
    ):
        from backend.app.services.camera_process import claim_processing_run

        camera_resp = api_client.post(
            "/api/cameras",
            headers=admin_headers,
            json={
                "store_id": STORE_ID,
                "name": f"Recorded {uuid.uuid4().hex[:8]}",
                "location": "Test",
                "rtsp_url": "sample-data/checkout.mp4",
                "source_type": "recorded",
            },
        )
        assert camera_resp.status_code == 201, camera_resp.text
        camera_id = camera_resp.json()["id"]

        active_zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        disabled_zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        for zone_id, name in (
            (active_zone_id, "Active Zone"),
            (disabled_zone_id, "Disabled Zone"),
        ):
            resp = api_client.post(
                "/api/zones",
                headers=admin_headers,
                json={
                    "id": zone_id,
                    "camera_id": camera_id,
                    "name": name,
                    "type": "general",
                    "polygon_points": [[0, 0], [10, 0], [10, 10]],
                },
            )
            assert resp.status_code == 201, resp.text

        delete_resp = api_client.delete(
            f"/api/zones/{disabled_zone_id}", headers=admin_headers
        )
        assert delete_resp.status_code == 204

        run_id = claim_processing_run(camera_id)
        with session_scope() as session:
            run = session.get(ProcessingRun, run_id)
            assert run is not None
            snapshot_ids = {z["id"] for z in run.zones_snapshot}
            assert active_zone_id in snapshot_ids
            assert disabled_zone_id not in snapshot_ids

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


class TestZoneAlertRuleProvisioning:
    """Module 15 Phase 6 — alert_rules auto-provision on zone creation."""

    def _org_default(
        self, api_client: TestClient, admin_headers: dict, rule_type: str
    ) -> dict:
        listing = api_client.get("/api/admin/alert-rules", headers=admin_headers)
        assert listing.status_code == 200
        return next(
            r
            for r in listing.json()
            if r["rule_type"] == rule_type and r["zone_id"] is None and r["store_id"] is None
        )

    def _zone_rules(
        self, api_client: TestClient, admin_headers: dict, zone_id: str
    ) -> list[dict]:
        listing = api_client.get("/api/admin/alert-rules", headers=admin_headers)
        assert listing.status_code == 200
        return [r for r in listing.json() if r["zone_id"] == zone_id]

    def _create_zone(
        self,
        api_client: TestClient,
        admin_headers: dict,
        zone_id: str,
        zone_type: str,
    ) -> None:
        resp = api_client.post(
            "/api/zones",
            headers=admin_headers,
            json={
                "id": zone_id,
                "camera_id": "town",
                "name": "Provision Test Zone",
                "type": zone_type,
                "polygon_points": [[0, 0], [10, 0], [10, 10]],
            },
        )
        assert resp.status_code == 201, resp.text

    def test_create_general_zone_provisions_dwell_from_org_default(
        self, api_client: TestClient, admin_headers: dict
    ):
        org_dwell = self._org_default(api_client, admin_headers, "DWELL_THRESHOLD")
        zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        self._create_zone(api_client, admin_headers, zone_id, "general")

        rules = self._zone_rules(api_client, admin_headers, zone_id)
        dwell = next(r for r in rules if r["rule_type"] == "DWELL_THRESHOLD")
        assert dwell["threshold"] == org_dwell["threshold"]
        assert dwell["severity"] == org_dwell["severity"]
        assert dwell["enabled"] == org_dwell["enabled"]
        assert not any(r["rule_type"] == "OCCUPANCY_THRESHOLD" for r in rules)
        assert not any(r["rule_type"] == "QUEUE_THRESHOLD" for r in rules)

        api_client.delete(f"/api/zones/{zone_id}", headers=admin_headers)

    def test_create_queue_zone_provisions_queue_rules_from_org_defaults(
        self, api_client: TestClient, admin_headers: dict
    ):
        org_dwell = self._org_default(api_client, admin_headers, "DWELL_THRESHOLD")
        org_queue = self._org_default(api_client, admin_headers, "QUEUE_THRESHOLD")
        org_duration = self._org_default(
            api_client, admin_headers, "QUEUE_THRESHOLD_DURATION"
        )
        zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        self._create_zone(api_client, admin_headers, zone_id, "checkout_queue")

        rules = self._zone_rules(api_client, admin_headers, zone_id)
        dwell = next(r for r in rules if r["rule_type"] == "DWELL_THRESHOLD")
        queue = next(r for r in rules if r["rule_type"] == "QUEUE_THRESHOLD")
        duration = next(r for r in rules if r["rule_type"] == "QUEUE_THRESHOLD_DURATION")

        assert dwell["threshold"] == org_dwell["threshold"]
        assert dwell["severity"] == org_dwell["severity"]
        assert queue["threshold"] == org_queue["threshold"]
        assert queue["severity"] == org_queue["severity"]
        assert duration["threshold"] == org_duration["threshold"]
        assert duration["severity"] == org_duration["severity"]
        assert not any(r["rule_type"] == "OCCUPANCY_THRESHOLD" for r in rules)

        api_client.delete(f"/api/zones/{zone_id}", headers=admin_headers)

    def test_delete_zone_soft_delete_preserves_alert_rules(
        self, api_client: TestClient, admin_headers: dict
    ):
        zone_id = f"zone_{uuid.uuid4().hex[:8]}"
        self._create_zone(api_client, admin_headers, zone_id, "general")
        assert len(self._zone_rules(api_client, admin_headers, zone_id)) >= 1

        delete = api_client.delete(f"/api/zones/{zone_id}", headers=admin_headers)
        assert delete.status_code == 204
        assert len(self._zone_rules(api_client, admin_headers, zone_id)) >= 1

        with session_scope() as session:
            zone = session.get(Zone, zone_id)
            assert zone is not None
            assert zone.status == "disabled"


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

    def test_delete_soft_disables_line_preserves_row(
        self, api_client: TestClient, admin_headers: dict
    ):
        line_id = f"line_{uuid.uuid4().hex[:8]}"
        create = api_client.post(
            "/api/lines",
            headers=admin_headers,
            json={
                "id": line_id,
                "camera_id": "entrance",
                "name": "Soft Delete Line",
                "point_a": {"x": 1, "y": 2},
                "point_b": {"x": 3, "y": 4},
                "direction": "left_is_inside",
            },
        )
        assert create.status_code == 201, create.text

        delete = api_client.delete(f"/api/lines/{line_id}", headers=admin_headers)
        assert delete.status_code == 204

        with session_scope() as session:
            row = session.get(CountingLine, line_id)
            assert row is not None
            assert row.status == "disabled"

        list_resp = api_client.get("/api/lines", headers=admin_headers)
        assert line_id not in {line["id"] for line in list_resp.json()}

        include_resp = api_client.get(
            "/api/lines",
            headers=admin_headers,
            params={"include_disabled": True},
        )
        assert include_resp.status_code == 200
        disabled = next(line for line in include_resp.json() if line["id"] == line_id)
        assert disabled["status"] == "disabled"

    def test_processing_run_excludes_disabled_line(
        self, api_client: TestClient, admin_headers: dict
    ):
        from backend.app.services.camera_process import claim_processing_run

        camera_resp = api_client.post(
            "/api/cameras",
            headers=admin_headers,
            json={
                "store_id": STORE_ID,
                "name": f"Recorded {uuid.uuid4().hex[:8]}",
                "location": "Test",
                "rtsp_url": "sample-data/checkout.mp4",
                "source_type": "recorded",
            },
        )
        assert camera_resp.status_code == 201, camera_resp.text
        camera_id = camera_resp.json()["id"]

        active_line_id = f"line_{uuid.uuid4().hex[:8]}"
        disabled_line_id = f"line_{uuid.uuid4().hex[:8]}"
        for line_id, name in (
            (active_line_id, "Active Line"),
            (disabled_line_id, "Disabled Line"),
        ):
            resp = api_client.post(
                "/api/lines",
                headers=admin_headers,
                json={
                    "id": line_id,
                    "camera_id": camera_id,
                    "name": name,
                    "point_a": {"x": 0, "y": 0},
                    "point_b": {"x": 10, "y": 0},
                    "direction": "left_is_inside",
                },
            )
            assert resp.status_code == 201, resp.text

        delete_resp = api_client.delete(
            f"/api/lines/{disabled_line_id}", headers=admin_headers
        )
        assert delete_resp.status_code == 204

        run_id = claim_processing_run(camera_id)
        with session_scope() as session:
            run = session.get(ProcessingRun, run_id)
            assert run is not None
            snapshot_ids = {line["id"] for line in run.lines_snapshot}
            assert active_line_id in snapshot_ids
            assert disabled_line_id not in snapshot_ids


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


class TestAdminAlertRules:
    def test_admin_can_list_alert_rules(self, api_client: TestClient, admin_headers: dict):
        resp = api_client.get("/api/admin/alert-rules", headers=admin_headers)
        assert resp.status_code == 200
        rules = resp.json()
        assert isinstance(rules, list)
        assert len(rules) >= 1
        assert any(r["rule_type"] == "OCCUPANCY_THRESHOLD" for r in rules)

    def test_admin_can_update_threshold(self, api_client: TestClient, admin_headers: dict):
        listing = api_client.get("/api/admin/alert-rules", headers=admin_headers)
        assert listing.status_code == 200
        rule = next(r for r in listing.json() if r["rule_type"] == "OCCUPANCY_THRESHOLD")
        rule_id = rule["id"]
        original_threshold = rule["threshold"]
        new_threshold = original_threshold + 1

        resp = api_client.put(
            f"/api/admin/alert-rules/{rule_id}",
            headers=admin_headers,
            json={
                "threshold": new_threshold,
                "severity": rule["severity"],
                "enabled": rule["enabled"],
            },
        )
        assert resp.status_code == 200
        assert resp.json()["threshold"] == new_threshold

        verify = api_client.get("/api/admin/alert-rules", headers=admin_headers)
        updated = next(r for r in verify.json() if r["id"] == rule_id)
        assert updated["threshold"] == new_threshold

        api_client.put(
            f"/api/admin/alert-rules/{rule_id}",
            headers=admin_headers,
            json={
                "threshold": original_threshold,
                "severity": rule["severity"],
                "enabled": rule["enabled"],
            },
        )

    def test_non_admin_forbidden(self, api_client: TestClient, user_headers: dict):
        resp = api_client.get("/api/admin/alert-rules", headers=user_headers)
        assert resp.status_code == 403

    def test_put_invalid_threshold_returns_422(
        self, api_client: TestClient, admin_headers: dict
    ):
        listing = api_client.get("/api/admin/alert-rules", headers=admin_headers)
        rule_id = listing.json()[0]["id"]
        resp = api_client.put(
            f"/api/admin/alert-rules/{rule_id}",
            headers=admin_headers,
            json={"threshold": 0, "severity": "warning", "enabled": True},
        )
        assert resp.status_code == 422


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
    def test_create_user_admin_and_user_roles_round_trip(
        self, api_client: TestClient, admin_headers: dict
    ):
        """Backend stores admin/user only; both roles persist and reload via GET."""
        for backend_role in ("admin", "user"):
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            create = api_client.post(
                "/api/users",
                headers=admin_headers,
                json={
                    "id": user_id,
                    "email": f"{user_id}@example.com",
                    "name": f"Role {backend_role}",
                    "role": backend_role,
                    "org_id": ORG_ID,
                    "password": "secret123",
                },
            )
            assert create.status_code == 201, create.text
            assert create.json()["role"] == backend_role

            listing = api_client.get("/api/users", headers=admin_headers)
            assert listing.status_code == 200
            row = next(u for u in listing.json() if u["id"] == user_id)
            assert row["role"] == backend_role

            api_client.delete(f"/api/users/{user_id}", headers=admin_headers)

    def test_database_user_roles_are_admin_or_user_only(self):
        with session_scope() as session:
            roles = {row for row in session.exec(select(User.role)).all()}
        assert roles.issubset({"admin", "user"})
        assert "viewer" not in roles
        assert "manager" not in roles

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

    def test_created_user_logs_in_with_own_password_not_default(
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
                "name": "Own Password User",
                "role": "user",
                "org_id": ORG_ID,
                "password": "correct-horse-battery-staple",
            },
        )
        assert create.status_code == 201

        # Regression: login previously ignored password_hash entirely and only
        # accepted the shared API_DEFAULT_PASSWORD, making per-user passwords
        # (and reset-password) functionally inert.
        wrong = api_client.post(
            "/api/auth/login", json={"email": email, "password": "demo"}
        )
        assert wrong.status_code == 401

        right = api_client.post(
            "/api/auth/login",
            json={"email": email, "password": "correct-horse-battery-staple"},
        )
        assert right.status_code == 200, right.text

        api_client.delete(f"/api/users/{user_id}", headers=admin_headers)

    def test_reset_password_changes_login_credential(
        self, api_client: TestClient, admin_headers: dict
    ):
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        email = f"{user_id}@example.com"
        api_client.post(
            "/api/users",
            headers=admin_headers,
            json={
                "id": user_id,
                "email": email,
                "name": "Reset Target",
                "role": "user",
                "org_id": ORG_ID,
                "password": "old-password",
            },
        )

        reset = api_client.post(
            f"/api/users/{user_id}/reset-password",
            headers=admin_headers,
            json={"new_password": "brand-new-password"},
        )
        assert reset.status_code == 204

        stale = api_client.post(
            "/api/auth/login", json={"email": email, "password": "old-password"}
        )
        assert stale.status_code == 401

        fresh = api_client.post(
            "/api/auth/login", json={"email": email, "password": "brand-new-password"}
        )
        assert fresh.status_code == 200, fresh.text

        api_client.delete(f"/api/users/{user_id}", headers=admin_headers)

    def test_deleted_user_token_immediately_rejected(
        self, api_client: TestClient, admin_headers: dict
    ):
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        email = f"{user_id}@example.com"
        api_client.post(
            "/api/users",
            headers=admin_headers,
            json={
                "id": user_id,
                "email": email,
                "name": "Revoke Target",
                "role": "user",
                "org_id": ORG_ID,
                "password": "whatever-password",
            },
        )

        login = api_client.post(
            "/api/auth/login", json={"email": email, "password": "whatever-password"}
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        assert api_client.get("/api/cameras", headers=headers).status_code == 200

        delete = api_client.delete(f"/api/users/{user_id}", headers=admin_headers)
        assert delete.status_code == 204

        # Regression: get_current_user previously only decoded the JWT and
        # never re-checked the DB, so a deleted user's existing token kept
        # working until it naturally expired.
        after_delete = api_client.get("/api/cameras", headers=headers)
        assert after_delete.status_code == 401

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
