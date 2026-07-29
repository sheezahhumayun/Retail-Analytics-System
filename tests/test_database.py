"""Tests for Module 11 — database and event storage."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func
from sqlmodel import select

from analytics.counting.types import CrossingEvent, EventType
from analytics.dwell.types import DwellCloseReason, DwellEvent
from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, AnalyticsEventType, EventBus
from analytics.events.adapters import crossing_to_analytics
from analytics.zones.types import Zone, ZoneEvent, ZoneEventType, ZoneType
from database.cleanup import prune_raw_events
from database.models import (
    DwellEventRow,
    Event,
    OccupancyMetric,
    Organization,
    Store,
    VisitorMetric,
    Zone as DbZone,
    ZoneMetric,
)
from database.seed import ORG_ID, STORE_ID, seed_reference_data
from database.session import create_all, reset_engine, session_scope
from database.writer import AnalyticsDbWriter, DbWriterConfig, visitors_by_hour_yesterday

pytestmark = pytest.mark.database

# Isolated test ids — avoid colliding with seed / pipeline data on a shared dev DB.
TEST_ZONE_ID = "test_promo"
TEST_CAMERA_ID = "entrance"
TEST_TRACK_ENTER = 88001
TEST_TRACK_EXIT = 88002
TEST_TRACK_ZONE = 88005

GENERAL_ZONE = Zone(
    zone_id=TEST_ZONE_ID,
    zone_name="Test Promo",
    camera_id=TEST_CAMERA_ID,
    polygon_coordinates=((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)),
    zone_type=ZoneType.PROMOTIONAL,
)

# Far-future bucket unlikely to exist from seed or pipeline runs.
TEST_METRIC_TS = datetime(2099, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
# Latest timestamp for occupancy-reload tests (must sort after all other test writes).
RELOAD_TEST_TS = datetime(2099, 12, 31, 12, 0, 0, tzinfo=timezone.utc)


def _crossing(
    event_type: EventType,
    timestamp: float,
    *,
    track_id: int = TEST_TRACK_ENTER,
) -> CrossingEvent:
    return CrossingEvent(
        camera_id=TEST_CAMERA_ID,
        track_id=track_id,
        event_type=event_type,
        timestamp=timestamp,
        line_name="door",
    )


def _ensure_test_zone() -> None:
    with session_scope() as session:
        session.merge(
            DbZone(
                id=TEST_ZONE_ID,
                camera_id=TEST_CAMERA_ID,
                name="Test Promo",
                polygon_coords=[[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0]],
                zone_type="promotional",
                analytics_enabled=True,
            )
        )


@pytest.fixture(scope="module")
def db_ready():
    """Create schema and seed reference rows for integration tests."""
    try:
        create_all()
        seed_reference_data(force=True)
        _ensure_test_zone()
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")
    yield
    reset_engine()


@pytest.fixture
def writer(db_ready) -> AnalyticsDbWriter:
    _ensure_test_zone()
    return AnalyticsDbWriter(
        DbWriterConfig(
            store_id=STORE_ID,
            camera_store_map={TEST_CAMERA_ID: STORE_ID, "town": STORE_ID},
            zones=[GENERAL_ZONE],
        )
    )


class TestAnalyticsDbWriter:
    def test_entry_exit_persists_events_and_aggregates(self, writer: AnalyticsDbWriter):
        bus = EventBus()
        writer.subscribe(bus)
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(
                camera_ids=[TEST_CAMERA_ID],
                store_id=STORE_ID,
                db_writer=writer,
            ),
        )

        base = TEST_METRIC_TS.timestamp()
        with session_scope() as session:
            events_before = session.exec(
                select(func.count())
                .select_from(Event)
                .where(
                    Event.camera_id == TEST_CAMERA_ID,
                    Event.timestamp >= TEST_METRIC_TS,
                )
            ).one()
            vm_before = session.exec(
                select(VisitorMetric).where(
                    VisitorMetric.store_id == STORE_ID,
                    VisitorMetric.metric_date == TEST_METRIC_TS.date(),
                    VisitorMetric.hour == TEST_METRIC_TS.hour,
                )
            ).first()
            entries_before = vm_before.entries if vm_before else 0
            exits_before = vm_before.exits if vm_before else 0

        occ_before = writer._camera_occupancy.get(TEST_CAMERA_ID, 0)

        for i, tid in enumerate((TEST_TRACK_ENTER, TEST_TRACK_EXIT), start=0):
            bus.publish(crossing_to_analytics(_crossing(EventType.ENTRY, base + i, track_id=tid)))
        bus.publish(
            crossing_to_analytics(
                _crossing(EventType.EXIT, base + 10, track_id=TEST_TRACK_ENTER)
            )
        )

        occ = engine.camera_occupancy(TEST_CAMERA_ID)
        assert occ is not None
        assert occ.current_occupancy == 1

        with session_scope() as session:
            events_after = session.exec(
                select(func.count())
                .select_from(Event)
                .where(
                    Event.camera_id == TEST_CAMERA_ID,
                    Event.timestamp >= TEST_METRIC_TS,
                )
            ).one()
            assert events_after - events_before == 3

            vm = session.exec(
                select(VisitorMetric).where(
                    VisitorMetric.store_id == STORE_ID,
                    VisitorMetric.metric_date == TEST_METRIC_TS.date(),
                    VisitorMetric.hour == TEST_METRIC_TS.hour,
                )
            ).one()
            assert vm.entries - entries_before == 2
            assert vm.exits - exits_before == 1

            occ_row = session.exec(
                select(OccupancyMetric)
                .where(
                    OccupancyMetric.camera_id == TEST_CAMERA_ID,
                    OccupancyMetric.timestamp >= TEST_METRIC_TS,
                )
                .order_by(OccupancyMetric.id.desc())  # type: ignore[attr-defined]
            ).first()
            assert occ_row is not None
            assert occ_row.current_occupancy == occ_before + 1

    def test_zone_enter_and_dwell_persist(self, writer: AnalyticsDbWriter):
        bus = EventBus()
        writer.subscribe(bus)
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(
                camera_ids=[TEST_CAMERA_ID],
                zones=[GENERAL_ZONE],
                store_id=STORE_ID,
                db_writer=writer,
            ),
        )

        enter_ts = TEST_METRIC_TS.timestamp()
        exit_ts = enter_ts + 60.0

        with session_scope() as session:
            dwells_before = session.exec(
                select(func.count())
                .select_from(DwellEventRow)
                .where(
                    DwellEventRow.zone_id == TEST_ZONE_ID,
                    DwellEventRow.track_id == str(TEST_TRACK_ZONE),
                )
            ).one()

        engine.process_zone_event(
            ZoneEvent(
                camera_id=TEST_CAMERA_ID,
                zone_id=TEST_ZONE_ID,
                zone_name="Test Promo",
                track_id=TEST_TRACK_ZONE,
                event_type=ZoneEventType.ZONE_ENTER,
                timestamp=enter_ts,
            )
        )
        engine.process_zone_event(
            ZoneEvent(
                camera_id=TEST_CAMERA_ID,
                zone_id=TEST_ZONE_ID,
                zone_name="Test Promo",
                track_id=TEST_TRACK_ZONE,
                event_type=ZoneEventType.ZONE_EXIT,
                timestamp=exit_ts,
            )
        )

        with session_scope() as session:
            dwells_after = session.exec(
                select(func.count())
                .select_from(DwellEventRow)
                .where(
                    DwellEventRow.zone_id == TEST_ZONE_ID,
                    DwellEventRow.track_id == str(TEST_TRACK_ZONE),
                )
            ).one()
            assert dwells_after - dwells_before == 1

            dwell = session.exec(
                select(DwellEventRow).where(
                    DwellEventRow.zone_id == TEST_ZONE_ID,
                    DwellEventRow.track_id == str(TEST_TRACK_ZONE),
                )
            ).first()
            assert dwell is not None
            assert dwell.dwell_seconds == pytest.approx(60.0)

            zm = session.exec(
                select(ZoneMetric).where(
                    ZoneMetric.zone_id == TEST_ZONE_ID,
                    ZoneMetric.metric_date == TEST_METRIC_TS.date(),
                    ZoneMetric.hour == TEST_METRIC_TS.hour,
                )
            ).one()
            assert zm.visitors >= 1
            assert zm.dwell_count >= dwells_after - dwells_before

    def test_person_detected_not_persisted_by_default(self, writer: AnalyticsDbWriter):
        from analytics.events.adapters import person_detected_to_analytics
        from inference.detection.types import Detection

        bus = EventBus()
        writer.subscribe(bus)

        with session_scope() as session:
            before = session.exec(
                select(func.count())
                .select_from(Event)
                .where(Event.event_type == AnalyticsEventType.PERSON_DETECTED.value)
            ).one()

        det = Detection(
            bbox=(1.0, 2.0, 3.0, 4.0),
            confidence=0.9,
            class_id=0,
            class_name="person",
            timestamp=TEST_METRIC_TS.timestamp(),
            camera_id=TEST_CAMERA_ID,
        )
        bus.publish(person_detected_to_analytics(det))

        with session_scope() as session:
            after = session.exec(
                select(func.count())
                .select_from(Event)
                .where(Event.event_type == AnalyticsEventType.PERSON_DETECTED.value)
            ).one()
            assert after == before

    def test_occupancy_reloads_from_db_on_writer_restart(self, writer: AnalyticsDbWriter):
        with session_scope() as session:
            session.add(
                OccupancyMetric(
                    camera_id=TEST_CAMERA_ID,
                    store_id=None,
                    timestamp=RELOAD_TEST_TS,
                    current_occupancy=7,
                )
            )
            session.add(
                OccupancyMetric(
                    camera_id=None,
                    store_id=STORE_ID,
                    timestamp=RELOAD_TEST_TS,
                    current_occupancy=7,
                )
            )

        reloaded = AnalyticsDbWriter(
            DbWriterConfig(
                store_id=STORE_ID,
                camera_store_map={TEST_CAMERA_ID: STORE_ID},
                zones=[GENERAL_ZONE],
            )
        )
        assert reloaded._camera_occupancy[TEST_CAMERA_ID] == 7
        assert reloaded._store_occupancy == 7


class TestRetention:
    def test_prune_old_events(self, db_ready):
        old_ts = datetime.now(timezone.utc) - timedelta(days=120)
        with session_scope() as session:
            session.add(
                Event(
                    camera_id=TEST_CAMERA_ID,
                    event_type="ENTRY",
                    timestamp=old_ts,
                    track_id="99999",
                )
            )
            session.commit()

        with session_scope() as session:
            deleted = prune_raw_events(session, retention_days=90)
            assert deleted >= 1


class TestSeedAndQueries:
    def test_seed_creates_org_hierarchy(self, db_ready):
        with session_scope() as session:
            assert session.get(Organization, ORG_ID) is not None
            assert session.get(Store, STORE_ID) is not None

    def test_visitors_by_hour_yesterday(self, db_ready):
        with session_scope() as session:
            rows = visitors_by_hour_yesterday(session, STORE_ID)
            assert rows
            assert sum(r["entries"] for r in rows) > 0


class TestDwellPersistenceDirect:
    def test_on_dwell_event(self, writer: AnalyticsDbWriter):
        enter_dt = RELOAD_TEST_TS.replace(hour=13)
        enter_ts = enter_dt.timestamp()
        exit_ts = enter_ts + 30.0
        track_id = 88099

        with session_scope() as session:
            before = session.exec(
                select(func.count())
                .select_from(DwellEventRow)
                .where(
                    DwellEventRow.zone_id == TEST_ZONE_ID,
                    DwellEventRow.track_id == str(track_id),
                    DwellEventRow.enter_ts == enter_dt,
                )
            ).one()

        writer.on_dwell_event(
            DwellEvent(
                camera_id=TEST_CAMERA_ID,
                zone_id=TEST_ZONE_ID,
                zone_name="Test Promo",
                track_id=track_id,
                enter_timestamp=enter_ts,
                exit_timestamp=exit_ts,
                dwell_seconds=30.0,
                close_reason=DwellCloseReason.EXIT,
            )
        )
        with session_scope() as session:
            after = session.exec(
                select(func.count())
                .select_from(DwellEventRow)
                .where(
                    DwellEventRow.zone_id == TEST_ZONE_ID,
                    DwellEventRow.track_id == str(track_id),
                    DwellEventRow.enter_ts == enter_dt,
                )
            ).one()
            assert after - before == 1

            row = session.exec(
                select(DwellEventRow)
                .where(
                    DwellEventRow.zone_id == TEST_ZONE_ID,
                    DwellEventRow.track_id == str(track_id),
                    DwellEventRow.enter_ts == enter_dt,
                )
                .order_by(DwellEventRow.id.desc())  # type: ignore[attr-defined]
            ).first()
            assert row is not None
            assert row.dwell_seconds == pytest.approx(30.0)
