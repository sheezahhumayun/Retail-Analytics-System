"""Verify heatmap floor zone mapping uses real camera zones (not placeholders)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import requests
from sqlmodel import select

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.app.auth import create_access_token
from database.models import User
from database.session import session_scope

API = "http://127.0.0.1:8000/api"
PLACEHOLDER_LABELS = {"Entrance", "Checkout", "Electronics", "Apparel", "Back Wall"}


def token_for(org_id: str) -> str:
    with session_scope() as session:
        users = session.exec(
            select(User).where(User.org_id == org_id, User.role == "admin")
        ).all()
        user = next((u for u in users if u.status == "active"), None)
        if user is None:
            user = users[0] if users else None
        if user is None:
            raise RuntimeError(f"No admin user for org {org_id}")
        token, _ = create_access_token(user)
        return token


def normalize_polygon_points(points: list, width: int, height: int) -> list[dict[str, float]]:
    normalized: list[dict[str, float]] = []
    for point in points:
        x, y = point[0], point[1]
        normalized.append(
            {
                "x": round(max(0.0, min(100.0, (x / width) * 100)), 2),
                "y": round(max(0.0, min(100.0, (y / height) * 100)), 2),
            }
        )
    return normalized


def floor_zones_for(
    camera_id: str,
    org_id: str,
    date: str = "2026-08-11",
) -> dict:
    token = token_for(org_id)
    headers = {"Authorization": f"Bearer {token}"}
    zones = requests.get(
        f"{API}/zones",
        headers=headers,
        params={"camera_id": camera_id},
        timeout=30,
    ).json()
    heat_resp = requests.get(
        f"{API}/analytics/heatmap",
        headers=headers,
        params={
            "camera_id": camera_id,
            "date": date,
            "from_time": "09:00",
            "to_time": "18:00",
        },
        timeout=30,
    )
    result = {
        "camera_id": camera_id,
        "org_id": org_id,
        "heatmap_status": heat_resp.status_code,
        "zone_api_names": [z["name"] for z in zones],
        "floor_zones": [],
        "contains_placeholder_labels": False,
    }
    if heat_resp.status_code != 200:
        result["heatmap_error"] = heat_resp.text[:500]
        return result

    heat = heat_resp.json()
    width = heat["spec"]["width"]
    height = heat["spec"]["height"]
    floor: list[dict] = []
    for zone in zones:
        if zone.get("status") == "disabled":
            continue
        points = normalize_polygon_points(zone["polygon_points"], width, height)
        if len(points) >= 3:
            floor.append({"id": zone["id"], "label": zone["name"], "points": points})
    result["floor_zones"] = floor
    result["contains_placeholder_labels"] = any(
        zone["label"] in PLACEHOLDER_LABELS for zone in floor
    )
    return result


def main() -> int:
    outside = floor_zones_for("cam_outside_cam_00a514", "wetrades")
    print("=== cam_outside_cam_00a514 (wetrades) ===")
    print(json.dumps(outside, indent=2))

    empty = floor_zones_for("entrance", "org_demo", date="2026-08-06")
    print("=== no-zone camera entrance (org_demo) ===")
    print(json.dumps(empty, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
