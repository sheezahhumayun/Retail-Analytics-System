"""Module 1 — Video Ingestion Layer tests.

These run against the real sample videos via OpenCV — no mocks, no network.
The RTSP reconnect state machine is unit-tested against an injected fake
``VideoCapture`` so it needs no live stream.

Run:   python -m pytest tests/                 (everything except webcam/rtsp)
       python -m pytest tests/ -m 'not slow'   (skip slow sweeps)
"""

from __future__ import annotations

import importlib
import sys
from datetime import datetime
from pathlib import Path

import pytest

# `inference` package may be installed (later) or just on sys.path (conftest).
inference = importlib.import_module("inference.video")
FileVideoSource = inference.FileVideoSource
RTSPVideoSource = inference.RTSPVideoSource
WebcamVideoSource = inference.WebcamVideoSource
create_video_source = inference.create_video_source
CameraState = inference.CameraState
VideoSourceError = inference.VideoSourceError
compute_frame_interval = inference.compute_frame_interval
resize_long_side = inference.resize_long_side

import numpy as np  # noqa: E402

# Known properties captured in PROJECT_STATUS.md / Module 0 verification.
EXPECTED_PROPS = {
    "entrance.mp4": dict(fps=29.97, w=2560, h=1440),
    "store-floor.mp4": dict(fps=30.0, w=1920, h=1080),
    "checkout.mp4": dict(fps=30.0, w=1920, h=1080),
}


# ===================================================================== #
# Open / fps / resolution
# ===================================================================== #
@pytest.mark.parametrize("name", list(EXPECTED_PROPS.keys()))
def test_open_reports_known_source_properties(sample_data_dir: Path, name: str):
    if not (sample_data_dir / name).exists():
        pytest.skip(f"{name} not present")
    src = FileVideoSource(sample_data_dir / name)
    src.open()
    try:
        exp = EXPECTED_PROPS[name]
        assert src.is_live() is False
        assert src.get_source_resolution() == (exp["w"], exp["h"])
        assert abs(src.get_fps() - exp["fps"]) < 0.5
    finally:
        src.release()


def test_missing_file_raises_on_open(tmp_path: Path):
    src = FileVideoSource(tmp_path / "does_not_exist.mp4")
    with pytest.raises(VideoSourceError):
        src.open()
    assert src.get_state() is CameraState.ERROR


# ===================================================================== #
# Downscale contract (CPU reality check)
# ===================================================================== #
def test_read_returns_downscaled_frame(sample_videos: list[Path]):
    src = FileVideoSource(sample_videos[0], target_long_side=640)
    src.open()
    try:
        ok, frame = src.read()
        assert ok and frame is not None
        h, w = frame.shape[:2]
        # Long side must be <= 640; aspect ratio preserved (w/h unchanged).
        assert max(w, h) <= 640
        src_w, src_h = src.get_source_resolution()
        assert abs((w / h) - (src_w / src_h)) < 1e-3
    finally:
        src.release()


def test_no_downscale_when_already_small():
    """Synthetic frame already under the cap must pass through unchanged."""
    small = np.zeros((100, 200, 3), dtype=np.uint8)  # long side 200 < 640
    out = resize_long_side(small, 640)
    assert out.shape == small.shape


# ===================================================================== #
# Throttle contract — the heart of "this layer decides which frames to hand off"
# ===================================================================== #
def test_throttle_keeps_every_third_frame_at_30fps_target_10(sample_videos):
    """30fps source + 10fps target => interval 3 => keep 1 of every 3."""
    src = FileVideoSource(sample_videos[0], target_fps=10.0)
    src.open()
    try:
        assert compute_frame_interval(30.0, 10.0) == 3
        kept_indices = []
        # Consume enough underlying reads to collect several kept frames.
        # Each read() call advances the underlying stream by `interval` frames
        # and returns exactly one kept frame, so the kept cadence == interval.
        for _ in range(5):
            ok, _frame = src.read()
            assert ok
            kept_indices.append(src._frame_index)
        # Difference between successive kept frame indices is the interval.
        deltas = [b - a for a, b in zip(kept_indices, kept_indices[1:])]
        assert all(d == 3 for d in deltas), deltas
    finally:
        src.release()


def test_timestamps_follow_source_media_time(sample_videos):
    """Kept-frame timestamps use source frame index / source fps, not target fps."""
    src = FileVideoSource(sample_videos[0], target_fps=10.0)
    src.open()
    try:
        source_fps = src.get_fps()
        timestamps: list[float] = []
        for _ in range(5):
            ok, _ = src.read()
            assert ok
            timestamps.append(src.get_last_timestamp())
        # Media time advances by interval/source_fps between kept frames.
        interval = compute_frame_interval(source_fps, 10.0)
        expected_delta = interval / source_fps
        deltas = [b - a for a, b in zip(timestamps, timestamps[1:])]
        for d in deltas:
            assert abs(d - expected_delta) < 0.05, (d, expected_delta)
        assert src.get_kept_frame_count() == 5
    finally:
        src.release()


def test_media_duration_from_file_metadata(sample_videos):
    src = FileVideoSource(sample_videos[0])
    src.open()
    try:
        dur = src.get_media_duration()
        assert dur is not None and dur > 0
        # Last timestamp after full read should not exceed duration by much.
        last_ts = 0.0
        while True:
            ok, _ = src.read()
            if not ok:
                break
            last_ts = src.get_last_timestamp()
        assert last_ts <= dur + 0.5
    finally:
        src.release()


def test_throttle_interval_helper_guards_bad_fps():
    # Bad source fps -> falls back to 30, so 30/10 == 3.
    assert compute_frame_interval(0.0, 10.0) == 3
    assert compute_frame_interval(float("nan"), 10.0) == 3
    # Bad target fps -> interval clamps to 1 (no skipping).
    assert compute_frame_interval(30.0, 0.0) == 1
    assert compute_frame_interval(30.0, -5.0) == 1
    # Identity rate -> 1 (keep everything).
    assert compute_frame_interval(30.0, 30.0) == 1
    # Target > source -> can't go faster than source, clamp to 1.
    assert compute_frame_interval(15.0, 60.0) == 1


def test_target_fps_handled_symmetrically_across_sources():
    """File, RTSP, and Webcam all accept the same throttle kwargs."""
    f = FileVideoSource("x.mp4", target_fps=5, target_long_side=320)
    assert f._target_fps == 5 and f._target_long_side == 320
    r = RTSPVideoSource("rtsp://x", target_fps=5, target_long_side=320)
    assert r._target_fps == 5 and r._target_long_side == 320
    w = WebcamVideoSource(0, target_fps=5, target_long_side=320)
    assert w._target_fps == 5 and w._target_long_side == 320


# ===================================================================== #
# Factory routing — downstream code never branches on source type
# ===================================================================== #
def test_factory_routes_file(sample_videos: list[Path]):
    src = create_video_source(str(sample_videos[0]))
    assert isinstance(src, FileVideoSource)
    assert src.is_live() is False


def test_factory_routes_rtsp():
    src = create_video_source("rtsp://10.0.0.5:554/stream")
    assert isinstance(src, RTSPVideoSource)
    assert src.is_live() is True
    # rtsps:// and rtmp:// also route to RTSP source.
    assert isinstance(create_video_source("rtsps://x"), RTSPVideoSource)
    assert isinstance(create_video_source("rtmp://x"), RTSPVideoSource)


def test_factory_routes_webcam_by_int():
    src = create_video_source(0)
    assert isinstance(src, WebcamVideoSource)
    assert src.is_live() is True
    assert src.device_index == 0


def test_factory_passes_target_fps_and_long_side():
    src = create_video_source("rtsp://x", target_fps=4, target_long_side=512)
    assert src._target_fps == 4 and src._target_long_side == 512


# ===================================================================== #
# Camera state machine (PRD §8), as observed from this layer
# ===================================================================== #
def test_state_transitions_for_file(sample_videos: list[Path]):
    src = FileVideoSource(sample_videos[0])
    # Before open: OFFLINE.
    assert src.get_state() is CameraState.OFFLINE

    src.open()
    # After open, before first successful read: PROCESSING.
    assert src.get_state() is CameraState.PROCESSING

    ok, _ = src.read()
    assert ok
    # First produced frame flips to ONLINE.
    assert src.get_state() is CameraState.ONLINE

    src.release()
    assert src.get_state() is CameraState.OFFLINE


def test_disable_then_open_raises(sample_videos: list[Path]):
    src = FileVideoSource(sample_videos[0])
    src.disable()
    assert src.get_state() is CameraState.DISABLED
    with pytest.raises(VideoSourceError):
        src.open()


def test_eof_returns_false_for_files(sample_videos: list[Path]):
    """A finite file must end cleanly with (False, None), not raise."""
    src = FileVideoSource(sample_videos[0], target_fps=1000)  # keep every frame
    src.open()
    ok_any = False
    last = False, None
    # Drain the whole file (these are short sample clips).
    for _ in range(100000):
        last = src.read()
        if not last[0]:
            break
        ok_any = True
    assert ok_any, "never read a single frame"
    assert last == (False, None)
    src.release()


# ===================================================================== #
# Context manager
# ===================================================================== #
def test_context_manager_opens_and_releases(sample_videos: list[Path]):
    with FileVideoSource(sample_videos[0]) as src:
        assert src.get_state() in (CameraState.PROCESSING, CameraState.ONLINE)
        ok, frame = src.read()
        assert ok and frame is not None
    assert src.get_state() is CameraState.OFFLINE


# ===================================================================== #
# RTSP reconnect state machine — unit-tested with an injected fake capture.
# No network needed.
# ===================================================================== #
class _FakeCapture:
    """Minimal stand-in for cv2.VideoCapture with scriptable failures.

    Two independent failure modes, matching the two real-world RTSP problems:
      * ``open_ok=False``  -> the NVR is unreachable; isOpened() is False so the
        connect itself fails (this is what ``reconnect_attempts`` exhaustion
        guards against).
      * ``fail_reads>0``   -> the NVR accepts the connection but drops frames
        (intermittent drops; recovered by the threshold-based reconnect).
    """

    def __init__(
        self,
        fail_reads: int = 0,
        open_ok: bool = True,
        fps: float = 30.0,
        w: int = 1920,
        h: int = 1080,
    ):
        self.remaining_failures = fail_reads
        self.open_ok = open_ok
        self.fps = fps
        self.w = w
        self.h = h
        self.released = False

    def isOpened(self):
        return self.open_ok and not self.released

    def get(self, prop):
        # cv2.CAP_PROP_FPS=5, CAP_PROP_FRAME_WIDTH=3, CAP_PROP_FRAME_HEIGHT=4
        if prop == 5:
            return float(self.fps)
        if prop == 3:
            return float(self.w)
        if prop == 4:
            return float(self.h)
        return 0.0

    def read(self):
        if self.remaining_failures > 0:
            self.remaining_failures -= 1
            return False, None
        # Return a tiny frame so resize_long_side has real dims to work with.
        return True, np.zeros((self.h, self.w, 3), dtype=np.uint8)

    def release(self):
        self.released = True


def test_rtsp_reconnect_recovers_from_drops():
    """N consecutive read failures trigger a reopen that then succeeds.

    Models a real CCTV hiccup: the NVR is reachable (opens fine) but drops a
    burst of frames; after the threshold we reopen and frames flow again.
    read() never raises during any of this.
    """
    fresh_captures: list[_FakeCapture] = []

    def factory(url):
        # First capture opens fine but drops 6 reads (> default threshold of 5);
        # the reconnect builds a fresh capture that succeeds immediately.
        if not fresh_captures:
            fresh_captures.append(_FakeCapture(fail_reads=6))
        else:
            fresh_captures.append(_FakeCapture(fail_reads=0))
        return fresh_captures[-1]

    src = RTSPVideoSource(
        "rtsp://fake/stream",
        reconnect_threshold=5,
        reconnect_attempts=3,
        backoff_base=0,  # don't actually sleep in the test
        backoff_max=0,
        _capture_factory=factory,
    )
    src._sleep = lambda _s: None  # belt-and-braces: no real sleeping
    src.open()
    assert src.get_state() is CameraState.PROCESSING

    # Reads fail until the threshold is crossed; then a reconnect happens and
    # subsequent reads succeed. read() never raises.
    got = False
    for _ in range(20):
        ok, frame = src.read()
        if ok:
            got = True
            break
    assert got, "did not recover after reconnect"
    assert len(fresh_captures) == 2, "expected exactly one reconnect"
    assert src.get_state() is CameraState.ONLINE
    src.release()


def test_rtsp_stays_in_error_when_reconnect_exhausted():
    """Stream opens fine, then drops; every reconnect attempt fails (NVR went
    fully down). After ``reconnect_attempts`` the source settles in ERROR and
    read() keeps returning (False, None) rather than raising — callers poll."""

    calls = {"n": 0}

    def factory(url):
        calls["n"] += 1
        # Call #1 is the initial open() -> succeeds but drops every read.
        # Calls #2.. are reconnect attempts inside _reconnect() -> unreachable.
        if calls["n"] == 1:
            return _FakeCapture(fail_reads=10_000)
        return _FakeCapture(open_ok=False)

    src = RTSPVideoSource(
        "rtsp://dead/stream",
        reconnect_threshold=2,
        reconnect_attempts=2,
        backoff_base=0,
        backoff_max=0,
        retry_after_exhaustion=10_000.0,  # never re-trigger during the test
        _capture_factory=factory,
    )
    src._sleep = lambda _s: None
    src._monotonic = lambda: 0.0
    src.open()  # initial open succeeds

    # Hammer read(); it must keep returning (False, None) without raising and
    # the state must settle in ERROR once reconnect attempts are exhausted.
    last_state = None
    for _ in range(15):
        ok, frame = src.read()
        assert ok is False and frame is None
        last_state = src.get_state()
    assert last_state is CameraState.ERROR
    src.release()


def test_rtsp_recovers_after_exhaustion_cooldown():
    """After a full reconnect cycle is exhausted, the source retries once the
    cooldown elapses and recovers if the NVR has come back online."""

    calls = {"n": 0}

    def factory(url):
        calls["n"] += 1
        if calls["n"] == 1:
            # Initial open: works, then drops every read -> triggers reconnect.
            return _FakeCapture(fail_reads=10_000)
        if calls["n"] == 2:
            # First reconnect attempt during exhaustion: NVR still down.
            return _FakeCapture(open_ok=False)
        # Subsequent reconnect (after cooldown): NVR is back and healthy.
        return _FakeCapture(fail_reads=0)

    src = RTSPVideoSource(
        "rtsp://flaky/stream",
        reconnect_threshold=2,
        reconnect_attempts=1,
        backoff_base=0,
        backoff_max=0,
        retry_after_exhaustion=10.0,
        _capture_factory=factory,
    )
    src._sleep = lambda _s: None

    # Drive a fake clock so we can advance past the cooldown deterministically.
    t = {"now": 0.0}
    src._monotonic = lambda: t["now"]

    src.open()  # initial open succeeds

    # Drain reads until the threshold trips a reconnect that exhausts (the one
    # failing reconnect attempt) -> ERROR.
    for _ in range(10):
        src.read()
    assert src.get_state() is CameraState.ERROR

    # read() while still within cooldown -> stays ERROR, no frame.
    ok, frame = src.read()
    assert ok is False and frame is None
    assert src.get_state() is CameraState.ERROR

    # Advance the clock past the cooldown; the next read() should trigger a
    # reconnect that this time succeeds, then produce a frame -> ONLINE.
    t["now"] = 11.0
    got = False
    for _ in range(3):
        ok, frame = src.read()
        if ok:
            got = True
            break
    assert got, "did not recover after the cooldown"
    assert src.get_state() is CameraState.ONLINE
    src.release()


def test_rtsp_open_failure_raises_and_sets_error():
    def factory(url):
        cap = _FakeCapture(fail_reads=0)
        cap.released = True  # force isOpened() False
        return cap

    src = RTSPVideoSource("rtsp://nope", _capture_factory=factory)
    with pytest.raises(VideoSourceError):
        src.open()
    assert src.get_state() is CameraState.ERROR


# ===================================================================== #
# Live hardware gates (skipped by default; opt-in with -m webcam / -m rtsp)
# ===================================================================== #
@pytest.mark.webcam
def test_real_webcam_open():
    src = WebcamVideoSource(0)
    try:
        src.open()
        ok, frame = src.read()
        assert ok and frame is not None
    finally:
        src.release()


@pytest.mark.rtsp
def test_real_rtsp_open():
    import os

    url = os.environ.get("RTSP_TEST_URL")
    if not url:
        pytest.skip("set RTSP_TEST_URL to run")
    src = RTSPVideoSource(url)
    try:
        src.open()
        ok, frame = src.read()
        assert ok and frame is not None
    finally:
        src.release()


def test_anchor_timestamp_live_returns_input():
    anchor_timestamp = inference.anchor_timestamp
    assert anchor_timestamp(123.5, True, None) == 123.5
    start = datetime.fromisoformat("2026-08-11T09:00:00+00:00")
    assert anchor_timestamp(123.5, True, start) == 123.5


def test_anchor_timestamp_file_with_recording_start():
    anchor_timestamp = inference.anchor_timestamp
    start = datetime.fromisoformat("2026-08-11T09:00:00+00:00")
    assert anchor_timestamp(30.0, False, start) == start.timestamp() + 30.0


def test_anchor_timestamp_file_without_recording_start():
    anchor_timestamp = inference.anchor_timestamp
    assert anchor_timestamp(42.0, False, None) == 42.0
