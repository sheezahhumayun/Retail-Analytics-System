"""Tests for Module 5 — occupancy analytics (analytics/occupancy)."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from analytics.counting.types import CrossingEvent, EventType
from analytics.occupancy import (
    OccupancyScope,
    OccupancyTracker,
    StoreOccupancyAggregator,
)


def _event(
    event_type: EventType,
    timestamp: float,
    *,
    track_id: int = 1,
    camera_id: str = "entrance",
) -> CrossingEvent:
    return CrossingEvent(
        camera_id=camera_id,
        track_id=track_id,
        event_type=event_type,
        timestamp=timestamp,
        line_name="door",
    )


class TestOccupancyTracker:
    def test_hand_worked_sequence(self):
        """ENTRY, ENTRY, EXIT, EXIT, EXIT → occupancy 1,2,1,0,0."""
        tracker = OccupancyTracker("entrance")
        times = [1000.0, 1010.0, 1020.0, 1030.0, 1040.0]
        types = [
            EventType.ENTRY,
            EventType.ENTRY,
            EventType.EXIT,
            EventType.EXIT,
            EventType.EXIT,
        ]
        expected_occ = [1, 2, 1, 0, 0]
        expected_visitors = [1, 2, 2, 2, 2]
        expected_exits = [0, 0, 1, 2, 3]

        for i, (etype, ts) in enumerate(zip(types, times, strict=True)):
            snap = tracker.process(_event(etype, ts, track_id=i))
            assert snap.current_occupancy == expected_occ[i]
            assert snap.today_visitors == expected_visitors[i]
            assert snap.today_exits == expected_exits[i]

        assert tracker.snapshot().peak_occupancy == 2
        assert tracker.snapshot().peak_occupancy_time == 1010.0

    def test_occupancy_never_negative_with_floor(self):
        tracker = OccupancyTracker("entrance", floor_at_zero=True)
        for i in range(3):
            snap = tracker.process(_event(EventType.EXIT, 1000.0 + i, track_id=i))
            assert snap.current_occupancy == 0
        assert tracker.snapshot().total_exits == 3

        # Entries eventually catch up — occupancy rises only once entries > exits.
        tracker.process(_event(EventType.ENTRY, 2000.0, track_id=10))
        tracker.process(_event(EventType.ENTRY, 2010.0, track_id=11))
        tracker.process(_event(EventType.ENTRY, 2020.0, track_id=12))
        assert tracker.snapshot().current_occupancy == 0
        snap = tracker.process(_event(EventType.ENTRY, 2030.0, track_id=13))
        assert snap.current_occupancy == 1

    def test_today_visitors_only_increases(self):
        tracker = OccupancyTracker("entrance")
        tracker.process(_event(EventType.ENTRY, 1000.0))
        tracker.process(_event(EventType.EXIT, 1010.0, track_id=2))
        snap = tracker.snapshot()
        assert snap.today_visitors == 1
        assert snap.current_occupancy == 0

    def test_reset_clears_counters(self):
        tracker = OccupancyTracker("entrance")
        tracker.process(_event(EventType.ENTRY, 1000.0))
        tracker.reset()
        snap = tracker.snapshot()
        assert snap.current_occupancy == 0
        assert snap.today_visitors == 0
        assert snap.peak_occupancy == 0

    def test_midnight_rollover_resets_daily_counters(self):
        # 2026-07-26 23:00 UTC then 2026-07-27 00:30 UTC
        t1 = datetime(2026, 7, 26, 23, 0, tzinfo=timezone.utc).timestamp()
        t2 = datetime(2026, 7, 27, 0, 30, tzinfo=timezone.utc).timestamp()
        tracker = OccupancyTracker("entrance", timezone="UTC")
        tracker.process(_event(EventType.ENTRY, t1))
        tracker.process(_event(EventType.ENTRY, t1 + 10, track_id=2))
        assert tracker.snapshot().today_visitors == 2
        assert tracker.snapshot().peak_occupancy == 2

        snap = tracker.process(_event(EventType.ENTRY, t2, track_id=3))
        assert snap.today_visitors == 1
        assert snap.peak_occupancy == 1
        assert tracker.last_day_rolled

    def test_snapshot_to_dict(self):
        tracker = OccupancyTracker("entrance")
        tracker.process(_event(EventType.ENTRY, 1000.0))
        d = tracker.snapshot().to_dict()
        assert d["scope_id"] == "entrance"
        assert d["scope_type"] == "camera"
        assert d["current_occupancy"] == 1
        assert d["today_visitors"] == 1


class TestStoreOccupancyAggregator:
    def test_store_roll_up_two_cameras(self):
        store = StoreOccupancyAggregator("store_1", ["entrance", "side"])
        store.process(_event(EventType.ENTRY, 1000.0, camera_id="entrance"))
        store.process(_event(EventType.ENTRY, 1010.0, track_id=2, camera_id="side"))
        snap = store.store_snapshot()
        assert snap.scope_type == OccupancyScope.STORE
        assert snap.current_occupancy == 2
        assert snap.today_visitors == 2
        assert snap.peak_occupancy == 2

    def test_ignores_unknown_camera(self):
        store = StoreOccupancyAggregator("store_1", ["entrance"])
        assert store.process(_event(EventType.ENTRY, 1000.0, camera_id="other")) is None


@pytest.mark.occupancy
class TestOccupancyFromCountingPipeline:
    def test_counting_events_drive_occupancy(self, pytorch_detector, entrance_video):
        from analytics.counting import CountingLine, InsideSide, LineCounter
        from inference.tracking import Tracker
        from inference.video import create_video_source

        line = CountingLine(
            x1=50.0,
            y1=280.0,
            x2=590.0,
            y2=280.0,
            inside_side=InsideSide.LEFT,
            camera_id="entrance",
        )
        counter = LineCounter(line)
        tracker = Tracker(camera_id="entrance", min_confirmation_frames=2)
        occupancy = OccupancyTracker("entrance")

        src = create_video_source(str(entrance_video), target_fps=10)
        src.open()
        for fi in range(40):
            ok, frame = src.read()
            if not ok:
                break
            dets = pytorch_detector.detect(frame, camera_id="entrance")
            for event in counter.update(tracker.update(dets)):
                snap = occupancy.process(event)
                assert snap.current_occupancy >= 0
        src.release()

        final = occupancy.snapshot()
        assert final.today_visitors >= final.current_occupancy
        assert final.peak_occupancy >= final.current_occupancy
