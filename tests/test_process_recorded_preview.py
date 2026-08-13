"""Tests for recorded-camera preview frame path on completed runs."""

from __future__ import annotations


class TestProcessRecordedPreviewResult:
    def test_result_includes_preview_frame_path(self):
        result = {
            "camera_id": "cam_x",
            "status": "completed",
            "preview_frame_path": "data/frame-previews/cam_x/run_abc.jpg",
        }
        assert result["preview_frame_path"] == "data/frame-previews/cam_x/run_abc.jpg"
