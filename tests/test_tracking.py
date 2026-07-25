"""Tests for Module 3 — multi-object tracking (inference/tracking).

Fast tests (types, NMS, synthetic motion, confirmation gating) run by default.
Real-inference integration tests are gated behind @pytest.mark.tracking since
they load model weights and are slower.

Run everything: pytest tests/test_tracking.py -m tracking
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from inference.detection import Detection
from inference.tracking import (
    DEFAULT_MIN_CONFIRMATION_FRAMES,
    PositionRecord,
    TrackedObject,
    Tracker,
)
from inference.tracking.tracker import _apply_pre_tracking_nms, _bbox_iou


# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #
class TestTrackedObjectType:
    def test_fields_and_derived_properties(self):
        history = (
            PositionRecord((50.0, 60.0), 1.0, (40.0, 50.0, 60.0, 70.0)),
            PositionRecord((55.0, 65.0), 2.0, (45.0, 55.0, 65.0, 75.0)),
        )
        t = TrackedObject(
            track_id=7,
            bbox=(45.0, 55.0, 65.0, 75.0),
            class_id=0,
            class_name="person",
            confidence=0.88,
            camera_id="cam_1",
            timestamp=2.0,
            position_history=history,
        )
        assert t.track_id == 7
        assert t.center == (55.0, 65.0)
        assert t.width == 20.0
        assert t.height == 20.0
        assert t.age == 2

    def test_frozen(self):
        t = TrackedObject(
            track_id=1,
            bbox=(0, 0, 10, 10),
            class_id=0,
            class_name="person",
            confidence=0.9,
            camera_id="cam",
            timestamp=0.0,
            position_history=(),
        )
        with pytest.raises(FrozenInstanceError):
            t.track_id = 2  # type: ignore[misc]


class TestPositionRecord:
    def test_frozen(self):
        r = PositionRecord((1.0, 2.0), 0.0, (0.0, 0.0, 2.0, 4.0))
        with pytest.raises(FrozenInstanceError):
            r.timestamp = 1.0  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# Pre-tracking NMS
# --------------------------------------------------------------------------- #
class TestPreTrackingNms:
    def _det(self, bbox, conf=0.9):
        return Detection(bbox, conf, 0, "person", 100.0, "cam")

    def test_suppresses_overlapping_lower_confidence(self):
        dets = [
            self._det((10, 10, 50, 50), 0.9),
            self._det((12, 12, 48, 48), 0.5),  # heavy overlap, lower conf
        ]
        kept = _apply_pre_tracking_nms(
            dets, conf_threshold=0.4, nms_iou_threshold=0.5
        )
        assert len(kept) == 1
        assert kept[0].confidence == pytest.approx(0.9)

    def test_keeps_separate_boxes(self):
        dets = [
            self._det((10, 10, 50, 50), 0.9),
            self._det((200, 200, 250, 250), 0.8),
        ]
        kept = _apply_pre_tracking_nms(
            dets, conf_threshold=0.4, nms_iou_threshold=0.5
        )
        assert len(kept) == 2

    def test_confidence_filter(self):
        dets = [self._det((10, 10, 50, 50), 0.2)]
        kept = _apply_pre_tracking_nms(
            dets, conf_threshold=0.4, nms_iou_threshold=0.5
        )
        assert kept == []


class TestBboxIou:
    def test_identical_boxes(self):
        b = (0.0, 0.0, 100.0, 100.0)
        assert _bbox_iou(b, b) == pytest.approx(1.0)

    def test_no_overlap(self):
        assert _bbox_iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


# --------------------------------------------------------------------------- #
# Tracker — synthetic motion, no model needed
# --------------------------------------------------------------------------- #
def _moving_detection(
    frame_idx: int,
    *,
    base_x: float = 100.0,
    step: float = 5.0,
    camera_id: str = "cam",
) -> Detection:
    x1 = base_x + frame_idx * step
    return Detection(
        bbox=(x1, 50.0, x1 + 40.0, 150.0),
        confidence=0.9,
        class_id=0,
        class_name="person",
        timestamp=float(frame_idx),
        camera_id=camera_id,
    )


class TestTrackerSynthetic:
    def test_empty_detections_returns_empty(self):
        tracker = Tracker()
        assert tracker.update([]) == []

    def test_confirmation_gate_hides_first_frame(self):
        tracker = Tracker(min_confirmation_frames=2)
        d = _moving_detection(0)
        assert tracker.update([d]) == []
        tracks = tracker.update([_moving_detection(1)])
        assert len(tracks) == 1
        assert tracks[0].track_id >= 0

    def test_stable_id_across_frames(self):
        tracker = Tracker(min_confirmation_frames=2)
        ids = []
        for i in range(6):
            tracks = tracker.update([_moving_detection(i)])
            if tracks:
                ids.append(tracks[0].track_id)
        assert len(ids) >= 1
        assert len(set(ids)) == 1

    def test_position_history_grows(self):
        tracker = Tracker(min_confirmation_frames=2)
        tracks = []
        for i in range(6):
            tracks = tracker.update([_moving_detection(i)])
        assert len(tracks) == 1
        # Frame 0 is unconfirmed; frames 1–5 produce history entries.
        assert len(tracks[0].position_history) == 5
        assert tracks[0].position_history[-1].timestamp == 5.0

    def test_history_capped_at_maxlen(self):
        tracker = Tracker(min_confirmation_frames=1, history_length=5)
        for i in range(10):
            tracks = tracker.update([_moving_detection(i)])
        assert len(tracks[0].position_history) == 5
        assert tracks[0].position_history[0].timestamp == 5.0

    def test_reset_clears_state(self):
        tracker = Tracker(min_confirmation_frames=2)
        tracker.update([_moving_detection(0)])
        tracker.update([_moving_detection(1)])
        tracker.reset()
        assert tracker.frame_index == 0
        # Confirmation gate applies again after reset.
        assert tracker.update([_moving_detection(0)]) == []

    def test_stamps_camera_id_from_detection(self):
        tracker = Tracker(min_confirmation_frames=2, camera_id="default")
        tracker.update([_moving_detection(0, camera_id="entrance")])
        tracks = tracker.update([_moving_detection(1, camera_id="entrance")])
        assert tracks[0].camera_id == "entrance"

    def test_two_people_get_distinct_ids(self):
        tracker = Tracker(min_confirmation_frames=1)
        for i in range(3):
            dets = [
                _moving_detection(i, base_x=50.0),
                _moving_detection(i, base_x=300.0),
            ]
            tracks = tracker.update(dets)
        assert len(tracks) == 2
        assert tracks[0].track_id != tracks[1].track_id

    def test_default_confirmation_is_two_frames(self):
        assert DEFAULT_MIN_CONFIRMATION_FRAMES == 2


# --------------------------------------------------------------------------- #
# Real inference integration — gated
# --------------------------------------------------------------------------- #
def _read_frames(video_path, n: int = 30, skip: int = 0):
    from inference.video import create_video_source

    src = create_video_source(str(video_path), target_fps=10)
    src.open()
    frames = []
    for _ in range(skip):
        ok, _ = src.read()
        if not ok:
            break
    for _ in range(n):
        ok, frame = src.read()
        if not ok:
            break
        frames.append(frame)
    src.release()
    return frames


@pytest.mark.tracking
class TestRealTrackingIntegration:
    def test_tracks_people_on_store_floor(
        self, pytorch_detector, store_floor_video
    ):
        tracker = Tracker(camera_id="store-floor", min_confirmation_frames=2)
        frames = _read_frames(store_floor_video, n=30)
        assert len(frames) > 5

        all_track_ids: set[int] = set()
        frames_with_tracks = 0
        for i, frame in enumerate(frames):
            dets = pytorch_detector.detect(
                frame, camera_id="store-floor", timestamp=float(i)
            )
            tracks = tracker.update(dets)
            if tracks:
                frames_with_tracks += 1
                all_track_ids.update(t.track_id for t in tracks)
                for t in tracks:
                    assert t.class_id == 0
                    assert len(t.position_history) >= 1
                    assert t.position_history[-1].center == t.center

        assert frames_with_tracks > 0
        assert len(all_track_ids) >= 1

    @pytest.mark.parametrize(
        "video_fixture", ["entrance_video", "store_floor_video", "checkout_video"]
    )
    def test_runs_on_all_sample_videos(
        self, pytorch_detector, video_fixture, request
    ):
        video_path = request.getfixturevalue(video_fixture)
        tracker = Tracker(camera_id=video_fixture, min_confirmation_frames=2)
        frames = _read_frames(video_path, n=15)
        assert len(frames) > 0
        for i, frame in enumerate(frames):
            dets = pytorch_detector.detect(
                frame, camera_id=video_fixture, timestamp=float(i)
            )
            tracks = tracker.update(dets)
            assert isinstance(tracks, list)


@pytest.mark.tracking
@pytest.mark.slow
class TestTrackingSmoke:
    def test_end_to_end_detect_and_track(self, pytorch_detector, store_floor_video):
        tracker = Tracker(camera_id="store-floor")
        frames = _read_frames(store_floor_video, n=50)
        total_tracks = 0
        for i, frame in enumerate(frames):
            dets = pytorch_detector.detect(
                frame, camera_id="store-floor", timestamp=float(i)
            )
            total_tracks += len(tracker.update(dets))
        assert total_tracks > 0
