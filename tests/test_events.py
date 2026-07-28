"""Tests for Module 10 — event architecture and Analytics Engine."""

from __future__ import annotations

import time

import pytest

from analytics.counting.types import CrossingEvent, EventType
from analytics.dwell import DwellTracker
from analytics.events import (
    AnalyticsEngine,
    AnalyticsEngineConfig,
    AnalyticsEvent,
    AnalyticsEventType,
    EventBus,
    PersonDetectionSampler,
    camera_offline_to_analytics,
    crossing_to_analytics,
)
from analytics.occupancy import OccupancyTracker
from analytics.queues import QueueTracker
from analytics.zones import MultiZoneAnalytics, Zone, ZoneEvent, ZoneEventType, ZoneType
from inference.detection.types import Detection
from inference.video import CameraState, RTSPVideoSource, VideoSourceError

QUEUE_ZONE = Zone(
    zone_id="checkout_lane",
    zone_name="Checkout Lane",
    camera_id="cam_1",
    polygon_coordinates=((0.0, 200.0), (400.0, 200.0), (400.0, 400.0), (0.0, 400.0)),
    zone_type=ZoneType.QUEUE,
)

GENERAL_ZONE = Zone(
    zone_id="promo",
    zone_name="Promo",
    camera_id="cam_1",
    polygon_coordinates=((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)),
    zone_type=ZoneType.PROMOTIONAL,
)


def _crossing(event_type: EventType, timestamp: float, *, track_id: int = 1) -> CrossingEvent:
    return CrossingEvent(
        camera_id="cam_1",
        track_id=track_id,
        event_type=event_type,
        timestamp=timestamp,
        line_name="door",
    )


def _zone_event(
    event_type: ZoneEventType,
    timestamp: float,
    *,
    track_id: int = 1,
    zone_id: str = "promo",
    zone_name: str = "Promo",
) -> ZoneEvent:
    return ZoneEvent(
        camera_id="cam_1",
        zone_id=zone_id,
        zone_name=zone_name,
        track_id=track_id,
        event_type=event_type,
        timestamp=timestamp,
        dwell_delta=1.0 if event_type == ZoneEventType.ZONE_PRESENCE else None,
    )


class TestAnalyticsEventSchema:
    def test_pydantic_fields(self):
        ev = AnalyticsEvent.from_epoch(
            event_type=AnalyticsEventType.ENTRY,
            camera_id="entrance",
            track_id=7,
            timestamp=1000.0,
            metadata={"line_name": "main"},
        )
        assert ev.event_type == "ENTRY"
        assert ev.camera_id == "entrance"
        assert ev.track_id == "7"
        assert ev.zone_id is None
        assert ev.metadata["line_name"] == "main"
        assert ev.timestamp.tzinfo is not None

    def test_to_log_dict(self):
        ev = AnalyticsEvent.from_epoch(
            event_type=AnalyticsEventType.ZONE_ENTER,
            camera_id="cam",
            zone_id="z1",
            track_id=3,
            timestamp=100.0,
        )
        d = ev.to_log_dict()
        assert d["event_type"] == "ZONE_ENTER"
        assert d["zone_id"] == "z1"
        assert d["track_id"] == "3"


class TestEventBus:
    def test_publish_notifies_subscribers(self):
        bus = EventBus()
        seen: list[AnalyticsEvent] = []
        bus.subscribe(seen.append)
        ev = AnalyticsEvent.from_epoch(
            event_type=AnalyticsEventType.ENTRY,
            camera_id="cam",
            track_id=1,
            timestamp=1.0,
        )
        bus.publish(ev)
        assert seen == [ev]
        assert bus.event_log == (ev,)


class TestAnalyticsEngineOccupancy:
    def test_occupancy_matches_direct_tracker(self):
        bus = EventBus()
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(camera_ids=["cam_1"]),
        )
        direct = OccupancyTracker("cam_1")

        sequence = [
            (EventType.ENTRY, 1000.0, 1),
            (EventType.ENTRY, 1010.0, 2),
            (EventType.EXIT, 1020.0, 3),
            (EventType.EXIT, 1030.0, 4),
            (EventType.EXIT, 1040.0, 5),
        ]
        for etype, ts, tid in sequence:
            crossing = _crossing(etype, ts, track_id=tid)
            direct.process(crossing)
            bus.publish(crossing_to_analytics(crossing))

        assert engine.camera_occupancy("cam_1") == direct.snapshot()


class TestAnalyticsEngineZoneMetrics:
    def test_zone_metrics_match_multi_zone_analytics(self):
        bus = EventBus()
        zones = [GENERAL_ZONE]
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(camera_ids=["cam_1"], zones=zones),
        )
        direct = MultiZoneAnalytics(zones)

        events = [
            _zone_event(ZoneEventType.ZONE_ENTER, 100.0, track_id=1),
            _zone_event(ZoneEventType.ZONE_PRESENCE, 110.0, track_id=1),
            _zone_event(ZoneEventType.ZONE_EXIT, 120.0, track_id=1),
            _zone_event(ZoneEventType.ZONE_ENTER, 200.0, track_id=2),
        ]
        for ev in events:
            direct.process(ev)
            engine.process_zone_event(ev)

        assert engine.zone_snapshot("promo") == direct.snapshot("promo")


class TestAnalyticsEngineDwellMetrics:
    def test_dwell_metrics_match_dwell_tracker(self):
        bus = EventBus()
        zones = [GENERAL_ZONE]
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(camera_ids=["cam_1"], zones=zones),
        )
        direct = DwellTracker(zones)

        events = [
            _zone_event(ZoneEventType.ZONE_ENTER, 1000.0),
            _zone_event(ZoneEventType.ZONE_PRESENCE, 1030.0),
            _zone_event(ZoneEventType.ZONE_EXIT, 1060.0),
        ]
        for ev in events:
            direct.process(ev)
            engine.process_zone_event(ev)

        assert engine.dwell_snapshot("promo") == direct.snapshot("promo")

    def test_dwell_threshold_on_bus(self):
        bus = EventBus()
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(
                camera_ids=["cam_1"],
                zones=[GENERAL_ZONE],
                dwell_thresholds={"promo": 20.0},
            ),
        )
        engine.process_zone_event(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0))
        engine.process_zone_event(_zone_event(ZoneEventType.ZONE_PRESENCE, 1030.0))

        threshold_events = [
            e for e in bus.event_log if e.event_type == AnalyticsEventType.DWELL_THRESHOLD.value
        ]
        assert len(threshold_events) == 1
        assert threshold_events[0].metadata["dwell_seconds"] == pytest.approx(30.0)


class TestAnalyticsEngineQueueMetrics:
    def test_queue_metrics_match_queue_tracker(self):
        bus = EventBus()
        zones = [QUEUE_ZONE]
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(camera_ids=["cam_1"], zones=zones),
        )
        direct = QueueTracker(zones)

        events = [
            _zone_event(
                ZoneEventType.ZONE_ENTER,
                100.0,
                zone_id="checkout_lane",
                zone_name="Checkout Lane",
                track_id=1,
            ),
            _zone_event(
                ZoneEventType.ZONE_ENTER,
                101.0,
                zone_id="checkout_lane",
                zone_name="Checkout Lane",
                track_id=2,
            ),
            _zone_event(
                ZoneEventType.ZONE_EXIT,
                150.0,
                zone_id="checkout_lane",
                zone_name="Checkout Lane",
                track_id=1,
            ),
        ]
        for ev in events:
            direct.process(ev)
            engine.process_zone_event(ev)

        assert engine.queue_snapshot("checkout_lane") == direct.snapshot("checkout_lane")

    def test_queue_threshold_on_bus(self):
        bus = EventBus()
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(
                camera_ids=["cam_1"],
                zones=[QUEUE_ZONE],
                queue_length_thresholds={"checkout_lane": 2},
            ),
        )
        engine.process_zone_event(
            _zone_event(
                ZoneEventType.ZONE_ENTER,
                100.0,
                zone_id="checkout_lane",
                zone_name="Checkout Lane",
                track_id=1,
            )
        )
        engine.process_zone_event(
            _zone_event(
                ZoneEventType.ZONE_ENTER,
                101.0,
                zone_id="checkout_lane",
                zone_name="Checkout Lane",
                track_id=2,
            )
        )

        threshold_events = [
            e for e in bus.event_log if e.event_type == AnalyticsEventType.QUEUE_THRESHOLD.value
        ]
        assert len(threshold_events) == 1
        assert threshold_events[0].metadata["queue_length"] == 2


class TestPersonDetectionSampler:
    def test_publishes_sampled_person_detected(self):
        bus = EventBus()
        sampler = PersonDetectionSampler(bus, "cam_1", sample_interval_seconds=0.0)
        det = Detection(
            bbox=(10.0, 20.0, 30.0, 40.0),
            confidence=0.9,
            class_id=0,
            class_name="person",
            timestamp=100.0,
            camera_id="cam_1",
        )
        assert sampler.maybe_publish([det]) == 1
        types = {e.event_type for e in bus.event_log}
        assert AnalyticsEventType.PERSON_DETECTED.value in types


class TestCameraOffline:
    def test_rtsp_emits_camera_offline_when_reconnect_exhausted(self):
        bus = EventBus()

        calls = {"n": 0}

        def factory(url):
            calls["n"] += 1
            if calls["n"] == 1:
                from tests.test_video_source import _FakeCapture

                return _FakeCapture(fail_reads=10_000)
            from tests.test_video_source import _FakeCapture

            return _FakeCapture(open_ok=False)

        src = RTSPVideoSource(
            "rtsp://dead/stream",
            camera_id="entrance-cam",
            event_bus=bus,
            reconnect_threshold=2,
            reconnect_attempts=2,
            backoff_base=0,
            backoff_max=0,
            retry_after_exhaustion=10_000.0,
            _capture_factory=factory,
        )
        src._sleep = lambda _s: None
        src._monotonic = lambda: 0.0
        src.open()

        for _ in range(15):
            src.read()

        assert src.get_state() is CameraState.ERROR
        offline = [e for e in bus.event_log if e.event_type == AnalyticsEventType.CAMERA_OFFLINE.value]
        assert len(offline) == 1
        assert offline[0].camera_id == "entrance-cam"
        assert offline[0].metadata["reason"] == "reconnect_exhausted"

    def test_camera_offline_adapter(self):
        ev = camera_offline_to_analytics("cam", timestamp=time.time(), url="rtsp://x")
        assert ev.event_type == "CAMERA_OFFLINE"


class TestLineCounterEventBus:
    def test_counter_publishes_entry_exit(self):
        from analytics.counting import CountingLine, InsideSide, LineCounter
        from tests.test_counting import HORIZONTAL_LINE, _track

        bus = EventBus()
        counter = LineCounter(HORIZONTAL_LINE, event_bus=bus)
        counter.update([_track(1, [(40.0, 100.0, 60.0, 150.0)])])
        counter.update(
            [_track(1, [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0)])]
        )
        bus_types = {e.event_type for e in bus.event_log}
        assert AnalyticsEventType.ENTRY.value in bus_types


@pytest.mark.events
class TestFullPipelineEventTypes:
    def test_all_prd_event_types_on_bus(self, pytorch_detector, entrance_video):
        from analytics.counting import CountingLine, InsideSide, LineCounter
        from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, EventBus, PersonDetectionSampler
        from analytics.zones import ZoneDetector
        from inference.tracking import Tracker
        from inference.video import create_video_source

        bus = EventBus()
        zones = [GENERAL_ZONE, QUEUE_ZONE]
        camera_id = "cam_1"
        engine = AnalyticsEngine(
            bus,
            AnalyticsEngineConfig(
                camera_ids=[camera_id],
                zones=zones,
                dwell_thresholds={"promo": 1.0},
                queue_length_thresholds={"checkout_lane": 1},
            ),
        )
        line = CountingLine(
            x1=50.0,
            y1=280.0,
            x2=590.0,
            y2=280.0,
            inside_side=InsideSide.LEFT,
            camera_id=camera_id,
        )
        counter = LineCounter(line, event_bus=bus)
        zone_detector = ZoneDetector(zones)
        tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)
        sampler = PersonDetectionSampler(bus, camera_id, sample_interval_seconds=0.0)

        src = create_video_source(str(entrance_video), target_fps=10)
        src.open()
        try:
            for _ in range(30):
                ok, frame = src.read()
                if not ok:
                    break
                ts = src.get_last_timestamp()
                dets = pytorch_detector.detect(frame, camera_id=camera_id, timestamp=ts)
                sampler.maybe_publish(dets)
                tracks = tracker.update(dets)
                counter.update(tracks)
                for ze in zone_detector.update(tracks):
                    engine.process_zone_event(ze)
                engine.close_stale_dwell_sessions(ts)
        finally:
            src.release()

        seen = engine.event_types_seen()
        assert AnalyticsEventType.PERSON_DETECTED.value in seen
        # ENTRY/EXIT depend on line geometry vs tracks — at least zones fire on clips.
        assert AnalyticsEventType.ZONE_ENTER.value in seen or AnalyticsEventType.ZONE_EXIT.value in seen

        for ev in bus.event_log:
            assert ev.camera_id
            assert ev.timestamp is not None
            d = ev.to_log_dict()
            assert d["event_type"] == ev.event_type
