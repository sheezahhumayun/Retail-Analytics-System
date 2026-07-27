"""Tests for Module 4 — entry/exit counting (analytics/counting)."""
from __future__ import annotations

import json
import tempfile
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from analytics.counting import (
    CountingLine,
    CrossingEvent,
    EventType,
    InsideSide,
    LineCounter,
    foot_point_from_bbox,
    is_inside,
    segments_intersect,
)
from inference.tracking import PositionRecord, TrackedObject


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
HORIZONTAL_LINE = CountingLine(
    x1=0.0,
    y1=200.0,
    x2=400.0,
    y2=200.0,
    inside_side=InsideSide.LEFT,  # below the L→R line
    camera_id="cam_1",
    name="door",
)


def _track(
    track_id: int,
    bboxes: list[tuple[float, float, float, float]],
    *,
    camera_id: str = "cam_1",
    base_ts: float = 1000.0,
) -> TrackedObject:
    history = tuple(
        PositionRecord(
            center=((b[0] + b[2]) / 2, (b[1] + b[3]) / 2),
            timestamp=base_ts + i,
            bbox=b,
        )
        for i, b in enumerate(bboxes)
    )
    last = bboxes[-1]
    return TrackedObject(
        track_id=track_id,
        bbox=last,
        class_id=0,
        class_name="person",
        confidence=0.9,
        camera_id=camera_id,
        timestamp=base_ts + len(bboxes) - 1,
        position_history=history,
    )


# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #
class TestCountingLine:
    def test_json_roundtrip(self):
        line = HORIZONTAL_LINE
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "line.json"
            line.save_json(path)
            loaded = CountingLine.load_json(path)
        assert loaded == line

    def test_frozen(self):
        with pytest.raises(FrozenInstanceError):
            HORIZONTAL_LINE.x1 = 1.0  # type: ignore[misc]


class TestCrossingEvent:
    def test_to_dict_shape(self):
        ev = CrossingEvent("cam_1", 42, EventType.ENTRY, 1_700_000_000.0, "door")
        d = ev.to_dict()
        assert d["camera_id"] == "cam_1"
        assert d["track_id"] == "42"
        assert d["event_type"] == "ENTRY"
        assert "timestamp" in d
        assert d["timestamp"].endswith("+00:00")


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #
class TestGeometry:
    def test_foot_point(self):
        assert foot_point_from_bbox((10.0, 20.0, 30.0, 100.0)) == (20.0, 100.0)

    def test_is_inside_below_horizontal_line(self):
        assert is_inside(HORIZONTAL_LINE, (50.0, 250.0))
        assert not is_inside(HORIZONTAL_LINE, (50.0, 50.0))

    def test_segments_intersect_crossing(self):
        assert segments_intersect(
            (50.0, 100.0), (50.0, 300.0), (0.0, 200.0), (400.0, 200.0)
        )

    def test_segments_no_intersect_parallel(self):
        assert not segments_intersect(
            (50.0, 50.0), (150.0, 50.0), (0.0, 200.0), (400.0, 200.0)
        )


# --------------------------------------------------------------------------- #
# LineCounter
# --------------------------------------------------------------------------- #
class TestLineCounter:
    def test_entry_on_outside_to_inside(self):
        counter = LineCounter(HORIZONTAL_LINE)
        # Move from above line (y=150) to below (y=250).
        t1 = _track(1, [(40.0, 100.0, 60.0, 150.0)])
        assert counter.update([t1]) == []

        t2 = _track(
            1,
            [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0)],
        )
        events = counter.update([t2])
        assert len(events) == 1
        assert events[0].event_type == EventType.ENTRY
        assert events[0].track_id == 1

    def test_exit_on_inside_to_outside(self):
        counter = LineCounter(HORIZONTAL_LINE)
        all_events: list[CrossingEvent] = []
        all_events.extend(counter.update([_track(2, [(40.0, 220.0, 60.0, 280.0)])]))
        all_events.extend(
            counter.update(
                [_track(2, [(40.0, 220.0, 60.0, 280.0), (40.0, 120.0, 60.0, 180.0)])]
            )
        )
        assert any(e.event_type == EventType.EXIT for e in all_events)

    def test_debounce_blocks_duplicate_entry(self):
        counter = LineCounter(HORIZONTAL_LINE)
        # Entry
        counter.update(
            [_track(3, [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0)])]
        )
        # Jitter back and forth across line without full exit
        jitter = _track(
            3,
            [
                (40.0, 200.0, 60.0, 250.0),
                (40.0, 100.0, 60.0, 150.0),
                (40.0, 200.0, 60.0, 250.0),
            ],
        )
        events = counter.update([jitter])
        assert all(e.event_type != EventType.ENTRY for e in events)

    def test_ignores_wrong_camera(self):
        counter = LineCounter(HORIZONTAL_LINE)
        t = _track(
            4,
            [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0)],
            camera_id="other_cam",
        )
        assert counter.update([t]) == []

    def test_reset_clears_debounce(self):
        counter = LineCounter(HORIZONTAL_LINE)
        counter.update(
            [_track(5, [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0)])]
        )
        counter.reset()
        events = counter.update(
            [_track(5, [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0)])]
        )
        assert len(events) == 1
        assert events[0].event_type == EventType.ENTRY

    def test_needs_two_history_points(self):
        counter = LineCounter(HORIZONTAL_LINE)
        assert counter.update([_track(6, [(40.0, 100.0, 60.0, 150.0)])]) == []

    def test_scans_all_new_history_pairs(self):
        """Every new history pair is checked, including on first sight."""
        counter = LineCounter(HORIZONTAL_LINE)
        cross = _track(
            8,
            [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0)],
        )
        events = counter.update([cross])
        assert len(events) == 1
        assert events[0].event_type == EventType.ENTRY
        later = counter.update(
            [_track(8, [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0), (41.0, 210.0, 61.0, 260.0)])]
        )
        assert not any(e.event_type == EventType.ENTRY for e in later)

    def test_track_id_zero_is_counted(self):
        """track_id=0 is valid — must not be treated as falsy anywhere."""
        counter = LineCounter(HORIZONTAL_LINE)
        events = counter.update(
            [
                _track(
                    0,
                    [(40.0, 100.0, 60.0, 150.0), (40.0, 200.0, 60.0, 250.0)],
                )
            ]
        )
        assert len(events) == 1
        assert events[0].track_id == 0
        assert events[0].event_type == EventType.ENTRY


@pytest.mark.counting
class TestCountingIntegration:
    def test_detect_track_count_pipeline(self, pytorch_detector, entrance_video):
        from inference.tracking import Tracker
        from inference.video import create_video_source

        # Default horizontal line across lower third of 640×360 frame.
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

        src = create_video_source(str(entrance_video), target_fps=10)
        src.open()
        all_events: list[CrossingEvent] = []
        for _ in range(40):
            ok, frame = src.read()
            if not ok:
                break
            dets = pytorch_detector.detect(frame, camera_id="entrance")
            tracks = tracker.update(dets)
            all_events.extend(counter.update(tracks))
        src.release()

        # Sanity: pipeline runs; events may or may not fire depending on line
        # placement vs actual foot traffic — we only assert well-formed output.
        for ev in all_events:
            assert ev.event_type in (EventType.ENTRY, EventType.EXIT)
            assert ev.camera_id == "entrance"
            d = ev.to_dict()
            assert json.loads(json.dumps(d)) == d
