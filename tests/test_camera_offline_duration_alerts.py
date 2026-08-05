"""Tests for CAMERA_OFFLINE_DURATION health-worker alerting."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlmodel import select

from backend.app.services.camera_health import (
    CAMERA_OFFLINE_DURATION_ALERT_TYPE,
    evaluate_camera_offline_duration_alerts,
)
from database.models import Alert, AlertRule, Camera
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope

pytestmark = [pytest.mark.database]

RULE_TYPE = "CAMERA_OFFLINE_DURATION"
TEST_CAMERA_ID = "test_offline_duration_cam"
THRESHOLD_SECONDS = 300.0


@pytest.fixture(scope="module")
def seeded_db():
    try:
        create_all()
        seed_reference_data(force=True)
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")
    yield
    reset_engine()


@pytest.fixture(autouse=True)
def cleanup_test_rows(seeded_db):
    with session_scope() as session:
        for alert in session.exec(
            select(Alert).where(Alert.camera_id == TEST_CAMERA_ID)
        ).all():
            session.delete(alert)
        cam = session.get(Camera, TEST_CAMERA_ID)
        if cam is not None:
            session.delete(cam)
        for rule in session.exec(
            select(AlertRule).where(AlertRule.rule_type == RULE_TYPE)
        ).all():
            if rule.camera_id == TEST_CAMERA_ID or rule.store_id == STORE_ID:
                session.delete(rule)
    yield
    with session_scope() as session:
        for alert in session.exec(
            select(Alert).where(Alert.camera_id == TEST_CAMERA_ID)
        ).all():
            session.delete(alert)
        cam = session.get(Camera, TEST_CAMERA_ID)
        if cam is not None:
            session.delete(cam)
        for rule in session.exec(
            select(AlertRule).where(AlertRule.rule_type == RULE_TYPE)
        ).all():
            if rule.camera_id == TEST_CAMERA_ID or rule.store_id == STORE_ID:
                session.delete(rule)


def _seed_org_rule(session, threshold: float = THRESHOLD_SECONDS) -> None:
    session.add(
        AlertRule(
            rule_type=RULE_TYPE,
            store_id=None,
            zone_id=None,
            camera_id=None,
            threshold=threshold,
            severity="critical",
            enabled=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    )
    session.flush()


def _upsert_test_camera(
    session,
    *,
    status: str,
    status_changed_at: datetime,
) -> Camera:
    camera = Camera(
        id=TEST_CAMERA_ID,
        store_id=STORE_ID,
        name="Offline duration test cam",
        rtsp_url="rtsp://demo.local/offline-test",
        source_type="live",
        status=status,
        status_changed_at=status_changed_at,
    )
    session.merge(camera)
    session.flush()
    return camera


class TestCameraOfflineDurationAlerts:
    def test_creates_alert_when_down_past_threshold(self, seeded_db):
        past = datetime.now(timezone.utc) - timedelta(seconds=THRESHOLD_SECONDS + 60)

        with session_scope() as session:
            _seed_org_rule(session)
            _upsert_test_camera(session, status="error", status_changed_at=past)
            created = evaluate_camera_offline_duration_alerts(session)

        assert created == 1

        with session_scope() as session:
            alert = session.exec(
                select(Alert).where(
                    Alert.camera_id == TEST_CAMERA_ID,
                    Alert.alert_type == CAMERA_OFFLINE_DURATION_ALERT_TYPE,
                    Alert.status == "open",
                )
            ).one()
            assert alert.severity == "critical"
            assert alert.metadata_["threshold_seconds"] == THRESHOLD_SECONDS

    def test_skips_when_open_alert_already_exists(self, seeded_db):
        past = datetime.now(timezone.utc) - timedelta(seconds=THRESHOLD_SECONDS + 60)
        now = datetime.now(timezone.utc)

        with session_scope() as session:
            _seed_org_rule(session)
            _upsert_test_camera(session, status="error", status_changed_at=past)
            session.add(
                Alert(
                    alert_type=CAMERA_OFFLINE_DURATION_ALERT_TYPE,
                    camera_id=TEST_CAMERA_ID,
                    zone_id=None,
                    timestamp=now,
                    severity="critical",
                    status="open",
                    metadata_={},
                )
            )
            session.flush()
            created = evaluate_camera_offline_duration_alerts(session)

        assert created == 0

        with session_scope() as session:
            count = len(
                session.exec(
                    select(Alert).where(
                        Alert.camera_id == TEST_CAMERA_ID,
                        Alert.alert_type == CAMERA_OFFLINE_DURATION_ALERT_TYPE,
                        Alert.status == "open",
                    )
                ).all()
            )
            assert count == 1

    def test_no_alert_when_under_threshold(self, seeded_db):
        recent = datetime.now(timezone.utc) - timedelta(seconds=60)

        with session_scope() as session:
            _seed_org_rule(session)
            _upsert_test_camera(session, status="offline", status_changed_at=recent)
            created = evaluate_camera_offline_duration_alerts(session)

        assert created == 0

        with session_scope() as session:
            alert = session.exec(
                select(Alert).where(Alert.camera_id == TEST_CAMERA_ID)
            ).first()
            assert alert is None
