"""Tests for Module 6 — zone management & analytics (analytics/zones)."""
from __future__ import annotations

import json
import tempfile
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from analytics.zones import (
    MultiZoneAnalytics,
    Zone,
    ZoneAnalytics,
    ZoneConfig,
    ZoneDetector,
    ZoneEventType,
    ZoneType,
    detect_flapping,
    extract_transitions,
    is_inside_zone,
    point_in_polygon,
)
from inference.tracking import PositionRecord, TrackedObject


# Rectangle zone: y=200..400, x=0..400
RECT_ZONE = Zone(
    zone_id="test_rect",
    zone_name="Test Rectangle",
    camera_id="cam_1",
    polygon_coordinates=((0.0, 200.0), (400.0, 200.0), (400.0, 400.0), (0.0, 400.0)),
    zone_type=ZoneType.GENERAL,
)

CHECKOUT_ZONE = Zone(
    zone_id="checkout",
    zone_name="Checkout",
    camera_id="cam_1",
    polygon_coordinates=((200.0, 200.0), (400.0, 200.0), (400.0, 400.0), (200.0, 400.0)),
    zone_type=ZoneType.CHECKOUT,
)

# Single-frame hysteresis for unit tests that use one-step crossings.
HYST_1 = {"hysteresis_frames": 1}


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
            timestamp=base_ts + i * 10.0,
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
        timestamp=base_ts + (len(bboxes) - 1) * 10.0,
        position_history=history,
    )


# --------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------- #
class TestZone:
    def test_json_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "zone.json"
            RECT_ZONE.save_json(path)
            loaded = Zone.load_json(path)
        assert loaded == RECT_ZONE

    def test_config_roundtrip(self):
        config = ZoneConfig(camera_id="cam_1", zones=(RECT_ZONE, CHECKOUT_ZONE))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "zones.json"
            config.save_json(path)
            loaded = ZoneConfig.load_json(path)
        assert loaded == config

    def test_frozen(self):
        with pytest.raises(FrozenInstanceError):
            RECT_ZONE.zone_id = "x"  # type: ignore[misc]

    def test_requires_three_points(self):
        with pytest.raises(ValueError):
            Zone(
                zone_id="bad",
                zone_name="Bad",
                camera_id="cam_1",
                polygon_coordinates=((0, 0), (10, 10)),
            )


# --------------------------------------------------------------------------- #
# Geometry
# --------------------------------------------------------------------------- #
class TestGeometry:
    def test_point_inside_rectangle(self):
        assert point_in_polygon(RECT_ZONE.polygon_coordinates, (200.0, 300.0))
        assert is_inside_zone(RECT_ZONE, (200.0, 300.0))

    def test_point_outside_rectangle(self):
        assert not point_in_polygon(RECT_ZONE.polygon_coordinates, (200.0, 100.0))
        assert not is_inside_zone(RECT_ZONE, (200.0, 100.0))

    def test_point_on_edge_counts_inside(self):
        assert point_in_polygon(RECT_ZONE.polygon_coordinates, (0.0, 300.0))


# --------------------------------------------------------------------------- #
# ZoneDetector
# --------------------------------------------------------------------------- #
class TestZoneDetector:
    def test_zone_enter_outside_to_inside(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        t1 = _track(1, [(180.0, 100.0, 220.0, 180.0)])
        assert detector.update([t1]) == []

        t2 = _track(
            1,
            [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
        )
        events = detector.update([t2])
        assert len(events) == 1
        assert events[0].event_type == ZoneEventType.ZONE_ENTER
        assert events[0].track_id == 1
        assert events[0].zone_id == "test_rect"

    def test_zone_exit_inside_to_outside(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        events = detector.update(
            [
                _track(
                    2,
                    [
                        (180.0, 250.0, 220.0, 320.0),
                        (185.0, 255.0, 225.0, 325.0),
                        (180.0, 100.0, 220.0, 180.0),
                    ],
                )
            ]
        )
        assert any(e.event_type == ZoneEventType.ZONE_EXIT for e in events)

    def test_zone_presence_while_inside(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        events = detector.update(
            [
                _track(
                    3,
                    [
                        (180.0, 250.0, 220.0, 320.0),
                        (185.0, 255.0, 225.0, 325.0),
                        (190.0, 260.0, 230.0, 330.0),
                    ],
                )
            ]
        )
        presence = [e for e in events if e.event_type == ZoneEventType.ZONE_PRESENCE]
        assert len(presence) == 1
        assert presence[0].dwell_delta == pytest.approx(10.0)

    def test_debounce_blocks_duplicate_enter(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        detector.update(
            [
                _track(
                    4,
                    [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
                )
            ]
        )
        jitter = _track(
            4,
            [
                (180.0, 250.0, 220.0, 320.0),
                (180.0, 100.0, 220.0, 180.0),
                (180.0, 250.0, 220.0, 320.0),
            ],
        )
        events = detector.update([jitter])
        assert all(e.event_type != ZoneEventType.ZONE_ENTER for e in events)

    def test_multiple_zones_same_camera(self):
        detector = ZoneDetector([RECT_ZONE, CHECKOUT_ZONE], **HYST_1)
        # Foot at (300, 300) — inside both overlapping zones.
        t = _track(
            5,
            [(280.0, 100.0, 320.0, 180.0), (280.0, 250.0, 320.0, 320.0)],
        )
        events = detector.update([t])
        enters = [e for e in events if e.event_type == ZoneEventType.ZONE_ENTER]
        zone_ids = {e.zone_id for e in enters}
        assert zone_ids == {"test_rect", "checkout"}

    def test_ignores_wrong_camera(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        t = _track(
            6,
            [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
            camera_id="other_cam",
        )
        assert detector.update([t]) == []

    def test_track_id_zero(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        events = detector.update(
            [
                _track(
                    0,
                    [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
                )
            ]
        )
        assert len(events) == 1
        assert events[0].track_id == 0

    def test_disabled_zone_skipped(self):
        disabled = Zone(
            zone_id="off",
            zone_name="Off",
            camera_id="cam_1",
            polygon_coordinates=RECT_ZONE.polygon_coordinates,
            analytics_enabled=False,
        )
        detector = ZoneDetector([disabled], **HYST_1)
        t = _track(
            7,
            [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
        )
        assert detector.update([t]) == []

    def test_hysteresis_delays_enter(self):
        detector = ZoneDetector([RECT_ZONE], hysteresis_frames=2)
        # One inside frame — not enough for ENTER.
        t1 = _track(
            8,
            [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
        )
        assert detector.update([t1]) == []

        # Second consecutive inside frame — ENTER fires.
        t2 = _track(
            8,
            [
                (180.0, 100.0, 220.0, 180.0),
                (180.0, 250.0, 220.0, 320.0),
                (185.0, 255.0, 225.0, 325.0),
            ],
        )
        events = detector.update([t2])
        assert len(events) == 1
        assert events[0].event_type == ZoneEventType.ZONE_ENTER

    def test_hysteresis_suppresses_single_frame_boundary_flap(self):
        detector = ZoneDetector([RECT_ZONE], hysteresis_frames=2)
        # Enter (2 inside frames).
        detector.update(
            [
                _track(
                    9,
                    [
                        (180.0, 100.0, 220.0, 180.0),
                        (180.0, 250.0, 220.0, 320.0),
                        (185.0, 255.0, 225.0, 325.0),
                    ],
                )
            ]
        )
        # One-frame outside blip while still logically inside — no EXIT yet.
        blip = _track(
            9,
            [
                (185.0, 255.0, 225.0, 325.0),
                (180.0, 100.0, 220.0, 180.0),
                (185.0, 255.0, 225.0, 325.0),
            ],
        )
        events = detector.update([blip])
        assert all(e.event_type != ZoneEventType.ZONE_EXIT for e in events)


# --------------------------------------------------------------------------- #
# ZoneAnalytics
# --------------------------------------------------------------------------- #
class TestZoneAnalytics:
    def test_visitors_and_visits(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        analytics = ZoneAnalytics(RECT_ZONE, timezone="UTC")

        events = detector.update(
            [
                _track(1, [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)]),
                _track(2, [(190.0, 100.0, 230.0, 180.0), (190.0, 260.0, 230.0, 330.0)]),
            ]
        )
        for ev in events:
            analytics.process(ev)

        snap = analytics.snapshot()
        assert snap.zone_visitors == 2
        assert snap.total_visits == 2
        assert snap.current_occupancy == 2

    def test_dwell_time_on_exit(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        analytics = ZoneAnalytics(RECT_ZONE, timezone="UTC")
        base = 1000.0

        enter_track = _track(
            1,
            [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
            base_ts=base,
        )
        for ev in detector.update([enter_track]):
            analytics.process(ev)

        exit_track = _track(
            1,
            [
                (180.0, 250.0, 220.0, 320.0),
                (180.0, 100.0, 220.0, 180.0),
            ],
            base_ts=base + 10.0,
        )
        for ev in detector.update([exit_track]):
            snap = analytics.process(ev)

        assert snap.current_occupancy == 0
        assert snap.avg_dwell_time == pytest.approx(10.0)
        assert snap.max_dwell_time == pytest.approx(10.0)
        assert snap.min_dwell_time == pytest.approx(10.0)

    def test_traffic_by_hour(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        analytics = ZoneAnalytics(RECT_ZONE, timezone="UTC")
        ts = datetime(2026, 7, 27, 14, 30, tzinfo=timezone.utc).timestamp()
        t = _track(
            1,
            [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
            base_ts=ts,
        )
        for ev in detector.update([t]):
            snap = analytics.process(ev)
        assert snap.traffic_by_hour[14] == 1

    def test_event_to_dict(self):
        detector = ZoneDetector([RECT_ZONE], **HYST_1)
        events = detector.update(
            [
                _track(
                    1,
                    [(180.0, 100.0, 220.0, 180.0), (180.0, 250.0, 220.0, 320.0)],
                )
            ]
        )
        d = events[0].to_dict()
        assert d["event_type"] == "ZONE_ENTER"
        assert json.loads(json.dumps(d)) == d


class TestMultiZoneAnalytics:
    def test_routes_by_zone_id(self):
        multi = MultiZoneAnalytics([RECT_ZONE, CHECKOUT_ZONE])
        detector = ZoneDetector([RECT_ZONE, CHECKOUT_ZONE], **HYST_1)
        t = _track(
            1,
            [(280.0, 100.0, 320.0, 180.0), (280.0, 250.0, 320.0, 320.0)],
        )
        for ev in detector.update([t]):
            multi.process(ev)
        snaps = multi.all_snapshots()
        assert snaps["test_rect"].total_visits == 1
        assert snaps["checkout"].total_visits == 1


class TestVerifyHelpers:
    def test_detect_flapping(self):
        from analytics.zones import TransitionRecord

        transitions = [
            TransitionRecord(10.0, 10.0, "z1", "Z1", 1, ZoneEventType.ZONE_ENTER),
            TransitionRecord(11.0, 11.0, "z1", "Z1", 1, ZoneEventType.ZONE_EXIT),
        ]
        flaps = detect_flapping(transitions, max_gap_seconds=3.0)
        assert len(flaps) == 1
        assert flaps[0].gap_seconds == pytest.approx(1.0)


@pytest.mark.zones
class TestZonesIntegration:
    def test_detect_track_zone_pipeline(self, pytorch_detector, store_floor_video):
        from inference.tracking import Tracker
        from inference.video import create_video_source

        zone = Zone(
            zone_id="floor_center",
            zone_name="Floor Center",
            camera_id="store-floor",
            polygon_coordinates=((100.0, 100.0), (540.0, 100.0), (540.0, 300.0), (100.0, 300.0)),
        )
        detector = ZoneDetector([zone], hysteresis_frames=2)
        analytics = ZoneAnalytics(zone)
        tracker = Tracker(camera_id="store-floor", min_confirmation_frames=2)

        src = create_video_source(str(store_floor_video), target_fps=10)
        src.open()
        all_events = []
        for _ in range(40):
            ok, frame = src.read()
            if not ok:
                break
            dets = pytorch_detector.detect(frame, camera_id="store-floor")
            for ev in detector.update(tracker.update(dets)):
                all_events.append(ev)
                snap = analytics.process(ev)
                assert snap.current_occupancy >= 0
        src.release()

        for ev in all_events:
            assert ev.event_type in (
                ZoneEventType.ZONE_ENTER,
                ZoneEventType.ZONE_EXIT,
                ZoneEventType.ZONE_PRESENCE,
            )
            assert ev.camera_id == "store-floor"
