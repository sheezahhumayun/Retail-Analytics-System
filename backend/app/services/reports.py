"""Report builders reusing Module 11 aggregate tables (Module 12.5)."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone as dt_timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlmodel import Session, col, select

from database.models import (
    DwellEventRow,
    Event,
    OccupancyMetric,
    QueueMetric,
    Store,
    VisitorMetric,
    ZoneMetric,
)

from ..config import get_settings
from ..exceptions import ApiError
from ..schemas.analytics import ComparisonInfo
from ..schemas.extended.reports import ReportHeader, ReportKpi, ReportPayload, ReportRow, ReportSeries
from .analytics_comparison import prior_period_bounds
from .report_eligibility import ReportScope, eligible_camera_ids, eligible_zone_ids, resolve_report_scope

ReportType = str

_ENTRY = "ENTRY"
_EXIT = "EXIT"


def _normalize_timezone(tz: str | ZoneInfo | dt_timezone) -> ZoneInfo | dt_timezone:
    if isinstance(tz, ZoneInfo):
        return tz
    if isinstance(tz, dt_timezone):
        return tz
    if str(tz).upper() == "UTC":
        return dt_timezone.utc
    try:
        return ZoneInfo(tz)
    except ZoneInfoNotFoundError:
        raise ZoneInfoNotFoundError(
            f"{tz!r} requires the tzdata package on Windows (pip install tzdata)"
        ) from None


def _local_parts(ts: datetime, tz: ZoneInfo | dt_timezone) -> tuple[date, int]:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=dt_timezone.utc)
    local = ts.astimezone(tz)
    return local.date(), local.hour


def build_report(
    session: Session,
    report_type: ReportType,
    *,
    store_id: str,
    start: datetime,
    end: datetime,
    camera_id: str | None = None,
    compare: bool = False,
) -> ReportPayload:
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")

    scope = resolve_report_scope(session, report_type, store_id, camera_id)
    header = ReportHeader(
        store_id=store_id,
        from_=start.isoformat(),
        to=end.isoformat(),
        generated_at=datetime.now(dt_timezone.utc).isoformat(),
        report_type=report_type,  # type: ignore[arg-type]
        camera_id=camera_id,
        coverage=scope.coverage,
    )

    if report_type == "traffic":
        payload = _traffic_report(session, header, scope, start, end, compare=compare)
    elif report_type == "occupancy":
        payload = _occupancy_report(session, header, scope, start, end, compare=compare)
    elif report_type == "zones":
        payload = _zones_report(session, header, scope, start, end, compare=compare)
    elif report_type == "dwell":
        payload = _dwell_report(session, header, scope, start, end, compare=compare)
    elif report_type == "queues":
        payload = _queues_report(session, header, scope, start, end, compare=compare)
    else:
        raise ApiError(400, "invalid_report_type", f"Unknown report type: {report_type}")

    payload.exclusions = scope.exclusions
    comparison_notes = list(payload.footnotes)
    payload.footnotes = [*scope.footnotes, *comparison_notes]
    return payload


def _with_scope_metadata(payload: ReportPayload, scope: ReportScope) -> ReportPayload:
    payload.exclusions = scope.exclusions
    payload.footnotes = scope.footnotes
    return payload


def _pct_change(current: float | int, prior: float | int | None) -> float | None:
    if prior is None or prior == 0:
        return None
    return round(((current - prior) / prior) * 100, 1)


def _comparison_footnote(comparison: ComparisonInfo | None) -> list[str]:
    if comparison is None:
        return []
    if comparison.status == "ok":
        return [f"Compared to prior period {comparison.from_} — {comparison.to}"]
    if comparison.message:
        return [comparison.message]
    return []


def _traffic_report(
    session: Session,
    header: ReportHeader,
    scope: ReportScope,
    start: datetime,
    end: datetime,
    *,
    compare: bool = False,
) -> ReportPayload:
    camera_ids = eligible_camera_ids(scope)
    settings = get_settings()
    tz = _normalize_timezone(settings.store_timezone)

    buckets: dict[tuple[Any, int], dict[str, int]] = defaultdict(lambda: {"entries": 0, "exits": 0})

    if camera_ids:
        events = session.exec(
            select(Event).where(
                col(Event.camera_id).in_(camera_ids),
                col(Event.event_type).in_([_ENTRY, _EXIT]),
                Event.timestamp >= start,
                Event.timestamp <= end,
            )
        ).all()
        for event in events:
            metric_date, hour = _local_parts(event.timestamp, tz)
            bucket = buckets[(metric_date, hour)]
            if event.event_type == _ENTRY:
                bucket["entries"] += 1
            else:
                bucket["exits"] += 1

    sorted_keys = sorted(buckets.keys())
    total_entries = sum(buckets[k]["entries"] for k in sorted_keys)
    total_exits = sum(buckets[k]["exits"] for k in sorted_keys)

    kpis = [
        ReportKpi(key="total_entries", label="Total entries", value=total_entries),
        ReportKpi(key="total_exits", label="Total exits", value=total_exits),
        ReportKpi(
            key="net_traffic",
            label="Net traffic",
            value=total_entries - total_exits,
        ),
        ReportKpi(
            key="coverage_cameras",
            label="Cameras in report",
            value=f"{scope.coverage.cameras_eligible}/{scope.coverage.cameras_in_scope}",
        ),
    ]
    series = [
        ReportSeries(
            name="entries",
            points=[
                {
                    "date": metric_date.isoformat(),
                    "hour": hour,
                    "value": buckets[(metric_date, hour)]["entries"],
                }
                for metric_date, hour in sorted_keys
            ],
        ),
        ReportSeries(
            name="exits",
            points=[
                {
                    "date": metric_date.isoformat(),
                    "hour": hour,
                    "value": buckets[(metric_date, hour)]["exits"],
                }
                for metric_date, hour in sorted_keys
            ],
        ),
    ]
    table = [
        ReportRow(
            columns={
                "date": metric_date.isoformat(),
                "hour": hour,
                "entries": buckets[(metric_date, hour)]["entries"],
                "exits": buckets[(metric_date, hour)]["exits"],
            }
        )
        for metric_date, hour in sorted_keys
    ]

    comparison: ComparisonInfo | None = None
    footnotes: list[str] = []
    if compare:
        from .analytics_comparison import build_comparison_info

        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = build_comparison_info(
            session,
            module=scope.module,
            cameras=scope.eligible_cameras,
            prior_start=prior_start,
            prior_end=prior_end,
        )
        footnotes = _comparison_footnote(comparison)
        if comparison.status == "ok":
            prior_buckets: dict[tuple[Any, int], dict[str, int]] = defaultdict(
                lambda: {"entries": 0, "exits": 0}
            )
            if camera_ids:
                prior_events = session.exec(
                    select(Event).where(
                        col(Event.camera_id).in_(camera_ids),
                        col(Event.event_type).in_([_ENTRY, _EXIT]),
                        Event.timestamp >= prior_start,
                        Event.timestamp <= prior_end,
                    )
                ).all()
                for event in prior_events:
                    metric_date, hour = _local_parts(event.timestamp, tz)
                    bucket = prior_buckets[(metric_date, hour)]
                    if event.event_type == _ENTRY:
                        bucket["entries"] += 1
                    else:
                        bucket["exits"] += 1
            prior_entries = sum(b["entries"] for b in prior_buckets.values())
            prior_exits = sum(b["exits"] for b in prior_buckets.values())
            kpis.extend(
                [
                    ReportKpi(
                        key="prior_total_entries",
                        label="Prior total entries",
                        value=prior_entries,
                    ),
                    ReportKpi(
                        key="entries_change_pct",
                        label="Entries change %",
                        value=_pct_change(total_entries, prior_entries) or "—",
                    ),
                ]
            )
            prior_sorted = sorted(prior_buckets.keys())
            prior_entry_values = [
                prior_buckets[key]["entries"] for key in prior_sorted
            ]
            for index, row in enumerate(table):
                prior_val = (
                    prior_entry_values[index] if index < len(prior_entry_values) else None
                )
                row.columns["prior_entries"] = prior_val if prior_val is not None else "—"
                change = _pct_change(row.columns["entries"], prior_val)
                row.columns["entries_change_pct"] = change if change is not None else "—"

    payload = ReportPayload(header=header, kpis=kpis, series=series, table=table)
    if comparison is not None:
        payload.comparison = comparison
    if footnotes:
        payload.footnotes = footnotes
    return payload


def _occupancy_report(
    session: Session,
    header: ReportHeader,
    scope: ReportScope,
    start: datetime,
    end: datetime,
    *,
    compare: bool = False,
) -> ReportPayload:
    camera_ids = eligible_camera_ids(scope)
    if not camera_ids:
        kpis = [
            ReportKpi(key="current_occupancy", label="Current occupancy", value=0),
            ReportKpi(key="peak_occupancy", label="Peak occupancy", value=0),
            ReportKpi(key="avg_occupancy", label="Average occupancy", value=0),
            ReportKpi(
                key="coverage_cameras",
                label="Cameras in report",
                value=f"0/{scope.coverage.cameras_in_scope}",
            ),
        ]
        return ReportPayload(header=header, kpis=kpis, series=[], table=[])

    rows = session.exec(
        select(OccupancyMetric)
        .where(
            col(OccupancyMetric.camera_id).in_(camera_ids),
            OccupancyMetric.timestamp >= start,
            OccupancyMetric.timestamp <= end,
        )
        .order_by(OccupancyMetric.timestamp)
    ).all()
    values = [r.current_occupancy for r in rows]
    current = values[-1] if values else 0
    peak = max(values) if values else 0
    avg = sum(values) / len(values) if values else 0
    kpis = [
        ReportKpi(key="current_occupancy", label="Current occupancy", value=current),
        ReportKpi(key="peak_occupancy", label="Peak occupancy", value=peak),
        ReportKpi(key="avg_occupancy", label="Average occupancy", value=round(avg, 2)),
        ReportKpi(
            key="coverage_cameras",
            label="Cameras in report",
            value=f"{scope.coverage.cameras_eligible}/{scope.coverage.cameras_in_scope}",
        ),
    ]
    series = [
        ReportSeries(
            name="occupancy",
            points=[
                {"timestamp": r.timestamp.isoformat(), "value": r.current_occupancy}
                for r in rows
            ],
        )
    ]
    table = [
        ReportRow(
            columns={
                "timestamp": r.timestamp.isoformat(),
                "camera_id": r.camera_id,
                "occupancy": r.current_occupancy,
            }
        )
        for r in rows
    ]
    comparison: ComparisonInfo | None = None
    footnotes: list[str] = []
    if compare:
        from .analytics_comparison import build_comparison_info

        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = build_comparison_info(
            session,
            module=scope.module,
            cameras=scope.eligible_cameras,
            prior_start=prior_start,
            prior_end=prior_end,
        )
        footnotes = _comparison_footnote(comparison)
        if comparison.status == "ok":
            prior_rows = session.exec(
                select(OccupancyMetric)
                .where(
                    col(OccupancyMetric.camera_id).in_(camera_ids),
                    OccupancyMetric.timestamp >= prior_start,
                    OccupancyMetric.timestamp <= prior_end,
                )
                .order_by(OccupancyMetric.timestamp)
            ).all()
            prior_values = [r.current_occupancy for r in prior_rows]
            prior_peak = max(prior_values) if prior_values else 0
            prior_avg = sum(prior_values) / len(prior_values) if prior_values else 0
            kpis.extend(
                [
                    ReportKpi(key="prior_peak_occupancy", label="Prior peak occupancy", value=prior_peak),
                    ReportKpi(
                        key="avg_occupancy_change_pct",
                        label="Avg occupancy change %",
                        value=_pct_change(avg, prior_avg) or "—",
                    ),
                ]
            )
            prior_by_ts = {r.timestamp.isoformat(): r.current_occupancy for r in prior_rows}
            prior_list = list(prior_by_ts.values())
            for index, row in enumerate(table):
                prior_val = prior_list[index] if index < len(prior_list) else None
                row.columns["prior_occupancy"] = prior_val if prior_val is not None else "—"
                change = _pct_change(row.columns["occupancy"], prior_val)
                row.columns["occupancy_change_pct"] = change if change is not None else "—"

    payload = ReportPayload(header=header, kpis=kpis, series=series, table=table)
    if comparison is not None:
        payload.comparison = comparison
    if footnotes:
        payload.footnotes = footnotes
    return payload


def _zones_report(
    session: Session,
    header: ReportHeader,
    scope: ReportScope,
    start: datetime,
    end: datetime,
    *,
    compare: bool = False,
) -> ReportPayload:
    zone_ids = eligible_zone_ids(scope)
    if not zone_ids:
        kpis = [
            ReportKpi(key="total_visitors", label="Total zone visitors", value=0),
            ReportKpi(key="zone_count", label="Zones in report", value=0),
            ReportKpi(
                key="coverage_zones",
                label="Zones in report",
                value=f"0/{scope.coverage.zones_in_scope}",
            ),
        ]
        return ReportPayload(header=header, kpis=kpis, series=[], table=[])

    rows = session.exec(
        select(ZoneMetric)
        .where(
            col(ZoneMetric.zone_id).in_(zone_ids),
            ZoneMetric.metric_date >= start.date(),
            ZoneMetric.metric_date <= end.date(),
        )
        .order_by(ZoneMetric.zone_id, ZoneMetric.metric_date, ZoneMetric.hour)
    ).all()
    total_visitors = sum(r.visitors for r in rows)
    kpis = [
        ReportKpi(key="total_visitors", label="Total zone visitors", value=total_visitors),
        ReportKpi(key="zone_count", label="Zones in report", value=len(zone_ids)),
        ReportKpi(
            key="coverage_zones",
            label="Zones in report",
            value=f"{scope.coverage.zones_eligible}/{scope.coverage.zones_in_scope}",
        ),
    ]
    series = [
        ReportSeries(
            name="visitors",
            points=[
                {
                    "zone_id": r.zone_id,
                    "date": r.metric_date.isoformat(),
                    "hour": r.hour,
                    "value": r.visitors,
                }
                for r in rows
            ],
        )
    ]
    table = [
        ReportRow(
            columns={
                "zone_id": r.zone_id,
                "date": r.metric_date.isoformat(),
                "hour": r.hour,
                "visitors": r.visitors,
                "avg_dwell": r.avg_dwell,
            }
        )
        for r in rows
    ]
    comparison: ComparisonInfo | None = None
    footnotes: list[str] = []
    if compare:
        from .analytics_comparison import build_comparison_info

        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = build_comparison_info(
            session,
            module=scope.module,
            cameras=scope.eligible_cameras,
            prior_start=prior_start,
            prior_end=prior_end,
        )
        footnotes = _comparison_footnote(comparison)
        if comparison.status == "ok":
            prior_rows = session.exec(
                select(ZoneMetric)
                .where(
                    col(ZoneMetric.zone_id).in_(zone_ids),
                    ZoneMetric.metric_date >= prior_start.date(),
                    ZoneMetric.metric_date <= prior_end.date(),
                )
                .order_by(ZoneMetric.zone_id, ZoneMetric.metric_date, ZoneMetric.hour)
            ).all()
            prior_total = sum(r.visitors for r in prior_rows)
            kpis.extend(
                [
                    ReportKpi(key="prior_total_visitors", label="Prior total visitors", value=prior_total),
                    ReportKpi(
                        key="visitors_change_pct",
                        label="Visitors change %",
                        value=_pct_change(total_visitors, prior_total) or "—",
                    ),
                ]
            )
            prior_by_index = [r.visitors for r in prior_rows]
            for index, row in enumerate(table):
                prior_val = prior_by_index[index] if index < len(prior_by_index) else None
                row.columns["prior_visitors"] = prior_val if prior_val is not None else "—"
                change = _pct_change(row.columns["visitors"], prior_val)
                row.columns["visitors_change_pct"] = change if change is not None else "—"

    payload = ReportPayload(header=header, kpis=kpis, series=series, table=table)
    if comparison is not None:
        payload.comparison = comparison
    if footnotes:
        payload.footnotes = footnotes
    return payload


def _dwell_report(
    session: Session,
    header: ReportHeader,
    scope: ReportScope,
    start: datetime,
    end: datetime,
    *,
    compare: bool = False,
) -> ReportPayload:
    zone_ids = eligible_zone_ids(scope)
    if not zone_ids:
        kpis = [
            ReportKpi(key="session_count", label="Dwell sessions", value=0),
            ReportKpi(key="avg_dwell_seconds", label="Avg dwell (s)", value=0),
            ReportKpi(
                key="coverage_zones",
                label="Zones in report",
                value=f"0/{scope.coverage.zones_in_scope}",
            ),
        ]
        return ReportPayload(header=header, kpis=kpis, series=[], table=[])

    rows = session.exec(
        select(DwellEventRow)
        .where(
            col(DwellEventRow.zone_id).in_(zone_ids),
            DwellEventRow.enter_ts >= start,
            DwellEventRow.enter_ts <= end,
        )
        .order_by(DwellEventRow.enter_ts)
    ).all()
    dwell_values = [r.dwell_seconds for r in rows]
    avg_dwell = sum(dwell_values) / len(dwell_values) if dwell_values else 0
    kpis = [
        ReportKpi(key="session_count", label="Dwell sessions", value=len(rows)),
        ReportKpi(key="avg_dwell_seconds", label="Avg dwell (s)", value=round(avg_dwell, 2)),
        ReportKpi(
            key="coverage_zones",
            label="Zones in report",
            value=f"{scope.coverage.zones_eligible}/{scope.coverage.zones_in_scope}",
        ),
    ]
    series = [
        ReportSeries(
            name="dwell_seconds",
            points=[
                {
                    "zone_id": r.zone_id,
                    "enter_ts": r.enter_ts.isoformat(),
                    "value": r.dwell_seconds,
                }
                for r in rows
            ],
        )
    ]
    table = [
        ReportRow(
            columns={
                "zone_id": r.zone_id,
                "track_id": r.track_id,
                "enter_ts": r.enter_ts.isoformat(),
                "exit_ts": r.exit_ts.isoformat(),
                "dwell_seconds": r.dwell_seconds,
            }
        )
        for r in rows
    ]
    comparison: ComparisonInfo | None = None
    footnotes: list[str] = []
    if compare:
        from .analytics_comparison import build_comparison_info

        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = build_comparison_info(
            session,
            module=scope.module,
            cameras=scope.eligible_cameras,
            prior_start=prior_start,
            prior_end=prior_end,
        )
        footnotes = _comparison_footnote(comparison)
        if comparison.status == "ok":
            prior_rows = session.exec(
                select(DwellEventRow)
                .where(
                    col(DwellEventRow.zone_id).in_(zone_ids),
                    DwellEventRow.enter_ts >= prior_start,
                    DwellEventRow.enter_ts <= prior_end,
                )
                .order_by(DwellEventRow.enter_ts)
            ).all()
            prior_avg = (
                sum(r.dwell_seconds for r in prior_rows) / len(prior_rows)
                if prior_rows
                else 0
            )
            kpis.extend(
                [
                    ReportKpi(key="prior_session_count", label="Prior dwell sessions", value=len(prior_rows)),
                    ReportKpi(
                        key="avg_dwell_change_pct",
                        label="Avg dwell change %",
                        value=_pct_change(avg_dwell, prior_avg) or "—",
                    ),
                ]
            )

    payload = ReportPayload(header=header, kpis=kpis, series=series, table=table)
    if comparison is not None:
        payload.comparison = comparison
    if footnotes:
        payload.footnotes = footnotes
    return payload


def _queues_report(
    session: Session,
    header: ReportHeader,
    scope: ReportScope,
    start: datetime,
    end: datetime,
    *,
    compare: bool = False,
) -> ReportPayload:
    zone_ids = eligible_zone_ids(scope)
    if not zone_ids:
        kpis = [
            ReportKpi(key="avg_queue_length", label="Avg queue length", value=0),
            ReportKpi(key="max_queue_length", label="Max queue length", value=0),
            ReportKpi(
                key="coverage_zones",
                label="Queue zones in report",
                value=f"0/{scope.coverage.zones_in_scope}",
            ),
        ]
        return ReportPayload(header=header, kpis=kpis, series=[], table=[])

    rows = session.exec(
        select(QueueMetric)
        .where(
            col(QueueMetric.zone_id).in_(zone_ids),
            QueueMetric.timestamp >= start,
            QueueMetric.timestamp <= end,
        )
        .order_by(QueueMetric.timestamp)
    ).all()
    lengths = [r.queue_length for r in rows]
    avg_len = sum(lengths) / len(lengths) if lengths else 0
    max_len = max(lengths) if lengths else 0
    kpis = [
        ReportKpi(key="avg_queue_length", label="Avg queue length", value=round(avg_len, 2)),
        ReportKpi(key="max_queue_length", label="Max queue length", value=max_len),
        ReportKpi(
            key="coverage_zones",
            label="Queue zones in report",
            value=f"{scope.coverage.zones_eligible}/{scope.coverage.zones_in_scope}",
        ),
    ]
    series = [
        ReportSeries(
            name="queue_length",
            points=[
                {
                    "zone_id": r.zone_id,
                    "timestamp": r.timestamp.isoformat(),
                    "value": r.queue_length,
                }
                for r in rows
            ],
        )
    ]
    table = [
        ReportRow(
            columns={
                "zone_id": r.zone_id,
                "timestamp": r.timestamp.isoformat(),
                "queue_length": r.queue_length,
                "estimated_wait": r.estimated_wait,
            }
        )
        for r in rows
    ]
    comparison: ComparisonInfo | None = None
    footnotes: list[str] = []
    if compare:
        from .analytics_comparison import build_comparison_info

        prior_start, prior_end = prior_period_bounds(start, end)
        comparison = build_comparison_info(
            session,
            module=scope.module,
            cameras=scope.eligible_cameras,
            prior_start=prior_start,
            prior_end=prior_end,
        )
        footnotes = _comparison_footnote(comparison)
        if comparison.status == "ok":
            prior_rows = session.exec(
                select(QueueMetric)
                .where(
                    col(QueueMetric.zone_id).in_(zone_ids),
                    QueueMetric.timestamp >= prior_start,
                    QueueMetric.timestamp <= prior_end,
                )
                .order_by(QueueMetric.timestamp)
            ).all()
            prior_lengths = [r.queue_length for r in prior_rows]
            prior_avg = sum(prior_lengths) / len(prior_lengths) if prior_lengths else 0
            prior_max = max(prior_lengths) if prior_lengths else 0
            kpis.extend(
                [
                    ReportKpi(key="prior_avg_queue_length", label="Prior avg queue length", value=round(prior_avg, 2)),
                    ReportKpi(
                        key="avg_queue_change_pct",
                        label="Avg queue change %",
                        value=_pct_change(avg_len, prior_avg) or "—",
                    ),
                ]
            )
            for index, row in enumerate(table):
                prior_val = prior_lengths[index] if index < len(prior_lengths) else None
                row.columns["prior_queue_length"] = prior_val if prior_val is not None else "—"
                change = _pct_change(row.columns["queue_length"], prior_val)
                row.columns["queue_change_pct"] = change if change is not None else "—"

    payload = ReportPayload(header=header, kpis=kpis, series=series, table=table)
    if comparison is not None:
        payload.comparison = comparison
    if footnotes:
        payload.footnotes = footnotes
    return payload


from .report_export import report_to_csv, report_to_pdf  # noqa: E402
