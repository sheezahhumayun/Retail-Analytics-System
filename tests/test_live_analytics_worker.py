"""Tests for the live analytics background worker."""

from __future__ import annotations

from unittest.mock import MagicMock

from inference.pipeline import live_analytics_worker as law


def test_stop_live_workers_for_org_targets_org_cameras(monkeypatch):
    stopped: list[str] = []
    monkeypatch.setattr(law, "_stop_camera", lambda camera_id: stopped.append(camera_id))

    law._analytics_states.clear()
    law._analytics_states["cam_a"] = MagicMock(org_id="org_one")
    law._analytics_states["cam_b"] = MagicMock(org_id="org_two")
    law._analytics_states["cam_c"] = MagicMock(org_id="org_one")

    count = law.stop_live_workers_for_org("org_one")

    assert count == 2
    assert set(stopped) == {"cam_a", "cam_c"}
