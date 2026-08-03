"""Process a recorded-video camera through the analytics pipeline."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sqlmodel import select

from analytics.counting import CountingLine, LineCounter
from analytics.events import AnalyticsEngine, AnalyticsEngineConfig, EventBus
from analytics.zones import Zone, ZoneDetector
from database import AnalyticsDbWriter, DbWriterConfig, session_scope
from database.models import Camera, CountingLine as DbCountingLine, Zone as DbZone
from inference.detection import create_detector
from inference.tracking import Tracker
from inference.video import create_video_source
from tests.scripts.demo_source import iter_frames, warmup_source


def _resolve_video_path(rtsp_url: str) -> Path:
    path = Path(rtsp_url)
    if path.is_file():
        return path
    candidate = REPO_ROOT / rtsp_url
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(f"Video file not found: {rtsp_url}")


def _zone_from_db(row: DbZone) -> Zone:
    return Zone.from_dict(
        {
            "zone_id": row.id,
            "zone_name": row.name,
            "camera_id": row.camera_id,
            "polygon_coordinates": row.polygon_coords,
            "zone_type": row.zone_type,
            "analytics_enabled": row.analytics_enabled,
        }
    )


def _line_from_db(row: DbCountingLine) -> CountingLine:
    inside_side = "left" if row.direction == "left_is_inside" else "right"
    return CountingLine.from_dict(
        {
            "x1": row.point_a["x"],
            "y1": row.point_a["y"],
            "x2": row.point_b["x"],
            "y2": row.point_b["y"],
            "inside_side": inside_side,
            "camera_id": row.camera_id,
            "name": row.name,
        }
    )


def process_recorded_camera(
    camera_id: str,
    *,
    backend: str = "ultralytics",
    target_fps: float = 10.0,
) -> dict[str, object]:
    """Run detect→track→analytics→DB for a recorded camera's video file."""
    with session_scope() as session:
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise ValueError(f"Camera '{camera_id}' not found")
        if camera.source_type != "recorded":
            raise ValueError(f"Camera '{camera_id}' is not a recorded-video source")
        if not camera.rtsp_url:
            raise ValueError(f"Camera '{camera_id}' has no video path configured")

        video_path = _resolve_video_path(camera.rtsp_url)
        store_id = camera.store_id

        db_zones = list(
            session.exec(select(DbZone).where(DbZone.camera_id == camera_id)).all()
        )
        zones = [_zone_from_db(z) for z in db_zones if z.analytics_enabled]

        db_line = session.exec(
            select(DbCountingLine).where(DbCountingLine.camera_id == camera_id)
        ).first()

    bus = EventBus()
    db_writer = AnalyticsDbWriter(
        DbWriterConfig(
            store_id=store_id,
            camera_store_map={camera_id: store_id},
            zones=zones,
        )
    )
    db_writer.subscribe(bus)

    engine = AnalyticsEngine(
        bus,
        AnalyticsEngineConfig(
            camera_ids=[camera_id],
            zones=zones,
            store_id=store_id,
            db_writer=db_writer,
        ),
    )

    counter = None
    if db_line is not None:
        line = _line_from_db(db_line)
        counter = LineCounter(line, event_bus=bus)

    zone_detector = ZoneDetector(zones) if zones else None
    tracker = Tracker(camera_id=camera_id, min_confirmation_frames=2)

    frames_processed = 0
    events_published = 0

    with create_detector(backend=backend) as detector:
        src = warmup_source(
            str(video_path),
            target_fps=target_fps,
            detector=detector,
            camera_id=camera_id,
        )
        try:
            for frame, ts in iter_frames(src, duration=None, preview=False):
                dets = detector.detect(frame, camera_id=camera_id, timestamp=ts)
                tracks = tracker.update(dets)
                if counter is not None:
                    counter.update(tracks)
                if zone_detector is not None:
                    for ze in zone_detector.update(tracks):
                        engine.process_zone_event(ze)
                engine.close_stale_dwell_sessions(ts)
                frames_processed += 1
        finally:
            src.release()

    events_published = len(bus.event_log)
    processed_at = datetime.now(timezone.utc)

    with session_scope() as session:
        camera = session.get(Camera, camera_id)
        if camera is not None:
            camera.last_processed_at = processed_at
            session.add(camera)
            session.commit()

    return {
        "camera_id": camera_id,
        "status": "completed",
        "frames_processed": frames_processed,
        "events_published": events_published,
        "processed_at": processed_at.isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Process a recorded camera video into analytics DB")
    parser.add_argument("--camera-id", required=True, help="Camera id (source_type=recorded)")
    parser.add_argument("--backend", choices=["ultralytics", "onnx"], default="ultralytics")
    parser.add_argument("--target-fps", type=float, default=10.0)
    args = parser.parse_args()

    try:
        result = process_recorded_camera(
            args.camera_id,
            backend=args.backend,
            target_fps=args.target_fps,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
