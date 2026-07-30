"""Report builders reusing Module 11 aggregate tables (Module 12.5)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from sqlmodel import Session, col, select

from database.models import (
    Camera,
    DwellEventRow,
    OccupancyMetric,
    QueueMetric,
    Store,
    VisitorMetric,
    Zone,
    ZoneMetric,
)

from ..exceptions import ApiError
from ..schemas.extended.reports import ReportHeader, ReportKpi, ReportPayload, ReportRow, ReportSeries

ReportType = Literal["traffic", "occupancy", "zones", "dwell", "queues"]


def build_report(
    session: Session,
    report_type: ReportType,
    *,
    store_id: str,
    start: datetime,
    end: datetime,
) -> ReportPayload:
    if session.get(Store, store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")

    header = ReportHeader(
        store_id=store_id,
        from_=start.isoformat(),
        to=end.isoformat(),
        generated_at=datetime.now(timezone.utc).isoformat(),
        report_type=report_type,
    )

    if report_type == "traffic":
        return _traffic_report(session, header, store_id, start, end)
    if report_type == "occupancy":
        return _occupancy_report(session, header, store_id, start, end)
    if report_type == "zones":
        return _zones_report(session, header, store_id, start, end)
    if report_type == "dwell":
        return _dwell_report(session, header, store_id, start, end)
    if report_type == "queues":
        return _queues_report(session, header, store_id, start, end)
    raise ApiError(400, "invalid_report_type", f"Unknown report type: {report_type}")


def _traffic_report(
    session: Session,
    header: ReportHeader,
    store_id: str,
    start: datetime,
    end: datetime,
) -> ReportPayload:
    rows = session.exec(
        select(VisitorMetric)
        .where(
            VisitorMetric.store_id == store_id,
            VisitorMetric.metric_date >= start.date(),
            VisitorMetric.metric_date <= end.date(),
        )
        .order_by(VisitorMetric.metric_date, VisitorMetric.hour)
    ).all()
    total_entries = sum(r.entries for r in rows)
    total_exits = sum(r.exits for r in rows)
    kpis = [
        ReportKpi(key="total_entries", label="Total entries", value=total_entries),
        ReportKpi(key="total_exits", label="Total exits", value=total_exits),
        ReportKpi(key="net_traffic", label="Net traffic", value=total_entries - total_exits),
    ]
    series = [
        ReportSeries(
            name="entries",
            points=[{"date": r.metric_date.isoformat(), "hour": r.hour, "value": r.entries} for r in rows],
        ),
        ReportSeries(
            name="exits",
            points=[{"date": r.metric_date.isoformat(), "hour": r.hour, "value": r.exits} for r in rows],
        ),
    ]
    table = [
        ReportRow(
            columns={
                "date": r.metric_date.isoformat(),
                "hour": r.hour,
                "entries": r.entries,
                "exits": r.exits,
            }
        )
        for r in rows
    ]
    return ReportPayload(header=header, kpis=kpis, series=series, table=table)


def _occupancy_report(
    session: Session,
    header: ReportHeader,
    store_id: str,
    start: datetime,
    end: datetime,
) -> ReportPayload:
    rows = session.exec(
        select(OccupancyMetric)
        .where(
            OccupancyMetric.store_id == store_id,
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
    ]
    series = [
        ReportSeries(
            name="occupancy",
            points=[{"timestamp": r.timestamp.isoformat(), "value": r.current_occupancy} for r in rows],
        )
    ]
    table = [
        ReportRow(columns={"timestamp": r.timestamp.isoformat(), "occupancy": r.current_occupancy})
        for r in rows
    ]
    return ReportPayload(header=header, kpis=kpis, series=series, table=table)


def _store_zone_ids(session: Session, store_id: str) -> list[str]:
    camera_ids = session.exec(select(Camera.id).where(Camera.store_id == store_id)).all()
    if not camera_ids:
        return []
    zones = session.exec(select(Zone.id).where(col(Zone.camera_id).in_(camera_ids))).all()
    return list(zones)


def _zones_report(
    session: Session,
    header: ReportHeader,
    store_id: str,
    start: datetime,
    end: datetime,
) -> ReportPayload:
    zone_ids = _store_zone_ids(session, store_id)
    if not zone_ids:
        return ReportPayload(header=header, kpis=[], series=[], table=[])

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
        ReportKpi(key="zone_count", label="Zones in scope", value=len(zone_ids)),
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
    return ReportPayload(header=header, kpis=kpis, series=series, table=table)


def _dwell_report(
    session: Session,
    header: ReportHeader,
    store_id: str,
    start: datetime,
    end: datetime,
) -> ReportPayload:
    zone_ids = _store_zone_ids(session, store_id)
    if not zone_ids:
        return ReportPayload(header=header, kpis=[], series=[], table=[])

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
    return ReportPayload(header=header, kpis=kpis, series=series, table=table)


def _queues_report(
    session: Session,
    header: ReportHeader,
    store_id: str,
    start: datetime,
    end: datetime,
) -> ReportPayload:
    zone_ids = _store_zone_ids(session, store_id)
    if not zone_ids:
        return ReportPayload(header=header, kpis=[], series=[], table=[])

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
    return ReportPayload(header=header, kpis=kpis, series=series, table=table)


def report_to_csv(payload: ReportPayload) -> str:
    import csv
    import io

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["report_type", payload.header.report_type])
    writer.writerow(["store_id", payload.header.store_id])
    writer.writerow(["from", payload.header.from_])
    writer.writerow(["to", payload.header.to])
    writer.writerow(["generated_at", payload.header.generated_at])
    writer.writerow([])
    writer.writerow(["KPI", "Label", "Value"])
    for kpi in payload.kpis:
        writer.writerow([kpi.key, kpi.label, kpi.value])
    writer.writerow([])
    if payload.table:
        columns = list(payload.table[0].columns.keys())
        writer.writerow(columns)
        for row in payload.table:
            writer.writerow([row.columns.get(c) for c in columns])
    return buffer.getvalue()


def report_to_pdf(payload: ReportPayload) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 8, f"Report: {payload.header.report_type}", ln=True)
    pdf.cell(0, 8, f"Store: {payload.header.store_id}", ln=True)
    pdf.cell(0, 8, f"Range: {payload.header.from_} to {payload.header.to}", ln=True)
    pdf.cell(0, 8, f"Generated: {payload.header.generated_at}", ln=True)
    pdf.ln(4)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 8, "KPIs", ln=True)
    pdf.set_font("Helvetica", size=10)
    for kpi in payload.kpis:
        pdf.cell(0, 6, f"{kpi.label}: {kpi.value}", ln=True)
    pdf.ln(4)
    if payload.table:
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.cell(0, 8, "Table", ln=True)
        pdf.set_font("Helvetica", size=9)
        for row in payload.table[:40]:
            parts = [f"{key}={value}" for key, value in row.columns.items()]
            line = ", ".join(parts)
            if len(line) > 100:
                line = line[:97] + "..."
            pdf.cell(0, 5, line, ln=True)
    return bytes(pdf.output())
