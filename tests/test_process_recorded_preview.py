"""Tests for recorded-camera preview frame path parsing."""

from __future__ import annotations

from backend.app.services.camera_process import _parse_subprocess_result


class TestProcessRecordedPreviewParsing:
    def test_parse_subprocess_result_extracts_preview_path(self):
        stdout = (
            "some log line\n"
            '{"camera_id": "cam_x", "status": "completed", '
            '"preview_frame_path": "data/frame-previews/cam_x/run_abc.jpg"}\n'
        )
        assert _parse_subprocess_result(stdout) == "data/frame-previews/cam_x/run_abc.jpg"

