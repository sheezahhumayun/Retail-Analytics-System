"""Unit tests for hourly zone-metric range filtering (no database)."""

from __future__ import annotations

from datetime import date, datetime, time, timezone

from backend.app.services.analytics_read import _bucket_overlaps_range


def _visitors_in_range(
    rows: list[tuple[int, int]],
    metric_date: date,
    start: datetime,
    end: datetime,
    tz=timezone.utc,
) -> int:
    total = 0
    for hour, visitors in rows:
        if _bucket_overlaps_range(metric_date, hour, start, end, tz):
            total += visitors
    return total


class TestZoneBucketRange:
    def test_narrow_window_excludes_other_hours(self):
        metric_date = date(2026, 8, 12)
        rows = [(10, 5), (12, 20), (14, 8)]

        wide_start = datetime.combine(metric_date, time(9, 0), tzinfo=timezone.utc)
        wide_end = datetime.combine(metric_date, time(21, 0), tzinfo=timezone.utc)
        narrow_start = datetime.combine(metric_date, time(11, 0), tzinfo=timezone.utc)
        narrow_end = datetime.combine(metric_date, time(13, 0), tzinfo=timezone.utc)

        wide_total = _visitors_in_range(rows, metric_date, wide_start, wide_end)
        narrow_total = _visitors_in_range(rows, metric_date, narrow_start, narrow_end)

        assert wide_total == 33
        assert narrow_total == 20
        assert wide_total != narrow_total
