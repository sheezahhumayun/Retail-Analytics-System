"""Tests for Module 9 — queue analytics (analytics/queues)."""

from __future__ import annotations

import json

import pytest

from analytics.queues import (
    QueueThresholdKind,
    QueueTracker,
    is_queue_zone,
)
from analytics.zones import Zone, ZoneEvent, ZoneEventType, ZoneType

QUEUE_ZONE = Zone(
    zone_id="checkout_lane",
    zone_name="Checkout Lane",
    camera_id="cam_1",
    polygon_coordinates=((0.0, 200.0), (400.0, 200.0), (400.0, 400.0), (0.0, 400.0)),
    zone_type=ZoneType.QUEUE,
)

GENERAL_ZONE = Zone(
    zone_id="floor",
    zone_name="Floor",
    camera_id="cam_1",
    polygon_coordinates=((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)),
    zone_type=ZoneType.GENERAL,
)


def _zone_event(
    event_type: ZoneEventType,
    timestamp: float,
    *,
    track_id: int = 1,
    zone_id: str = "checkout_lane",
) -> ZoneEvent:
    return ZoneEvent(
        camera_id="cam_1",
        zone_id=zone_id,
        zone_name="Checkout Lane",
        track_id=track_id,
        event_type=event_type,
        timestamp=timestamp,
        dwell_delta=1.0 if event_type == ZoneEventType.ZONE_PRESENCE else None,
    )


class TestQueueZoneTypes:
    def test_is_queue_zone_accepts_queue_checkout_waiting(self):
        assert is_queue_zone(QUEUE_ZONE) is True
        checkout = Zone(
            zone_id="c",
            zone_name="C",
            camera_id="cam",
            polygon_coordinates=((0, 0), (1, 0), (1, 1)),
            zone_type=ZoneType.CHECKOUT,
        )
        waiting = Zone(
            zone_id="w",
            zone_name="W",
            camera_id="cam",
            polygon_coordinates=((0, 0), (1, 0), (1, 1)),
            zone_type=ZoneType.WAITING,
        )
        assert is_queue_zone(checkout) is True
        assert is_queue_zone(waiting) is True
        assert is_queue_zone(GENERAL_ZONE) is False

    def test_queue_zone_type_enum_value(self):
        assert ZoneType.QUEUE.value == "queue"


class TestQueueTracker:
    def test_current_length_from_enter_exit(self):
        queues = QueueTracker([QUEUE_ZONE])
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 100.0, track_id=1))
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 101.0, track_id=2))
        result = queues.process(_zone_event(ZoneEventType.ZONE_EXIT, 110.0, track_id=1))

        assert result.metrics is not None
        assert result.metrics.current_queue_length == 1
        assert result.metrics.max_queue_length == 2

    def test_avg_queue_length_samples(self):
        queues = QueueTracker([QUEUE_ZONE])
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 100.0, track_id=1))
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 101.0, track_id=2))
        queues.process(_zone_event(ZoneEventType.ZONE_EXIT, 110.0, track_id=2))
        snap = queues.snapshot("checkout_lane")
        assert snap is not None
        assert snap.avg_queue_length == pytest.approx(4 / 3)
        assert snap.length_samples == 3

    def test_estimated_wait_from_completed_dwells(self):
        queues = QueueTracker([QUEUE_ZONE])
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 100.0, track_id=1))
        queues.process(_zone_event(ZoneEventType.ZONE_EXIT, 160.0, track_id=1))
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 200.0, track_id=2))
        queues.process(_zone_event(ZoneEventType.ZONE_EXIT, 260.0, track_id=2))

        snap = queues.snapshot("checkout_lane")
        assert snap is not None
        assert snap.estimated_wait_seconds == pytest.approx(60.0)
        assert snap.completed_wait_samples == 2

    def test_queue_duration_episode(self):
        queues = QueueTracker([QUEUE_ZONE])
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 100.0, track_id=1))
        result = queues.process(
            _zone_event(ZoneEventType.ZONE_PRESENCE, 145.0, track_id=1)
        )
        assert result.metrics is not None
        assert result.metrics.queue_duration_seconds == pytest.approx(45.0)

        queues.process(_zone_event(ZoneEventType.ZONE_EXIT, 150.0, track_id=1))
        cleared = queues.snapshot("checkout_lane")
        assert cleared is not None
        assert cleared.current_queue_length == 0
        assert cleared.queue_duration_seconds == 0.0

    def test_length_threshold_fires_once_until_below(self):
        queues = QueueTracker(
            [QUEUE_ZONE],
            length_thresholds={"checkout_lane": 2},
        )
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 100.0, track_id=1))
        r1 = queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 101.0, track_id=2))
        assert len(r1.threshold_events) == 1
        assert r1.threshold_events[0].threshold_kind == QueueThresholdKind.LENGTH
        assert r1.threshold_events[0].queue_length == 2

        r2 = queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 102.0, track_id=3))
        assert r2.threshold_events == ()

        queues.process(_zone_event(ZoneEventType.ZONE_EXIT, 110.0, track_id=1))
        queues.process(_zone_event(ZoneEventType.ZONE_EXIT, 111.0, track_id=2))
        below = queues.process(_zone_event(ZoneEventType.ZONE_EXIT, 112.0, track_id=3))
        assert below.metrics is not None
        assert below.metrics.current_queue_length == 0

        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 200.0, track_id=4))
        refire = queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 201.0, track_id=5))
        assert len(refire.threshold_events) == 1

    def test_duration_threshold_fires_once_per_episode(self):
        queues = QueueTracker(
            [QUEUE_ZONE],
            duration_thresholds={"checkout_lane": 30.0},
        )
        queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 100.0, track_id=1))
        queues.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 120.0, track_id=1))
        r1 = queues.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 135.0, track_id=1))
        assert len(r1.threshold_events) == 1
        assert r1.threshold_events[0].threshold_kind == QueueThresholdKind.DURATION

        r2 = queues.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 140.0, track_id=1))
        assert r2.threshold_events == ()

    def test_threshold_event_to_dict(self):
        queues = QueueTracker(
            [QUEUE_ZONE],
            length_thresholds={"checkout_lane": 1},
        )
        result = queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 100.0))
        d = result.threshold_events[0].to_dict()
        assert d["event_type"] == "QUEUE_THRESHOLD"
        assert d["threshold_kind"] == "length"
        assert json.loads(json.dumps(d)) == d

    def test_ignores_non_queue_zones(self):
        queues = QueueTracker([GENERAL_ZONE])
        assert queues.zone_ids == ()
        result = queues.process(_zone_event(ZoneEventType.ZONE_ENTER, 100.0, zone_id="floor"))
        assert result.metrics is None


@pytest.mark.queues
class TestQueueIntegration:
    def test_zone_detector_to_queue_tracker(self, pytorch_detector, checkout_video):
        from analytics.zones import ZoneDetector
        from inference.tracking import Tracker
        from inference.video import create_video_source

        zone = Zone(
            zone_id="checkout_area",
            zone_name="Checkout",
            camera_id="checkout",
            polygon_coordinates=((50.0, 100.0), (590.0, 100.0), (590.0, 350.0), (50.0, 350.0)),
            zone_type=ZoneType.CHECKOUT,
        )
        detector = ZoneDetector([zone], hysteresis_frames=2)
        queues = QueueTracker([zone], length_thresholds={"checkout_area": 1})
        tracker = Tracker(camera_id="checkout", min_confirmation_frames=2)

        src = create_video_source(str(checkout_video), target_fps=10)
        src.open()
        for _ in range(30):
            ok, frame = src.read()
            if not ok:
                break
            ts = src.get_last_timestamp()
            dets = pytorch_detector.detect(frame, camera_id="checkout", timestamp=ts)
            for ev in detector.update(tracker.update(dets)):
                queues.process(ev)
        src.release()

        snap = queues.snapshot("checkout_area")
        assert snap is not None
        assert snap.length_samples >= 0
