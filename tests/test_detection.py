"""Tests for Module 2 — person detection (inference/detection).

Fast tests (types, ABC filtering contract, factory routing) run by default.
Real-inference tests (model loading, actual detection, backend parity) are
gated behind @pytest.mark.detection since they load weights and are slower.
Run everything: pytest tests/test_detection.py -m detection
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from inference.detection import (
    Detection,
    DetectionBackend,
    ONNXDetector,
    PersonDetector,
    UltralyticsDetector,
    create_detector,
)
from inference.detection.factory import DEFAULT_MODELS_DIR


# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #
class TestDetectionType:
    def test_fields(self):
        d = Detection(
            bbox=(10.0, 20.0, 110.0, 220.0),
            confidence=0.87,
            class_id=0,
            class_name="person",
            timestamp=1234.5,
            camera_id="cam_1",
        )
        assert d.bbox == (10.0, 20.0, 110.0, 220.0)
        assert d.confidence == 0.87
        assert d.class_id == 0
        assert d.class_name == "person"
        assert d.timestamp == 1234.5
        assert d.camera_id == "cam_1"

    def test_frozen(self):
        d = Detection((0, 0, 10, 10), 0.9, 0, "person", 0.0, "cam")
        with pytest.raises(FrozenInstanceError):
            d.confidence = 0.5  # type: ignore[misc]

    def test_derived_properties(self):
        d = Detection((10.0, 20.0, 110.0, 220.0), 0.9, 0, "person", 0.0, "cam")
        assert d.x1 == 10.0
        assert d.y1 == 20.0
        assert d.x2 == 110.0
        assert d.y2 == 220.0
        assert d.width == 100.0
        assert d.height == 200.0
        assert d.center == (60.0, 120.0)


class TestDetectionBackendEnum:
    def test_values(self):
        assert DetectionBackend.ULTRALYTICS.value == "ultralytics"
        assert DetectionBackend.ONNX.value == "onnx"


# --------------------------------------------------------------------------- #
# ABC filtering contract — no model needed, exercises detect() directly.
# --------------------------------------------------------------------------- #
class _FakeDetector(PersonDetector):
    """Minimal PersonDetector whose _raw_infer returns a fixed, unfiltered
    set of detections spanning person/car/dog — used to test the ABC's
    filtering + stamping logic in isolation from any real model."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.released = False

    def _raw_infer(self, frame):
        return [
            Detection((0, 0, 10, 10), 0.9, 0, "person", 0.0, ""),
            Detection((20, 20, 40, 40), 0.8, 2, "car", 0.0, ""),
            Detection((50, 50, 60, 60), 0.7, 16, "dog", 0.0, ""),
        ]

    def backend(self):
        return DetectionBackend.ULTRALYTICS

    def release(self):
        self.released = True


class TestPersonDetectorFilteringContract:
    def test_person_only_filters_non_person_classes(self):
        det = _FakeDetector(person_only=True)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        results = det.detect(frame, camera_id="cam_1")
        assert len(results) == 1
        assert results[0].class_id == 0
        assert results[0].class_name == "person"

    def test_person_only_false_keeps_all_classes(self):
        det = _FakeDetector(person_only=False)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        results = det.detect(frame, camera_id="cam_1")
        assert len(results) == 3
        assert {r.class_id for r in results} == {0, 2, 16}

    def test_stamps_caller_timestamp_and_camera_id(self):
        det = _FakeDetector(person_only=False)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        results = det.detect(frame, timestamp=555.5, camera_id="cam_42")
        assert len(results) == 3
        for r in results:
            assert r.timestamp == 555.5
            assert r.camera_id == "cam_42"

    def test_default_timestamp_is_now(self):
        import time

        det = _FakeDetector(person_only=False)
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        before = time.time()
        results = det.detect(frame, camera_id="cam_1")
        after = time.time()
        for r in results:
            assert before <= r.timestamp <= after

    def test_empty_frame_returns_empty_list(self):
        det = _FakeDetector(person_only=False)
        assert det.detect(None, camera_id="cam_1") == []
        assert det.detect(np.zeros((0, 0, 3)), camera_id="cam_1") == []

    def test_context_manager_calls_release(self):
        with _FakeDetector(person_only=False) as det:
            assert not det.released
        assert det.released


# --------------------------------------------------------------------------- #
# Factory routing — no model load, just class selection + error handling.
# --------------------------------------------------------------------------- #
class TestCreateDetectorRouting:
    def test_unknown_backend_raises(self):
        with pytest.raises(ValueError):
            create_detector(backend="not-a-real-backend")

    def test_default_backend_is_ultralytics(self):
        # Only checks the class chosen, not that a model loads successfully
        # (that's covered by the gated real-inference tests below).
        import inspect

        sig = inspect.signature(create_detector)
        assert sig.parameters["backend"].default == DetectionBackend.ULTRALYTICS.value

    def test_default_models_dir_under_inference(self):
        assert DEFAULT_MODELS_DIR.name == "models"
        assert DEFAULT_MODELS_DIR.parent.name == "inference"


# --------------------------------------------------------------------------- #
# Real inference — gated: loads actual weights, runs on real frames.
# --------------------------------------------------------------------------- #
@pytest.fixture(scope="module")
def pytorch_detector():
    det = create_detector(backend="ultralytics")
    yield det
    det.release()


@pytest.fixture(scope="module")
def onnx_detector():
    det = create_detector(backend="onnx")
    yield det
    det.release()


def _read_frame(video_path, skip=5):
    from inference.video import create_video_source

    src = create_video_source(str(video_path), target_fps=5)
    src.open()
    frame = None
    for _ in range(skip + 1):
        ok, frame = src.read()
        if not ok:
            break
    src.release()
    return frame


@pytest.mark.detection
class TestRealInference:
    def test_pytorch_detects_people(self, pytorch_detector, store_floor_video):
        frame = _read_frame(store_floor_video)
        assert frame is not None
        results = pytorch_detector.detect(frame, camera_id="store-floor")
        assert len(results) > 0
        h, w = frame.shape[:2]
        for d in results:
            assert d.class_id == 0
            assert 0.0 <= d.confidence <= 1.0
            x1, y1, x2, y2 = d.bbox
            assert 0 <= x1 < x2 <= w
            assert 0 <= y1 < y2 <= h

    def test_onnx_detects_people(self, onnx_detector, store_floor_video):
        frame = _read_frame(store_floor_video)
        assert frame is not None
        results = onnx_detector.detect(frame, camera_id="store-floor")
        assert len(results) > 0
        h, w = frame.shape[:2]
        for d in results:
            assert d.class_id == 0
            assert 0.0 <= d.confidence <= 1.0
            x1, y1, x2, y2 = d.bbox
            assert 0 <= x1 < x2 <= w
            assert 0 <= y1 < y2 <= h

    @pytest.mark.parametrize(
        "video_fixture", ["entrance_video", "store_floor_video", "checkout_video"]
    )
    def test_pytorch_runs_on_all_sample_videos(
        self, pytorch_detector, video_fixture, request
    ):
        video_path = request.getfixturevalue(video_fixture)
        frame = _read_frame(video_path)
        assert frame is not None
        results = pytorch_detector.detect(frame, camera_id=video_fixture)
        # Not every frame has a person (e.g. an empty establishing shot), so
        # this only asserts the call succeeds and returns well-formed output.
        assert isinstance(results, list)
        for d in results:
            assert d.class_id == 0


@pytest.mark.detection
class TestBackendParity:
    def test_person_counts_agree_within_tolerance(
        self, pytorch_detector, onnx_detector, store_floor_video
    ):
        frame = _read_frame(store_floor_video)
        assert frame is not None
        d_pt = pytorch_detector.detect(frame, camera_id="parity")
        d_onnx = onnx_detector.detect(frame, camera_id="parity")
        assert abs(len(d_pt) - len(d_onnx)) <= 1

    def test_confidences_are_close(
        self, pytorch_detector, onnx_detector, store_floor_video
    ):
        frame = _read_frame(store_floor_video)
        d_pt = sorted(
            pytorch_detector.detect(frame, camera_id="parity"),
            key=lambda d: -d.confidence,
        )
        d_onnx = sorted(
            onnx_detector.detect(frame, camera_id="parity"),
            key=lambda d: -d.confidence,
        )
        n = min(len(d_pt), len(d_onnx))
        assert n > 0
        # Tolerant match: compare by nearest-confidence pairing rather than
        # raw index, since near-tied confidences can swap order between
        # backends (see parity investigation — same boxes, different rank).
        onnx_confs = [d.confidence for d in d_onnx]
        for d in d_pt[:n]:
            closest = min(onnx_confs, key=lambda c: abs(c - d.confidence))
            assert abs(closest - d.confidence) < 0.1


# --------------------------------------------------------------------------- #
# Smoke integration — full pipeline over several frames of one clip.
# --------------------------------------------------------------------------- #
@pytest.mark.detection
@pytest.mark.slow
class TestSmokeIntegration:
    def test_end_to_end_over_n_frames(self, pytorch_detector, store_floor_video):
        from inference.video import create_video_source

        src = create_video_source(str(store_floor_video), target_fps=5)
        src.open()
        total_detections = 0
        frames_seen = 0
        for _ in range(20):
            ok, frame = src.read()
            if not ok:
                break
            frames_seen += 1
            total_detections += len(
                pytorch_detector.detect(frame, camera_id="store-floor")
            )
        src.release()

        assert frames_seen > 0
        # Sanity bounds, not precision: store-floor is a busy clip, so we
        # expect people in most frames but not an absurd per-frame count.
        assert total_detections > 0
        assert total_detections < frames_seen * 30