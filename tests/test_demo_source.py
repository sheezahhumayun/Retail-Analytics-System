"""Unit tests for tests/scripts/demo_source.py helpers."""

from __future__ import annotations

import pytest

from tests.scripts.demo_source import (
    is_live_source_spec,
    parse_source_spec,
    resolve_camera_id,
    resolve_duration,
)


def test_parse_webcam_index():
    assert parse_source_spec("0") == 0
    assert parse_source_spec(" 1 ") == 1


def test_parse_rtsp_and_file():
    assert parse_source_spec("rtsp://10.0.0.5/stream") == "rtsp://10.0.0.5/stream"
    assert parse_source_spec("sample-data/store.mp4") == "sample-data/store.mp4"


def test_is_live_source_spec():
    assert is_live_source_spec("0") is True
    assert is_live_source_spec("rtsp://x") is True
    assert is_live_source_spec("rtsps://x") is True
    assert is_live_source_spec("sample.mp4") is False


def test_resolve_camera_id():
    assert resolve_camera_id("sample-data/store.mp4") == "store"
    assert resolve_camera_id("0") == "webcam-0"
    assert resolve_camera_id("rtsp://10.0.0.5/stream") == "10-0-0-5"
    assert resolve_camera_id("sample.mp4", "custom") == "custom"


def test_resolve_duration_defaults():
    assert resolve_duration("sample.mp4", None) is None
    assert resolve_duration("sample.mp4", 30.0) == 30.0
    assert resolve_duration("sample.mp4", 0) is None
    assert resolve_duration("0", None) == pytest.approx(120.0)
    assert resolve_duration("0", 0) is None
