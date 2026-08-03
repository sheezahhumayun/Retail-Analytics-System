"""Destructive demo seed — multi-month realistic analytics dataset for dashboard dev.

Wipes all application rows (schema/migrations untouched) and reloads org hierarchy,
cameras/zones/lines, users, and ~3 months of hourly metrics. Idempotent: every run
truncates first, then inserts the same deterministic dataset (fixed RNG seed).

Minimal test fixture seed remains ``database.seed.seed_reference_data`` (no ``--demo``).
"""

from __future__ import annotations

import json
import random
import shutil
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator

import numpy as np
from sqlalchemy import text
from sqlmodel import Session

from .models import (
    Alert,
    Camera,
    CountingLine,
    DwellEventRow,
    Event,
    OccupancyMetric,
    Organization,
    QueueMetric,
    Store,
    User,
    VisitorMetric,
    Zone,
    ZoneMetric,
    ZoneShape,
)
from .session import session_scope

RNG = random.Random(42)
REPO_ROOT = Path(__file__).resolve().parent.parent
HEATMAP_ROOT = REPO_ROOT / "data" / "heatmaps"

# Matches Module 8 HeatmapFrameSpec defaults (640x360 @ grid_scale=4 → 160×90 grids).
HEATMAP_WIDTH = 640
HEATMAP_HEIGHT = 360
HEATMAP_GRID_SCALE = 4
HEATMAP_GRID_W = HEATMAP_WIDTH // HEATMAP_GRID_SCALE
HEATMAP_GRID_H = HEATMAP_HEIGHT // HEATMAP_GRID_SCALE

ORG_ID = "org_demo"

# Daily traffic shape (same curve as minimal seed / traffic.csv sample): overnight low,
# morning ramp, lunch + evening peaks.
HOURLY_SHAPE = [
    2, 1, 0, 0, 1, 3, 8, 15, 22, 28, 35, 42, 38, 30, 25, 20, 18, 24, 30, 22, 15, 10, 6, 3,
]

# Anomaly days (month, day) -> multiplier applied on top of other factors.
ANOMALY_DAYS: dict[tuple[int, int], float] = {
    (5, 12): 0.55,   # noticeably slow Tuesday in May
    (6, 3): 0.70,    # mid-week dip in June
    (7, 4): 1.65,    # busy holiday weekend (US Independence Day)
    (7, 18): 1.45,   # summer promo weekend
    (8, 1): 1.35,    # month-start rush
}

BATCH_SIZE = 5_000


@dataclass(frozen=True)
class DemoDateRange:
    start: date
    end: date

    @property
    def label(self) -> str:
        return f"{self.start.isoformat()} through {self.end.isoformat()} (inclusive)"


@dataclass(frozen=True)
class StoreSpec:
    id: str
    name: str
    address: str
    scale: float


@dataclass(frozen=True)
class CameraSpec:
    id: str
    store_id: str
    name: str
    location: str
    rtsp_url: str
    source_type: str


@dataclass(frozen=True)
class ZoneSpec:
    id: str
    camera_id: str
    name: str
    polygon: list[list[float]]
    zone_type: str


@dataclass(frozen=True)
class LineSpec:
    id: str
    camera_id: str
    name: str
    point_a: dict[str, float]
    point_b: dict[str, float]
    direction: str


STORES: tuple[StoreSpec, ...] = (
    StoreSpec("store_main", "Downtown Flagship", "100 Main St, Demo City", 1.0),
    StoreSpec("store_west", "Westside Mall", "450 West Ave, Demo City", 0.78),
    StoreSpec("store_east", "East Market", "88 East Blvd, Demo City", 0.88),
)

CAMERAS: tuple[CameraSpec, ...] = (
    CameraSpec(
        "entrance",
        "store_main",
        "Main Entrance",
        "Front door counting line",
        "sample-data/entrance.mp4",
        "live",
    ),
    CameraSpec(
        "shop",
        "store_main",
        "Shop Floor",
        "Interior aisles",
        "sample-data/shop.mp4",
        "recorded",
    ),
    CameraSpec(
        "checkout_cam",
        "store_main",
        "Checkout Overhead",
        "Registers 1-4",
        "rtsp://demo.local/checkout",
        "live",
    ),
    CameraSpec(
        "west_entrance",
        "store_west",
        "West Mall Entrance",
        "Mall atrium entry",
        "rtsp://demo.local/west-entrance",
        "live",
    ),
    CameraSpec(
        "west_floor",
        "store_west",
        "West Sales Floor",
        "Aisle overview",
        "sample-data/store-floor.mp4",
        "recorded",
    ),
    CameraSpec(
        "east_entrance",
        "store_east",
        "East Street Entrance",
        "Street-facing doors",
        "rtsp://demo.local/east-entrance",
        "live",
    ),
    CameraSpec(
        "east_checkout",
        "store_east",
        "East Checkout",
        "Self-checkout lane",
        "rtsp://demo.local/east-checkout",
        "live",
    ),
    CameraSpec(
        "town",
        "store_east",
        "Open Mall View",
        "Shared concourse",
        "sample-data/town.mp4",
        "recorded",
    ),
)

ZONES: tuple[ZoneSpec, ...] = (
    ZoneSpec(
        "floor_main",
        "shop",
        "Main Floor",
        [
            [252.0, 196.0],
            [103.0, 324.0],
            [91.0, 107.0],
            [150.0, 70.0],
            [175.0, 114.0],
            [192.0, 105.0],
            [203.0, 132.0],
            [254.0, 195.0],
        ],
        "general",
    ),
    ZoneSpec(
        "queue_lane",
        "shop",
        "Checkout Queue",
        [[267.0, 227.0], [228.0, 253.0], [293.0, 353.0], [374.0, 348.0]],
        "queue",
    ),
    ZoneSpec(
        "west_entrance_zone",
        "west_entrance",
        "West Entrance Funnel",
        [[40.0, 120.0], [180.0, 120.0], [200.0, 300.0], [20.0, 300.0]],
        "entrance",
    ),
    ZoneSpec(
        "west_aisle",
        "west_floor",
        "West Aisle",
        [[60.0, 80.0], [520.0, 80.0], [520.0, 320.0], [60.0, 320.0]],
        "general",
    ),
    ZoneSpec(
        "east_checkout_queue",
        "east_checkout",
        "East Checkout Queue",
        [[300.0, 180.0], [420.0, 180.0], [420.0, 340.0], [300.0, 340.0]],
        "queue",
    ),
    ZoneSpec(
        "store1",
        "town",
        "Concourse Store A",
        [[1.0, 179.0], [1.0, 220.0], [75.0, 238.0], [224.0, 146.0], [147.0, 112.0]],
        "general",
    ),
    ZoneSpec(
        "store2",
        "town",
        "Concourse Store B",
        [[185.0, 91.0], [269.0, 120.0], [363.0, 72.0], [262.0, 58.0]],
        "general",
    ),
)

LINES: tuple[LineSpec, ...] = (
    LineSpec(
        "line_entrance_main",
        "entrance",
        "main_entrance",
        {"x": 191.0, "y": 275.0},
        {"x": 323.0, "y": 332.0},
        "right_is_inside",
    ),
    LineSpec(
        "line_west_entrance",
        "west_entrance",
        "west_door",
        {"x": 120.0, "y": 280.0},
        {"x": 280.0, "y": 280.0},
        "left_is_inside",
    ),
    LineSpec(
        "line_east_entrance",
        "east_entrance",
        "east_door",
        {"x": 100.0, "y": 300.0},
        {"x": 260.0, "y": 300.0},
        "right_is_inside",
    ),
)

USERS: tuple[tuple[str, str, str, str, str, str | None], ...] = (
    ("user_admin", ORG_ID, "Admin User", "admin@demo-retail.local", "admin", None),
    ("user_demo", ORG_ID, "Store Manager", "user@demo-retail.local", "user", "store_main"),
    (
        "user_analyst",
        ORG_ID,
        "Retail Analyst",
        "analyst@demo-retail.local",
        "user",
        "store_east",
    ),
)

QUEUE_ZONE_IDS = frozenset({"queue_lane", "east_checkout_queue"})

ZONE_TRAFFIC_SHARE: dict[str, float] = {
    "floor_main": 0.42,
    "queue_lane": 0.12,
    "west_entrance_zone": 0.35,
    "west_aisle": 0.55,
    "east_checkout_queue": 0.15,
    "store1": 0.38,
    "store2": 0.34,
}


def compute_demo_date_range(*, today: date | None = None) -> DemoDateRange:
    """Three full calendar months before the current month, through today."""
    today = today or datetime.now(timezone.utc).date()
    first_of_month = today.replace(day=1)
    month = first_of_month.month - 3
    year = first_of_month.year
    while month <= 0:
        month += 12
        year -= 1
    return DemoDateRange(start=date(year, month, 1), end=today)


def _iter_dates(start: date, end: date) -> Iterator[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def _month_trend_factor(d: date) -> float:
    """Gradual growth May → August so month-over-month charts diverge."""
    month_offsets = {5: 0.92, 6: 1.0, 7: 1.06, 8: 1.10}
    base = month_offsets.get(d.month, 1.0)
    # Gentle intra-month ramp (early month slightly softer).
    return base * (0.97 + 0.06 * (d.day / 31.0))


def _weekday_factor(d: date) -> float:
    wd = d.weekday()  # Mon=0
    if wd >= 5:
        return 1.22  # weekends busier for this retail profile
    factors = {0: 0.88, 1: 0.92, 2: 0.96, 3: 1.0, 4: 1.08}
    return factors[wd]


def _hourly_entries_for_store(store: StoreSpec, d: date, hour: int) -> int:
    base = HOURLY_SHAPE[hour]
    if base == 0 and hour < 6:
        return 0
    factor = (
        store.scale
        * _weekday_factor(d)
        * _month_trend_factor(d)
        * ANOMALY_DAYS.get((d.month, d.day), 1.0)
        * RNG.uniform(0.86, 1.14)
    )
    return max(0, int(round(base * factor)))


def _map_zone_shape_type(zone_type: str) -> str:
    if zone_type in ("queue", "checkout", "waiting"):
        return "checkout_queue"
    if zone_type == "entrance":
        return "entrance"
    return "general"


def truncate_all_tables(session: Session) -> None:
    """Delete all application data in FK-safe order (schema preserved)."""
    session.execute(
        text(
            """
            TRUNCATE TABLE
                alerts,
                events,
                dwell_events,
                queue_metrics,
                zone_metrics,
                visitor_metrics,
                occupancy_metrics,
                tracks,
                counting_lines,
                zone_shapes,
                zones,
                cameras,
                users,
                stores,
                organizations
            RESTART IDENTITY CASCADE
            """
        )
    )


def _seed_reference_entities(session: Session, created_at: datetime) -> DemoDateRange:
    date_range = compute_demo_date_range()

    session.add(Organization(id=ORG_ID, name="Northwind Retail Group"))
    for store in STORES:
        session.add(
            Store(
                id=store.id,
                org_id=ORG_ID,
                name=store.name,
                address=store.address,
            )
        )
    session.flush()

    for user_id, org_id, name, email, role, store_id in USERS:
        session.add(
            User(
                id=user_id,
                org_id=org_id,
                name=name,
                email=email,
                role=role,
                store_id=store_id,
            )
        )
    session.flush()

    for cam in CAMERAS:
        session.add(
            Camera(
                id=cam.id,
                store_id=cam.store_id,
                name=cam.name,
                location=cam.location,
                rtsp_url=cam.rtsp_url,
                source_type=cam.source_type,
                camera_type="fixed",
                resolution="640x360",
                fps=10.0,
                status="online",
            )
        )
    session.flush()

    for zone in ZONES:
        session.add(
            Zone(
                id=zone.id,
                camera_id=zone.camera_id,
                name=zone.name,
                polygon_coords=zone.polygon,
                zone_type=zone.zone_type,
                analytics_enabled=True,
            )
        )
        session.add(
            ZoneShape(
                id=zone.id,
                camera_id=zone.camera_id,
                name=zone.name,
                shape_type=_map_zone_shape_type(zone.zone_type),
                polygon_points=zone.polygon,
                created_at=created_at,
            )
        )
    session.flush()

    for line in LINES:
        session.add(
            CountingLine(
                id=line.id,
                camera_id=line.camera_id,
                name=line.name,
                point_a=line.point_a,
                point_b=line.point_b,
                direction=line.direction,
                created_at=created_at,
            )
        )

    return date_range


def _bulk_insert(session: Session, model: type, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    for offset in range(0, len(rows), BATCH_SIZE):
        session.bulk_insert_mappings(model, rows[offset : offset + BATCH_SIZE])


def _generate_visitor_metrics(date_range: DemoDateRange) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for store in STORES:
        for d in _iter_dates(date_range.start, date_range.end):
            for hour in range(24):
                entries = _hourly_entries_for_store(store, d, hour)
                exits = max(0, entries - (2 if 9 <= hour <= 20 else 0))
                rows.append(
                    {
                        "store_id": store.id,
                        "metric_date": d,
                        "hour": hour,
                        "entries": entries,
                        "exits": exits,
                    }
                )
    return rows


def _generate_occupancy_metrics(
    date_range: DemoDateRange,
    visitor_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    by_store_day: dict[tuple[str, date], list[tuple[int, int, int]]] = {}
    for row in visitor_rows:
        key = (row["store_id"], row["metric_date"])
        by_store_day.setdefault(key, []).append((row["hour"], row["entries"], row["exits"]))

    store_cameras = {s.id: [c.id for c in CAMERAS if c.store_id == s.id] for s in STORES}

    for (store_id, d), hours in by_store_day.items():
        hours_sorted = sorted(hours, key=lambda item: item[0])
        occupancy = 0
        for hour, entries, exits in hours_sorted:
            occupancy = max(0, occupancy + entries - exits)
            ts = datetime(d.year, d.month, d.day, hour, 59, 0, tzinfo=timezone.utc)
            rows.append(
                {
                    "store_id": store_id,
                    "camera_id": None,
                    "timestamp": ts,
                    "current_occupancy": occupancy,
                }
            )
            for camera_id in store_cameras[store_id]:
                cam_occ = max(0, int(round(occupancy / max(1, len(store_cameras[store_id])))))
                rows.append(
                    {
                        "store_id": None,
                        "camera_id": camera_id,
                        "timestamp": ts,
                        "current_occupancy": cam_occ,
                    }
                )
    return rows


def _generate_zone_metrics(
    date_range: DemoDateRange,
    visitor_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    store_hour_entries: dict[tuple[str, date, int], int] = {}
    for row in visitor_rows:
        store_hour_entries[(row["store_id"], row["metric_date"], row["hour"])] = row["entries"]

    camera_store = {c.id: c.store_id for c in CAMERAS}
    zone_store = {z.id: camera_store[z.camera_id] for z in ZONES}

    for zone in ZONES:
        share = ZONE_TRAFFIC_SHARE[zone.id]
        is_queue = zone.id in QUEUE_ZONE_IDS
        for d in _iter_dates(date_range.start, date_range.end):
            for hour in range(24):
                store_entries = store_hour_entries.get((zone_store[zone.id], d, hour), 0)
                visitors = max(0, int(round(store_entries * share * RNG.uniform(0.9, 1.1))))
                if visitors == 0:
                    continue
                if is_queue:
                    avg_dwell = RNG.uniform(120.0, 360.0)
                elif zone.zone_type == "entrance":
                    avg_dwell = RNG.uniform(30.0, 90.0)
                else:
                    avg_dwell = RNG.uniform(180.0, 720.0)
                dwell_count = max(1, int(round(visitors * RNG.uniform(0.55, 0.85))))
                max_dwell = avg_dwell * RNG.uniform(1.4, 2.2)
                min_dwell = max(15.0, avg_dwell * RNG.uniform(0.25, 0.55))
                rows.append(
                    {
                        "zone_id": zone.id,
                        "metric_date": d,
                        "hour": hour,
                        "visitors": visitors,
                        "avg_dwell": round(avg_dwell, 1),
                        "max_dwell": round(max_dwell, 1),
                        "min_dwell": round(min_dwell, 1),
                        "dwell_count": dwell_count,
                    }
                )
    return rows


def _generate_dwell_events(
    date_range: DemoDateRange,
    zone_metric_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    track_counter = 0
    for zm in zone_metric_rows:
        if zm["dwell_count"] <= 0:
            continue
        zone_id = zm["zone_id"]
        is_queue = zone_id in QUEUE_ZONE_IDS
        d: date = zm["metric_date"]
        hour: int = zm["hour"]
        for _ in range(zm["dwell_count"]):
            track_counter += 1
            if is_queue:
                dwell_seconds = RNG.uniform(90.0, 420.0)
            else:
                dwell_seconds = RNG.uniform(60.0, 1_800.0)
            minute_offset = RNG.randint(0, 50)
            enter_ts = datetime(
                d.year,
                d.month,
                d.day,
                hour,
                min(59, minute_offset),
                RNG.randint(0, 59),
                tzinfo=timezone.utc,
            )
            exit_ts = enter_ts + timedelta(seconds=dwell_seconds)
            rows.append(
                {
                    "zone_id": zone_id,
                    "track_id": f"t{track_counter:06d}",
                    "enter_ts": enter_ts,
                    "exit_ts": exit_ts,
                    "dwell_seconds": round(dwell_seconds, 1),
                }
            )
    return rows


def _generate_queue_metrics(zone_metric_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for zm in zone_metric_rows:
        if zm["zone_id"] not in QUEUE_ZONE_IDS:
            continue
        if zm["hour"] < 9 or zm["hour"] > 21:
            continue
        d: date = zm["metric_date"]
        hour: int = zm["hour"]
        peak_factor = 1.0 + max(0.0, (zm["hour"] - 11) / 8.0) * 0.6
        queue_length = max(0, int(round(zm["visitors"] * 0.35 * peak_factor)))
        if queue_length == 0:
            continue
        estimated_wait = round(min(18.0, 1.5 + queue_length * RNG.uniform(0.8, 1.6)), 1)
        ts = datetime(d.year, d.month, d.day, hour, 30, 0, tzinfo=timezone.utc)
        rows.append(
            {
                "zone_id": zm["zone_id"],
                "timestamp": ts,
                "queue_length": queue_length,
                "estimated_wait": estimated_wait,
            }
        )
    return rows


def _generate_events_and_alerts(
    date_range: DemoDateRange,
    visitor_rows: list[dict[str, Any]],
    zone_metric_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []
    alerts: list[dict[str, Any]] = []

    store_entrance_camera = {
        "store_main": "entrance",
        "store_west": "west_entrance",
        "store_east": "east_entrance",
    }
    zone_camera = {z.id: z.camera_id for z in ZONES}

    event_id = 0
    for row in visitor_rows:
        if row["entries"] == 0:
            continue
        d: date = row["metric_date"]
        hour: int = row["hour"]
        camera_id = store_entrance_camera[row["store_id"]]
        sample_count = max(1, row["entries"] // 12)
        for _ in range(sample_count):
            event_id += 1
            ts = datetime(
                d.year,
                d.month,
                d.day,
                hour,
                RNG.randint(0, 59),
                RNG.randint(0, 59),
                tzinfo=timezone.utc,
            )
            events.append(
                {
                    "camera_id": camera_id,
                    "zone_id": None,
                    "track_id": f"e{event_id:07d}",
                    "event_type": "ENTRY",
                    "timestamp": ts,
                    "metadata_": {"source": "demo_seed"},
                }
            )

    for zm in zone_metric_rows:
        if zm["visitors"] < 3:
            continue
        d = zm["metric_date"]
        hour = zm["hour"]
        zone_id = zm["zone_id"]
        camera_id = zone_camera[zone_id]
        ts = datetime(d.year, d.month, d.day, hour, 15, 0, tzinfo=timezone.utc)
        events.append(
            {
                "camera_id": camera_id,
                "zone_id": zone_id,
                "track_id": f"z{zone_id[:4]}{d.toordinal()}{hour}",
                "event_type": "ZONE_ENTER",
                "timestamp": ts,
                "metadata_": {"visitors": zm["visitors"]},
            }
        )

    alert_specs: list[tuple[str, str | None, str | None, str, str, dict[str, Any]]] = []
    for d in _iter_dates(date_range.start, date_range.end):
        if d.weekday() == 1 and d.day % 2 == 0:
            alert_specs.append(
                (
                    "QUEUE_THRESHOLD",
                    "shop",
                    "queue_lane",
                    "warning",
                    "open" if d > date_range.end - timedelta(days=7) else "resolved",
                    {"queue_length": 8, "threshold": 6},
                )
            )
        if d.weekday() == 4 and d.day % 3 == 0:
            alert_specs.append(
                (
                    "DWELL_THRESHOLD",
                    "town",
                    "store1",
                    "info",
                    "acknowledged" if d.month == 6 else "resolved",
                    {"dwell_seconds": 900, "threshold": 600},
                )
            )

    # Spread camera-offline alerts across the range.
    offline_days = [
        date_range.start + timedelta(days=12),
        date_range.start + timedelta(days=45),
        date_range.start + timedelta(days=78),
    ]
    for offline_day in offline_days:
        if offline_day > date_range.end:
            continue
        alert_specs.append(
            (
                "CAMERA_OFFLINE",
                "west_floor",
                None,
                "critical",
                "resolved",
                {"reason": "stream_timeout"},
            )
        )

    for idx, (alert_type, camera_id, zone_id, severity, status, meta) in enumerate(alert_specs):
        spread_day = date_range.start + timedelta(days=idx * 3)
        if spread_day > date_range.end:
            spread_day = date_range.end - timedelta(days=idx % 5)
        ts = datetime(
            spread_day.year,
            spread_day.month,
            spread_day.day,
            14,
            30,
            0,
            tzinfo=timezone.utc,
        )
        alerts.append(
            {
                "alert_type": alert_type,
                "camera_id": camera_id,
                "zone_id": zone_id,
                "timestamp": ts,
                "severity": severity,
                "status": status,
                "metadata_": meta,
            }
        )

    return events, alerts


def _polygon_centroid(polygon: list[list[float]]) -> tuple[float, float]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def _camera_hotspots(camera_id: str) -> list[tuple[float, float]]:
    """Concentrate synthetic density near zone / counting-line areas for a camera."""
    spots: list[tuple[float, float]] = []
    for zone in ZONES:
        if zone.camera_id == camera_id:
            spots.append(_polygon_centroid(zone.polygon))
    for line in LINES:
        if line.camera_id == camera_id:
            spots.append(
                (
                    (line.point_a["x"] + line.point_b["x"]) / 2.0,
                    (line.point_a["y"] + line.point_b["y"]) / 2.0,
                )
            )
    if not spots:
        # Default funnel + aisle for cameras without geometry (e.g. checkout_cam).
        spots = [(320.0, 280.0), (220.0, 200.0), (420.0, 200.0), (320.0, 140.0)]
    return spots


def _build_synthetic_hour_arrays(
    hotspots: list[tuple[float, float]],
    entries: int,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Build density/trajectory grids correlated with visitor entries (no frame loop)."""
    if entries <= 0:
        return None

    # Cap point count for speed; scale weights so busier hours stay denser.
    n_points = min(96, max(4, entries * 2))
    weight_scale = max(0.5, entries / n_points)
    density = np.zeros((HEATMAP_GRID_H, HEATMAP_GRID_W), dtype=np.float32)
    trajectory = np.zeros_like(density)
    scale = HEATMAP_GRID_SCALE
    gw, gh = HEATMAP_GRID_W, HEATMAP_GRID_H

    for _ in range(n_points):
        hx, hy = hotspots[RNG.randrange(len(hotspots))]
        x = hx + RNG.gauss(0.0, 28.0)
        y = hy + RNG.gauss(0.0, 22.0)
        gx = int(x / scale)
        gy = int(y / scale)
        if 0 <= gx < gw and 0 <= gy < gh:
            w = weight_scale * RNG.uniform(0.7, 1.3)
            density[gy, gx] += w
            # Soften into a 3x3 neighborhood so blobs read as heat, not single cells.
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    nx, ny = gx + dx, gy + dy
                    if 0 <= nx < gw and 0 <= ny < gh and (dx or dy):
                        density[ny, nx] += w * 0.25

    # Light aisle noise + faint trajectories between hotspots.
    bg = max(1, n_points // 6)
    for _ in range(bg):
        gx = RNG.randint(2, gw - 3)
        gy = RNG.randint(2, gh - 3)
        density[gy, gx] += weight_scale * 0.15

    if len(hotspots) >= 2:
        for _ in range(max(1, n_points // 10)):
            a = hotspots[RNG.randrange(len(hotspots))]
            b = hotspots[RNG.randrange(len(hotspots))]
            steps = 6
            for step in range(steps + 1):
                t = step / steps
                x = a[0] + (b[0] - a[0]) * t + RNG.gauss(0.0, 8.0)
                y = a[1] + (b[1] - a[1]) * t + RNG.gauss(0.0, 8.0)
                gx = int(x / scale)
                gy = int(y / scale)
                if 0 <= gx < gw and 0 <= gy < gh:
                    trajectory[gy, gx] += weight_scale * 0.4

    return density, trajectory


def _save_heatmap_npz(
    root: Path,
    *,
    camera_id: str,
    day: date,
    hour: int,
    density: np.ndarray,
    trajectory: np.ndarray,
) -> Path:
    """Write one hour bucket in the exact Module 8 ``HeatmapStore.save`` NPZ schema."""
    path = root / camera_id / day.isoformat() / f"{hour:02d}.npz"
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        path,
        density=density.astype(np.float32, copy=False),
        trajectory=trajectory.astype(np.float32, copy=False),
        spec_width=np.int32(HEATMAP_WIDTH),
        spec_height=np.int32(HEATMAP_HEIGHT),
        spec_grid_scale=np.int32(HEATMAP_GRID_SCALE),
        meta=json.dumps(
            {"camera_id": camera_id, "day": day.isoformat(), "hour": hour}
        ),
    )
    return path


def _reset_heatmap_root() -> None:
    """Wipe prior synthetic NPZ trees so re-seed is idempotent (schema untouched)."""
    if HEATMAP_ROOT.exists():
        # Windows can fail shutil.rmtree on deep trees; delete files first.
        for path in sorted(HEATMAP_ROOT.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink(missing_ok=True)
            elif path.is_dir():
                try:
                    path.rmdir()
                except OSError:
                    pass
        try:
            shutil.rmtree(HEATMAP_ROOT, ignore_errors=True)
        except OSError:
            pass
    HEATMAP_ROOT.mkdir(parents=True, exist_ok=True)


def _seed_heatmap_files(
    date_range: DemoDateRange,
    visitor_rows: list[dict[str, Any]],
) -> int:
    """Write Module 8 hour-bucket NPZ files for every seeded camera/date.

    Synthetic only — density is correlated with visitor_metrics entries and
    concentrated near zone/line hotspots. Not real inference output.
    Format matches ``analytics.heatmaps.storage.HeatmapStore.save`` exactly
    (density, trajectory, spec_*, meta) so GET /api/analytics/heatmap can read them.
    """
    _reset_heatmap_root()

    entries_by_store: dict[tuple[str, date, int], int] = {
        (row["store_id"], row["metric_date"], row["hour"]): row["entries"]
        for row in visitor_rows
    }
    camera_store = {c.id: c.store_id for c in CAMERAS}
    hotspots_by_camera = {c.id: _camera_hotspots(c.id) for c in CAMERAS}

    written = 0
    for cam in CAMERAS:
        hotspots = hotspots_by_camera[cam.id]
        store_id = camera_store[cam.id]
        for d in _iter_dates(date_range.start, date_range.end):
            for hour in range(24):
                entries = entries_by_store.get((store_id, d, hour), 0)
                # Share store traffic across cameras; keep floor cams denser than checkout.
                share = 0.55 if cam.source_type == "recorded" or "entrance" in cam.id else 0.35
                cam_entries = max(0, int(round(entries * share)))
                if cam_entries <= 0 and not (8 <= hour <= 21 and entries > 0):
                    continue
                if cam_entries <= 0:
                    cam_entries = max(1, entries // 4)
                arrays = _build_synthetic_hour_arrays(hotspots, cam_entries)
                if arrays is None:
                    continue
                density, trajectory = arrays
                _save_heatmap_npz(
                    HEATMAP_ROOT,
                    camera_id=cam.id,
                    day=d,
                    hour=hour,
                    density=density,
                    trajectory=trajectory,
                )
                written += 1
    return written


def seed_demo_data(*, database_url: str | None = None) -> DemoDateRange:
    """Wipe and reload the full demo dataset. Returns the seeded date range."""
    started = time.perf_counter()
    RNG.seed(42)
    created_at = datetime.now(timezone.utc)
    date_range = compute_demo_date_range()

    with session_scope(database_url=database_url) as session:
        truncate_all_tables(session)
        date_range = _seed_reference_entities(session, created_at)
        session.flush()

        visitor_rows = _generate_visitor_metrics(date_range)
        zone_metric_rows = _generate_zone_metrics(date_range, visitor_rows)
        occupancy_rows = _generate_occupancy_metrics(date_range, visitor_rows)
        dwell_rows = _generate_dwell_events(date_range, zone_metric_rows)
        queue_rows = _generate_queue_metrics(zone_metric_rows)
        event_rows, alert_rows = _generate_events_and_alerts(
            date_range, visitor_rows, zone_metric_rows
        )

        _bulk_insert(session, VisitorMetric, visitor_rows)
        _bulk_insert(session, ZoneMetric, zone_metric_rows)
        _bulk_insert(session, OccupancyMetric, occupancy_rows)
        _bulk_insert(session, DwellEventRow, dwell_rows)
        _bulk_insert(session, QueueMetric, queue_rows)
        _bulk_insert(session, Event, event_rows)
        _bulk_insert(session, Alert, alert_rows)

    heatmap_count = _seed_heatmap_files(date_range, visitor_rows)

    elapsed = time.perf_counter() - started
    print(
        f"Demo seed complete in {elapsed:.1f}s - {date_range.label}\n"
        f"  visitor_metrics: {len(visitor_rows):,}\n"
        f"  zone_metrics: {len(zone_metric_rows):,}\n"
        f"  occupancy_metrics: {len(occupancy_rows):,}\n"
        f"  dwell_events: {len(dwell_rows):,}\n"
        f"  queue_metrics: {len(queue_rows):,}\n"
        f"  events: {len(event_rows):,}\n"
        f"  alerts: {len(alert_rows):,}\n"
        f"  heatmap NPZ buckets (synthetic): {heatmap_count:,}\n"
        f"  heatmap root: {HEATMAP_ROOT}\n"
        f"  most recent heatmap date: {date_range.end.isoformat()}"
    )
    return date_range


if __name__ == "__main__":
    seed_demo_data()
