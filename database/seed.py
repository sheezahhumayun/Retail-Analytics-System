"""Seed reference org/store/camera/zone data for local development."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from sqlmodel import Session, select

from .models import (
    Camera,
    CountingLine,
    Organization,
    Store,
    User,
    VisitorMetric,
    Zone,
    ZoneMetric,
    ZoneShape,
)
from .session import session_scope

REPO_ROOT = Path(__file__).resolve().parent.parent

ORG_ID = "org_demo"
STORE_ID = "store_main"
USER_ID = "user_admin"
USER_REGULAR_ID = "user_demo"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def seed_reference_data(*, force: bool = False) -> None:
    """Insert demo org hierarchy and configs matching sample videos."""
    with session_scope() as session:
        if not force and session.get(Organization, ORG_ID) is not None:
            return
        _seed_core(session)
        _seed_cameras_and_zones(session)
        _seed_zone_shapes(session)
        _seed_historical_metrics(session)
        session.commit()


def _seed_core(session: Session) -> None:
    session.merge(Organization(id=ORG_ID, name="Demo Retail Co"))
    session.merge(
        Store(
            id=STORE_ID,
            org_id=ORG_ID,
            name="Main Street Store",
            address="100 Main St, Demo City",
        )
    )
    session.merge(
        User(
            id=USER_ID,
            org_id=ORG_ID,
            name="Admin User",
            email="admin@demo-retail.local",
            role="admin",
        )
    )
    session.merge(
        User(
            id=USER_REGULAR_ID,
            org_id=ORG_ID,
            name="Regular User",
            email="user@demo-retail.local",
            role="user",
        )
    )


def _seed_cameras_and_zones(session: Session) -> None:
    cameras = [
        Camera(
            id="entrance",
            store_id=STORE_ID,
            name="Entrance Camera",
            location="Front door",
            rtsp_url="sample-data/entrance.mp4",
            camera_type="fixed",
            resolution="640x360",
            fps=10.0,
            status="online",
        ),
        Camera(
            id="town",
            store_id=STORE_ID,
            name="Town Floor Camera",
            location="Open mall view",
            rtsp_url="sample-data/town.mp4",
            camera_type="fixed",
            resolution="640x360",
            fps=10.0,
            status="online",
        ),
        Camera(
            id="shop",
            store_id=STORE_ID,
            name="Shop Floor Camera",
            location="Interior aisle",
            rtsp_url="sample-data/shop.mp4",
            camera_type="fixed",
            resolution="640x360",
            fps=10.0,
            status="online",
        ),
    ]
    for cam in cameras:
        session.merge(cam)

    line_path = REPO_ROOT / "tests" / "videos" / "entrance_line.json"
    if line_path.is_file():
        line = _load_json(line_path)
        session.merge(
            CountingLine(
                id="line_entrance_main",
                camera_id=line.get("camera_id", "entrance"),
                name="main_entrance",
                point_a={"x": line["x1"], "y": line["y1"]},
                point_b={"x": line["x2"], "y": line["y2"]},
                direction="left_is_inside",
                created_at=datetime.now(timezone.utc),
            )
        )

    zone_config_path = REPO_ROOT / "tests" / "videos" / "town_zones.json"
    if zone_config_path.is_file():
        config = _load_json(zone_config_path)
        for z in config.get("zones", []):
            session.merge(
                Zone(
                    id=z["zone_id"],
                    camera_id=z.get("camera_id", config.get("camera_id", "town")),
                    name=z.get("zone_name", z["zone_id"]),
                    polygon_coords=z["polygon_coordinates"],
                    zone_type=z.get("zone_type", "general"),
                    analytics_enabled=z.get("analytics_enabled", True),
                )
            )

    shop_zones_path = REPO_ROOT / "tests" / "videos" / "shop_zones.json"
    if shop_zones_path.is_file():
        config = _load_json(shop_zones_path)
        for z in config.get("zones", []):
            session.merge(
                Zone(
                    id=z["zone_id"],
                    camera_id=z.get("camera_id", config.get("camera_id", "shop")),
                    name=z.get("zone_name", z["zone_id"]),
                    polygon_coords=z["polygon_coordinates"],
                    zone_type=z.get("zone_type", "general"),
                    analytics_enabled=z.get("analytics_enabled", True),
                )
            )


def _map_zone_shape_type(zone_type: str) -> str:
    if zone_type in ("queue", "checkout", "waiting"):
        return "checkout_queue"
    if zone_type == "entrance":
        return "entrance"
    return "general"


def _seed_zone_shapes(session: Session) -> None:
    for path, default_camera in (
        (REPO_ROOT / "tests" / "videos" / "town_zones.json", "town"),
        (REPO_ROOT / "tests" / "videos" / "shop_zones.json", "shop"),
    ):
        if not path.is_file():
            continue
        config = _load_json(path)
        for z in config.get("zones", []):
            session.merge(
                ZoneShape(
                    id=z["zone_id"],
                    camera_id=z.get("camera_id", config.get("camera_id", default_camera)),
                    name=z.get("zone_name", z["zone_id"]),
                    shape_type=_map_zone_shape_type(z.get("zone_type", "general")),
                    polygon_points=z["polygon_coordinates"],
                    created_at=datetime.now(timezone.utc),
                )
            )


def _seed_historical_metrics(session: Session) -> None:
    """Yesterday's hourly visitor traffic for dashboard query smoke tests."""
    today = datetime.now(timezone.utc).date()
    yesterday = today.fromordinal(today.toordinal() - 1)
    hourly_entries = [2, 1, 0, 0, 1, 3, 8, 15, 22, 28, 35, 42, 38, 30, 25, 20, 18, 24, 30, 22, 15, 10, 6, 3]
    for hour, entries in enumerate(hourly_entries):
        existing = session.exec(
            select(VisitorMetric).where(
                VisitorMetric.store_id == STORE_ID,
                VisitorMetric.metric_date == yesterday,
                VisitorMetric.hour == hour,
            )
        ).first()
        exits = max(0, entries - (2 if 9 <= hour <= 18 else 0))
        if existing is None:
            session.add(
                VisitorMetric(
                    store_id=STORE_ID,
                    metric_date=yesterday,
                    hour=hour,
                    entries=entries,
                    exits=exits,
                )
            )
        else:
            existing.entries = entries
            existing.exits = exits
            session.add(existing)

    # Zone metrics for store1 yesterday noon hour
    existing = session.exec(
        select(ZoneMetric).where(
            ZoneMetric.zone_id == "store1",
            ZoneMetric.metric_date == yesterday,
            ZoneMetric.hour == 12,
        )
    ).first()
    if existing is None:
        session.add(
            ZoneMetric(
                zone_id="store1",
                metric_date=yesterday,
                hour=12,
                visitors=18,
                avg_dwell=48.5,
                max_dwell=120.0,
                min_dwell=12.0,
                dwell_count=10,
            )
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the retail analytics database.")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Wipe all rows and load the multi-month demo dataset (destructive).",
    )
    args = parser.parse_args()
    if args.demo:
        from .seed_demo import seed_demo_data

        seed_demo_data()
    else:
        seed_reference_data(force=True)
        print("Minimal seed data applied (test fixture).")
