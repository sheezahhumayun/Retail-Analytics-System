"""Tests for Module 8 — heatmap generation (analytics/heatmaps)."""
from __future__ import annotations

import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

import cv2
import numpy as np
import pytest

from analytics.heatmaps import (
    HeatmapAccumulator,
    HeatmapEngine,
    HeatmapFrameSpec,
    HeatmapStore,
    HourBucketKey,
    render_heatmap_overlay,
)
from inference.tracking import PositionRecord, TrackedObject


SPEC = HeatmapFrameSpec(width=640, height=360, grid_scale=4)


def _ref_frame() -> np.ndarray:
    return np.zeros((SPEC.height, SPEC.width, 3), dtype=np.uint8) + 40


def _track(
    track_id: int,
    bboxes: list[tuple[float, float, float, float]],
    *,
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
    return TrackedObject(
        track_id=track_id,
        bbox=bboxes[-1],
        class_id=0,
        class_name="person",
        confidence=0.9,
        camera_id="cam_1",
        timestamp=base_ts + len(bboxes) - 1,
        position_history=history,
    )


class TestHeatmapAccumulator:
    def test_point_maps_to_grid_with_scale(self):
        acc = HeatmapAccumulator(SPEC)
        acc.add_point(100.0, 200.0)
        gx, gy = 100 // 4, 200 // 4
        assert acc.density[gy, gx] == pytest.approx(1.0)
        assert acc.density.sum() == pytest.approx(1.0)

    def test_segment_adds_trajectory_weight(self):
        acc = HeatmapAccumulator(SPEC)
        acc.add_segment(40.0, 80.0, 200.0, 160.0)
        assert acc.trajectory.sum() > 0

    def test_merge_accumulators(self):
        a = HeatmapAccumulator(SPEC)
        b = HeatmapAccumulator(SPEC)
        a.add_point(50.0, 50.0)
        b.add_point(50.0, 50.0)
        a.merge_inplace(b)
        assert a.density.sum() == pytest.approx(2.0)


class TestHeatmapRenderer:
    def test_render_matches_reference_shape(self):
        acc = HeatmapAccumulator(SPEC)
        acc.add_point(320.0, 180.0)
        acc.add_point(321.0, 181.0)
        ref = _ref_frame()
        out = render_heatmap_overlay(acc, ref, blur_sigma=5.0)
        assert out.shape == ref.shape

    def test_render_rejects_size_mismatch(self):
        acc = HeatmapAccumulator(SPEC)
        bad_ref = np.zeros((100, 100, 3), dtype=np.uint8)
        with pytest.raises(ValueError, match="does not match"):
            render_heatmap_overlay(acc, bad_ref)


class TestHeatmapStore:
    def test_save_load_roundtrip(self):
        acc = HeatmapAccumulator(SPEC)
        acc.add_point(120.0, 240.0)
        key = HourBucketKey("cam_1", date(2026, 7, 28), 12)
        with tempfile.TemporaryDirectory() as tmp:
            store = HeatmapStore(tmp)
            store.save(key, acc)
            loaded = store.load(key)
        assert loaded is not None
        assert loaded.density.sum() == pytest.approx(acc.density.sum())

    def test_merge_range_sums_buckets(self):
        key_a = HourBucketKey("cam_1", date(2026, 7, 28), 10)
        key_b = HourBucketKey("cam_1", date(2026, 7, 28), 11)
        acc_a = HeatmapAccumulator(SPEC)
        acc_b = HeatmapAccumulator(SPEC)
        acc_a.add_point(80.0, 80.0)
        acc_b.add_point(400.0, 300.0)

        with tempfile.TemporaryDirectory() as tmp:
            store = HeatmapStore(tmp, timezone="UTC")
            store.save(key_a, acc_a)
            store.save(key_b, acc_b)

            start = datetime(2026, 7, 28, 10, 0, tzinfo=timezone.utc)
            one_hour = store.merge_range("cam_1", start, datetime(2026, 7, 28, 11, 0, tzinfo=timezone.utc))
            both = store.merge_range("cam_1", start, datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc))

        assert one_hour is not None and both is not None
        assert one_hour.total_hits() == pytest.approx(1.0)
        assert both.total_hits() == pytest.approx(2.0)

    def test_time_range_produces_different_heatmaps(self):
        """Lunch-hour bucket vs full-day merge should differ when activity varies."""
        key_lunch = HourBucketKey("cam_1", date(2026, 7, 28), 12)
        key_other = HourBucketKey("cam_1", date(2026, 7, 28), 9)
        lunch = HeatmapAccumulator(SPEC)
        morning = HeatmapAccumulator(SPEC)
        lunch.add_point(500.0, 300.0)
        lunch.add_point(510.0, 310.0)
        morning.add_point(80.0, 60.0)

        ref = _ref_frame()
        with tempfile.TemporaryDirectory() as tmp:
            store = HeatmapStore(tmp, timezone="UTC")
            store.save(key_lunch, lunch)
            store.save(key_other, morning)

            day_start = datetime(2026, 7, 28, 0, 0, tzinfo=timezone.utc)
            lunch_start = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)
            lunch_end = datetime(2026, 7, 28, 13, 0, tzinfo=timezone.utc)
            day_end = datetime(2026, 7, 29, 0, 0, tzinfo=timezone.utc)

            full_acc = store.merge_range("cam_1", day_start, day_end)
            lunch_acc = store.merge_range("cam_1", lunch_start, lunch_end)

        assert full_acc is not None and lunch_acc is not None
        full_img = render_heatmap_overlay(full_acc, ref, blur_sigma=3.0)
        lunch_img = render_heatmap_overlay(lunch_acc, ref, blur_sigma=3.0)
        assert not np.array_equal(full_img, lunch_img)


class TestHeatmapEngine:
    def test_update_accumulates_tracks(self):
        engine = HeatmapEngine("cam_1", SPEC.width, SPEC.height, grid_scale=4)
        engine.set_reference_frame(_ref_frame())
        engine.update(
            [_track(1, [(100.0, 100.0, 140.0, 200.0), (110.0, 110.0, 150.0, 210.0)])],
            1000.0,
        )
        overlay = engine.render()
        assert overlay.shape == (SPEC.height, SPEC.width, 3)
        assert overlay.sum() > _ref_frame().sum()

    def test_flush_persists_bucket(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = HeatmapStore(tmp, timezone="UTC")
            engine = HeatmapEngine(
                "cam_1", SPEC.width, SPEC.height, store=store, timezone="UTC"
            )
            engine.set_reference_frame(_ref_frame())
            ts = datetime(2026, 7, 28, 14, 30, tzinfo=timezone.utc).timestamp()
            engine.update([_track(1, [(200.0, 200.0, 240.0, 300.0)])], ts)
            engine.flush()
            key = HourBucketKey("cam_1", date(2026, 7, 28), 14)
            loaded = store.load(key)
        assert loaded is not None
        assert loaded.total_hits() > 0

    def test_render_after_flush_loads_persisted_bucket(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = HeatmapStore(tmp, timezone="UTC")
            engine = HeatmapEngine(
                "cam_1", SPEC.width, SPEC.height, store=store, timezone="UTC"
            )
            ref = _ref_frame()
            engine.set_reference_frame(ref)
            ts = datetime(2026, 7, 28, 14, 30, tzinfo=timezone.utc).timestamp()
            engine.update([_track(1, [(200.0, 200.0, 240.0, 300.0)])], ts)
            engine.flush()
            overlay = engine.render()
            assert overlay.sum() > ref.sum()


@pytest.mark.heatmaps
class TestHeatmapIntegration:
    def test_video_pipeline_produces_overlay(self, store_floor_video):
        from inference.detection import create_detector
        from inference.tracking import Tracker
        from inference.video import create_video_source

        target_fps = 10.0
        with tempfile.TemporaryDirectory() as tmp:
            src = create_video_source(str(store_floor_video), target_fps=target_fps)
            src.open()
            ok, frame = src.read()
            assert ok
            h, w = frame.shape[:2]
            src.release()

            store = HeatmapStore(tmp)
            engine = HeatmapEngine("store-floor", w, h, store=store)
            engine.set_reference_frame(frame)

            with create_detector(backend="ultralytics") as det:
                det.detect(frame)
                src = create_video_source(str(store_floor_video), target_fps=target_fps)
                src.open()
                tracker = Tracker(camera_id="store-floor", min_confirmation_frames=2)
                frame_idx = 0
                while frame_idx < 25:
                    ok, frame = src.read()
                    if not ok:
                        break
                    ts = src.get_last_timestamp()
                    dets = det.detect(frame, camera_id="store-floor", timestamp=ts)
                    engine.update(tracker.update(dets), ts)
                    frame_idx += 1
                src.release()

            engine.flush()
            overlay = engine.render()
            out_path = Path(tmp) / "heatmap.png"
            cv2.imwrite(str(out_path), overlay)
            assert out_path.is_file()
            assert overlay.shape[:2] == (h, w)
            assert overlay.sum() != frame.sum()
