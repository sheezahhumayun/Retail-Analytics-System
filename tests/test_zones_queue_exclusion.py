"""Test zone aggregation with queue zone exclusion."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from backend.app.main import app
from backend.app.services.analytics_read import read_zones_for_scope
from database.models import Zone, ZoneMetric
from database.seed import STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope

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
    return (datetime.now(timezone.utc).date() - timedelta(days=1)).isoformat()


class TestZoneAggregationQueueExclusion:
    """Test that queue zones are excluded from "all zones" aggregations at both camera and store levels."""

    def test_camera_level_excludes_queue_zones(self):
        """
        Scenario: A camera with 2 zones — one general ("floor_main"), one queue ("queue_lane").
        
        Expected:
        - "all zones" aggregation for that camera should equal general zone's data only
        - queue zone's data should NOT be included in the total
        """
        with session_scope() as session:
            # Get the shop camera with its zones
            zones = session.exec(
                select(Zone).where(Zone.camera_id == "shop")
            ).all()
            zone_ids = {z.id for z in zones}
            zone_types = {z.id: z.zone_type for z in zones}

            # Verify test precondition: shop has both general and queue zones
            assert "floor_main" in zone_ids, "floor_main zone not found"
            assert "queue_lane" in zone_ids, "queue_lane zone not found"
            assert zone_types["floor_main"] == "general"
            assert zone_types["queue_lane"] == "queue", f"Expected zone_type='queue', got '{zone_types['queue_lane']}'"

            # Create test data: metrics for both zones
            yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1))
            
            # General zone: 100 visitors
            session.add(
                ZoneMetric(
                    zone_id="floor_main",
                    metric_date=yesterday,
                    hour=12,
                    visitors=100,
                    avg_dwell=45.0,
                    max_dwell=120.0,
                    min_dwell=10.0,
                    dwell_count=20,
                )
            )
            
            # Queue zone: 316 visitors (this should NOT be included in camera-level "all zones")
            session.add(
                ZoneMetric(
                    zone_id="queue_lane",
                    metric_date=yesterday,
                    hour=12,
                    visitors=316,  # This makes the combined total 416 if not filtered
                    avg_dwell=20.0,
                    max_dwell=60.0,
                    min_dwell=5.0,
                    dwell_count=30,
                )
            )
            session.commit()

            # Now query camera-level "all zones" aggregation
            start = datetime.combine(yesterday, datetime.min.time(), tzinfo=timezone.utc)
            end = start + timedelta(hours=1)
            
            buckets, eligible = read_zones_for_scope(
                session,
                store_id=STORE_ID,
                camera_id="shop",
                zone_id=None,  # No specific zone — aggregate "all zones" for this camera
                start=start,
                end=end,
            )

            # The aggregation should only include floor_main (100 visitors)
            # NOT queue_lane (316 visitors)
            assert len(buckets) == 1, f"Expected 1 bucket, got {len(buckets)}"
            assert buckets[0].visitors == 100, (
                f"Camera-level 'all zones' should equal general zone only (100), "
                f"not general + queue (416). Got {buckets[0].visitors}."
            )

    def test_store_level_excludes_queue_zones(self):
        """
        Scenario: Store with multiple cameras, each with general and queue zones.
        
        Expected:
        - "all zones" aggregation across the store should exclude all queue zones
        - totals should reflect general zones only
        """
        with session_scope() as session:
            # Get all zones in the store
            all_zones = session.exec(
                select(Zone).where(Zone.camera_id.in_(["town", "shop"]))
            ).all()
            zone_types = {z.id: z.zone_type for z in all_zones}

            # Create test data: add metrics for all zones
            yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1))
            
            # Town zones (all general, no queue zones in this JSON, but adding for completeness)
            session.add(
                ZoneMetric(
                    zone_id="store1",
                    metric_date=yesterday,
                    hour=12,
                    visitors=50,
                    avg_dwell=40.0,
                    max_dwell=100.0,
                    min_dwell=10.0,
                    dwell_count=15,
                )
            )
            session.add(
                ZoneMetric(
                    zone_id="store2",
                    metric_date=yesterday,
                    hour=12,
                    visitors=75,
                    avg_dwell=45.0,
                    max_dwell=110.0,
                    min_dwell=12.0,
                    dwell_count=18,
                )
            )
            
            # Shop: floor_main (general) + queue_lane (queue that should be excluded)
            # Ensure queue_lane data exists (or re-use from previous test)
            # Check if metric already exists to avoid duplicate
            existing_queue = session.exec(
                select(ZoneMetric).where(
                    ZoneMetric.zone_id == "queue_lane",
                    ZoneMetric.metric_date == yesterday,
                    ZoneMetric.hour == 12,
                )
            ).first()
            if not existing_queue:
                session.add(
                    ZoneMetric(
                        zone_id="queue_lane",
                        metric_date=yesterday,
                        hour=12,
                        visitors=316,
                        avg_dwell=20.0,
                        max_dwell=60.0,
                        min_dwell=5.0,
                        dwell_count=30,
                    )
                )

            # Ensure floor_main data exists (or re-use from previous test)
            existing_floor = session.exec(
                select(ZoneMetric).where(
                    ZoneMetric.zone_id == "floor_main",
                    ZoneMetric.metric_date == yesterday,
                    ZoneMetric.hour == 12,
                )
            ).first()
            if not existing_floor:
                session.add(
                    ZoneMetric(
                        zone_id="floor_main",
                        metric_date=yesterday,
                        hour=12,
                        visitors=100,
                        avg_dwell=45.0,
                        max_dwell=120.0,
                        min_dwell=10.0,
                        dwell_count=20,
                    )
                )
            
            session.commit()

            # Query store-level "all zones" aggregation
            start = datetime.combine(yesterday, datetime.min.time(), tzinfo=timezone.utc)
            end = start + timedelta(hours=1)
            
            buckets, eligible = read_zones_for_scope(
                session,
                store_id=STORE_ID,
                camera_id=None,  # No specific camera — aggregate "all cameras, all zones" for the store
                zone_id=None,
                start=start,
                end=end,
            )

            # Expected total:
            # - store1: 50 (general)
            # - store2: 75 (general)
            # - floor_main: 100 (general)
            # - queue_lane: NOT included (queue type)
            # Total: 50 + 75 + 100 = 225
            
            assert len(buckets) == 1, f"Expected 1 bucket, got {len(buckets)}"
            expected_total = 50 + 75 + 100
            assert buckets[0].visitors == expected_total, (
                f"Store-level 'all zones' should exclude all queue zones. "
                f"Expected {expected_total} (general zones only), "
                f"got {buckets[0].visitors}."
            )

    def test_single_zone_query_not_affected_by_queue_filter(self):
        """
        Scenario: Query a specific queue zone directly (zone_id provided).
        
        Expected:
        - Single zone queries should NOT apply queue exclusion
        - Requesting queue_lane specifically should return its data
        """
        with session_scope() as session:
            yesterday = (datetime.now(timezone.utc).date() - timedelta(days=1))
            
            # Ensure queue_lane metric exists
            existing = session.exec(
                select(ZoneMetric).where(
                    ZoneMetric.zone_id == "queue_lane",
                    ZoneMetric.metric_date == yesterday,
                    ZoneMetric.hour == 12,
                )
            ).first()
            if not existing:
                session.add(
                    ZoneMetric(
                        zone_id="queue_lane",
                        metric_date=yesterday,
                        hour=12,
                        visitors=316,
                        avg_dwell=20.0,
                        max_dwell=60.0,
                        min_dwell=5.0,
                        dwell_count=30,
                    )
                )
                session.commit()

            # Query the queue zone directly
            start = datetime.combine(yesterday, datetime.min.time(), tzinfo=timezone.utc)
            end = start + timedelta(hours=1)
            
            buckets, eligible = read_zones_for_scope(
                session,
                store_id=STORE_ID,
                camera_id=None,
                zone_id="queue_lane",  # Specific zone query
                start=start,
                end=end,
            )

            # Single zone query should return its data, even if it's a queue zone
            assert len(buckets) == 1
            assert buckets[0].visitors == 316, (
                f"Single queue zone query should return queue zone's data (316), "
                f"not exclude it. Got {buckets[0].visitors}."
            )
