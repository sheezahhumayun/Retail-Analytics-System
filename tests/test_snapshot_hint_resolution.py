"""Contract tests for snapshot preview hint resolution (mirrors frontend logic)."""

from __future__ import annotations


def resolve_snapshot_hint(
    camera_status: str | None,
    source_type: str | None,
    snapshot_unavailable: bool,
) -> str | None:
    if not snapshot_unavailable:
        return None
    if camera_status == "error":
        return "source_unavailable"
    if source_type == "recorded" and camera_status == "online":
        return "process_first"
    return None


SNAPSHOT_HINT_MESSAGES = {
    "source_unavailable": "Camera source unavailable",
    "process_first": "Process this camera to see a real camera view here.",
}


class TestSnapshotHintResolution:
    def test_error_status_shows_source_unavailable(self):
        kind = resolve_snapshot_hint("error", "recorded", True)
        assert kind == "source_unavailable"
        assert SNAPSHOT_HINT_MESSAGES[kind] == "Camera source unavailable"

    def test_online_recorded_without_snapshot_shows_process_first(self):
        kind = resolve_snapshot_hint("online", "recorded", True)
        assert kind == "process_first"
        assert SNAPSHOT_HINT_MESSAGES[kind] == (
            "Process this camera to see a real camera view here."
        )

    def test_snapshot_available_shows_no_hint(self):
        assert resolve_snapshot_hint("online", "recorded", False) is None

    def test_live_online_snapshot_failure_has_no_recorded_hint(self):
        assert resolve_snapshot_hint("online", "live", True) is None
