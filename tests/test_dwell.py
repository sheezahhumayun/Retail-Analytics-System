"""Tests for Module 7 — dwell-time analytics (analytics/dwell)."""
from __future__ import annotations

import json

import pytest

from analytics.dwell import (
    DwellCloseReason,
    DwellTracker,
    dwell_bucket,
    empty_distribution,
)
from analytics.zones import Zone, ZoneEvent, ZoneEventType


RECT_ZONE = Zone(
    zone_id="test_rect",
    zone_name="Test Rectangle",
    camera_id="cam_1",
    polygon_coordinates=((0.0, 200.0), (400.0, 200.0), (400.0, 400.0), (0.0, 400.0)),
)


def _zone_event(
    event_type: ZoneEventType,
    timestamp: float,
    *,
    track_id: int = 1,
    zone_id: str = "test_rect",
) -> ZoneEvent:
    return ZoneEvent(
        camera_id="cam_1",
        zone_id=zone_id,
        zone_name="Test Rectangle",
        track_id=track_id,
        event_type=event_type,
        timestamp=timestamp,
        dwell_delta=1.0 if event_type == ZoneEventType.ZONE_PRESENCE else None,
    )


class TestDwellBucket:
    def test_bucket_labels(self):
        assert dwell_bucket(15.0).value == "0-30s"
        assert dwell_bucket(45.0).value == "30-60s"
        assert dwell_bucket(120.0).value == "1-3min"
        assert dwell_bucket(300.0).value == "3-10min"
        assert dwell_bucket(900.0).value == "10min+"

    def test_empty_distribution_has_all_buckets(self):
        dist = empty_distribution()
        assert set(dist.keys()) == {
            "0-30s",
            "30-60s",
            "1-3min",
            "3-10min",
            "10min+",
        }
        assert sum(dist.values()) == 0


class TestDwellTracker:
    def test_enter_exit_emits_dwell_event(self):
        dwell = DwellTracker([RECT_ZONE])
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0))
        result = dwell.process(_zone_event(ZoneEventType.ZONE_EXIT, 1090.0))

        assert result.dwell_event is not None
        assert result.dwell_event.dwell_seconds == pytest.approx(90.0)
        assert result.dwell_event.close_reason == DwellCloseReason.EXIT
        assert result.dwell_event.enter_timestamp == 1000.0
        assert result.dwell_event.exit_timestamp == 1090.0

    def test_dwell_event_to_dict(self):
        dwell = DwellTracker([RECT_ZONE])
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0))
        result = dwell.process(_zone_event(ZoneEventType.ZONE_EXIT, 1030.0))
        d = result.dwell_event.to_dict()  # type: ignore[union-attr]
        assert d["dwell_seconds"] == 30.0
        assert d["close_reason"] == "exit"
        assert json.loads(json.dumps(d)) == d

    def test_aggregates_avg_median_max(self):
        dwell = DwellTracker([RECT_ZONE])
        visits = [(1000.0, 1030.0), (2000.0, 2120.0), (3000.0, 3180.0)]
        for enter, exit_ts in visits:
            dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, enter))
            dwell.process(_zone_event(ZoneEventType.ZONE_EXIT, exit_ts, track_id=1))

        snap = dwell.snapshot("test_rect")
        assert snap is not None
        assert snap.total_dwell_events == 3
        assert snap.avg_dwell_seconds == pytest.approx((30 + 120 + 180) / 3)
        assert snap.median_dwell_seconds == pytest.approx(120.0)
        assert snap.max_dwell_seconds == pytest.approx(180.0)

    def test_distribution_buckets(self):
        dwell = DwellTracker([RECT_ZONE])
        durations = [15.0, 45.0, 120.0, 300.0, 700.0]
        base = 1000.0
        for i, dur in enumerate(durations):
            enter = base + i * 1000
            dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, enter, track_id=i))
            dwell.process(
                _zone_event(ZoneEventType.ZONE_EXIT, enter + dur, track_id=i)
            )

        dist = dwell.snapshot("test_rect").distribution  # type: ignore[union-attr]
        assert dist["0-30s"] == 1
        assert dist["30-60s"] == 1
        assert dist["1-3min"] == 1
        assert dist["3-10min"] == 1
        assert dist["10min+"] == 1

    def test_track_loss_closes_with_last_seen(self):
        dwell = DwellTracker([RECT_ZONE], lost_track_timeout_seconds=5.0)
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0))
        dwell.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 1040.0))

        closed = dwell.close_stale_sessions(1046.0)
        assert len(closed) == 1
        assert closed[0].dwell_seconds == pytest.approx(40.0)
        assert closed[0].close_reason == DwellCloseReason.TRACK_LOST
        assert closed[0].exit_timestamp == 1040.0
        assert dwell.active_session_count() == 0

    def test_track_loss_not_before_timeout(self):
        dwell = DwellTracker([RECT_ZONE], lost_track_timeout_seconds=5.0)
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0))
        dwell.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 1040.0))
        assert dwell.close_stale_sessions(1044.0) == []
        assert dwell.active_session_count() == 1

    def test_threshold_fires_once_per_visit(self):
        dwell = DwellTracker([RECT_ZONE], dwell_thresholds={"test_rect": 60.0})
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0))

        r1 = dwell.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 1061.0))
        assert r1.threshold_event is not None
        assert r1.threshold_event.dwell_seconds == pytest.approx(61.0)
        assert r1.threshold_event.to_dict()["event_type"] == "DWELL_THRESHOLD"

        r2 = dwell.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 1100.0))
        assert r2.threshold_event is None

        r3 = dwell.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 1200.0))
        assert r3.threshold_event is None

    def test_threshold_not_fired_below_limit(self):
        dwell = DwellTracker([RECT_ZONE], dwell_thresholds={"test_rect": 60.0})
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0))
        result = dwell.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 1050.0))
        assert result.threshold_event is None

    def test_threshold_resets_on_new_visit(self):
        dwell = DwellTracker([RECT_ZONE], dwell_thresholds={"test_rect": 30.0})
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0))
        dwell.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 1035.0))
        dwell.process(_zone_event(ZoneEventType.ZONE_EXIT, 1040.0))

        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 2000.0))
        result = dwell.process(_zone_event(ZoneEventType.ZONE_PRESENCE, 2035.0))
        assert result.threshold_event is not None

    def test_active_sessions_count(self):
        dwell = DwellTracker([RECT_ZONE])
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0, track_id=1))
        dwell.process(_zone_event(ZoneEventType.ZONE_ENTER, 1000.0, track_id=2))
        snap = dwell.snapshot("test_rect")
        assert snap is not None
        assert snap.active_sessions == 2

        dwell.process(_zone_event(ZoneEventType.ZONE_EXIT, 1010.0, track_id=1))
        snap = dwell.snapshot("test_rect")
        assert snap is not None
        assert snap.active_sessions == 1


@pytest.mark.dwell
class TestDwellFromZonePipeline:
    def test_zone_events_drive_dwell(self):
        from analytics.zones import ZoneDetector
        from analytics.zones.types import ZoneEventType as ZT
        from inference.tracking import PositionRecord, TrackedObject

        zone = RECT_ZONE
        detector = ZoneDetector([zone], hysteresis_frames=1)

        def _track(track_id: int, bboxes: list[tuple[float, float, float, float]], base: float):
            history = tuple(
                PositionRecord(
                    center=((b[0] + b[2]) / 2, (b[1] + b[3]) / 2),
                    timestamp=base + i * 10.0,
                    bbox=b,
                )
                for i, b in enumerate(bboxes)
            )
            return TrackedObject(
                track_id=track_id,
                bbox=bboxes[-1],
                class_id=0,
                class_name="person",
                confidence=0.9,
                camera_id="cam_1",
                timestamp=base + (len(bboxes) - 1) * 10.0,
                position_history=history,
            )

        dwell = DwellTracker([zone], dwell_thresholds={"test_rect": 10.0})
        threshold_count = 0
        dwell_count = 0

        events = detector.update(
            [
                _track(
                    1,
                    [
                        (180.0, 250.0, 220.0, 320.0),
                        (185.0, 255.0, 225.0, 325.0),
                        (190.0, 260.0, 230.0, 330.0),
                        (180.0, 100.0, 220.0, 180.0),
                    ],
                    1000.0,
                )
            ]
        )
        for ev in events:
            result = dwell.process(ev)
            if result.dwell_event:
                dwell_count += 1
            if result.threshold_event:
                threshold_count += 1

        assert dwell_count == 1
        assert threshold_count == 1
        assert any(e.event_type == ZT.ZONE_EXIT for e in events)
        snap = dwell.snapshot("test_rect")
        assert snap is not None
        assert snap.total_dwell_events == 1
        assert snap.avg_dwell_seconds == pytest.approx(20.0)
