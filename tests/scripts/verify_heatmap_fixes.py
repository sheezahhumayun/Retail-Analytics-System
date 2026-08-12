"""Verify heatmap spec-mismatch fix and same-spec merge behavior."""
from __future__ import annotations

import logging
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analytics.heatmaps import (
    HeatmapAccumulator,
    HeatmapEngine,
    HeatmapFrameSpec,
    HeatmapStore,
    HourBucketKey,
)
from inference.tracking import PositionRecord, TrackedObject

logging.basicConfig(level=logging.WARNING, format="%(name)s %(levelname)s %(message)s")

SPEC_360 = HeatmapFrameSpec(width=640, height=360, grid_scale=4)
SPEC_361 = HeatmapFrameSpec(width=640, height=361, grid_scale=4)
CAM = "verify_spec_cam"
KEY = HourBucketKey(CAM, date(2026, 8, 12), 11)
TS = datetime(2026, 8, 12, 11, 30, tzinfo=timezone.utc).timestamp()


def _track(
    camera_id: str,
    bbox: tuple[float, float, float, float],
    *,
    ts: float = TS,
) -> TrackedObject:
    return TrackedObject(
        track_id=1,
        bbox=bbox,
        class_id=0,
        class_name="person",
        confidence=0.9,
        camera_id=camera_id,
        timestamp=ts,
        position_history=(
            PositionRecord(
                center=((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2),
                timestamp=ts,
                bbox=bbox,
            ),
        ),
    )


def verify_spec_mismatch_overwrite() -> None:
    """First run 640x361, then 640x360 — second flush must succeed and replace."""
    with tempfile.TemporaryDirectory() as tmp:
        store = HeatmapStore(tmp, timezone="UTC")

        # Seed old bucket at 640x361
        old_acc = HeatmapAccumulator(SPEC_361)
        old_acc.add_point(100.0, 100.0)
        store.save(KEY, old_acc)
        before = store.load(KEY)
        assert before is not None
        before_sum = float(before.density.sum())
        print(f"[spec-mismatch] before: spec={before.spec.width}x{before.spec.height} density_sum={before_sum}")

        # New run at 640x360 — would have crashed pre-fix
        engine = HeatmapEngine(CAM, 640, 360, store=store, timezone="UTC")
        engine.update([_track(CAM, (200.0, 200.0, 240.0, 280.0), ts=TS)], TS)
        engine.flush()

        after = store.load(KEY)
        assert after is not None
        after_sum = float(after.density.sum())
        gx, gy = 200 // 4, 200 // 4
        new_cell = float(after.density[gy, gx])
        print(
            f"[spec-mismatch] after:  spec={after.spec.width}x{after.spec.height} "
            f"density_sum={after_sum} cell@200,200={new_cell}"
        )
        assert after.spec == SPEC_360
        assert after_sum > 0
        print("[spec-mismatch] PASS — second run completed, bucket reflects new spec")


def verify_same_spec_merge() -> None:
    """Two runs same spec in same hour — density must sum."""
    with tempfile.TemporaryDirectory() as tmp:
        store = HeatmapStore(tmp, timezone="UTC")
        cam = "verify_merge_cam"
        key = HourBucketKey(cam, date(2026, 8, 12), 12)
        ts = datetime(2026, 8, 12, 12, 15, tzinfo=timezone.utc).timestamp()

        engine1 = HeatmapEngine(cam, 640, 360, store=store, timezone="UTC")
        engine1.update([_track(cam, (50.0, 50.0, 90.0, 130.0), ts=ts)], ts)
        engine1.flush()
        first = store.load(key)
        assert first is not None
        first_sum = float(first.density.sum())
        print(f"[same-spec] after run 1: density_sum={first_sum}")

        engine2 = HeatmapEngine(cam, 640, 360, store=store, timezone="UTC")
        engine2.update([_track(cam, (400.0, 300.0, 440.0, 340.0), ts=ts + 60)], ts + 60)
        engine2.flush()
        merged = store.load(key)
        assert merged is not None
        merged_sum = float(merged.density.sum())
        print(f"[same-spec] after run 2: density_sum={merged_sum} (expected ~{first_sum * 2})")
        assert merged_sum == first_sum * 2
        print("[same-spec] PASS — density summed across two runs")


def verify_merge_range_skips_mismatch() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = HeatmapStore(tmp, timezone="UTC")
        key_a = HourBucketKey("cam_x", date(2026, 8, 12), 10)
        key_b = HourBucketKey("cam_x", date(2026, 8, 12), 11)
        acc_a = HeatmapAccumulator(SPEC_360)
        acc_b = HeatmapAccumulator(SPEC_361)
        acc_a.add_point(80.0, 80.0)
        acc_b.add_point(400.0, 300.0)
        store.save(key_a, acc_a)
        store.save(key_b, acc_b)

        start = datetime(2026, 8, 12, 10, 0, tzinfo=timezone.utc)
        end = datetime(2026, 8, 12, 12, 0, tzinfo=timezone.utc)
        merged = store.merge_range("cam_x", start, end)
        assert merged is not None
        hits = merged.total_hits()
        print(f"[merge_range] merged hits={hits} (only compatible bucket, expected 1.0)")
        assert hits == 1.0
        print("[merge_range] PASS — incompatible bucket skipped")


if __name__ == "__main__":
    verify_spec_mismatch_overwrite()
    verify_same_spec_merge()
    verify_merge_range_skips_mismatch()
    print("\nAll heatmap fix verifications passed.")
