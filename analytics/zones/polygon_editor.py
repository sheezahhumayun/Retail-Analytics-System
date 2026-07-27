"""MVP polygon zone editor — click-to-define geometry in OpenCV.

Full admin UI for zone configuration is Module 16; this is enough for dev and
test against sample footage.

Usage
-----
PowerShell — single line (bash ``\\`` continuation does not work in PS)::

    python -m analytics.zones.polygon_editor sample-data/store-floor.mp4 --camera-id store-floor --zone-id electronics --zone-name Electronics --output tests/videos/store_floor_zones.json

Controls
--------
- Left-click: add polygon vertex.
- Right-click or ``c``: close polygon (needs ≥ 3 points).
- ``r``: reset clicks.
- ``s``: save JSON (requires closed polygon).
- ``q`` / ESC: quit (saves first if polygon is closed).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from inference.video import DEFAULT_LONG_SIDE, resize_long_side

from .types import Zone, ZoneConfig, ZoneType


def _draw_polygon(
    frame: np.ndarray,
    clicks: list[tuple[int, int]],
    *,
    closed: bool,
) -> None:
    if not clicks:
        return
    pts = np.array(clicks, dtype=np.int32)
    color_line = (0, 200, 255)
    color_fill = (0, 160, 0)
    if closed and len(clicks) >= 3:
        overlay = frame.copy()
        cv2.fillPoly(overlay, [pts], color_fill)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        cv2.polylines(frame, [pts], True, color_line, 2)
    else:
        for i in range(1, len(clicks)):
            cv2.line(frame, clicks[i - 1], clicks[i], color_line, 2)
    for pt in clicks:
        cv2.circle(frame, pt, 5, (0, 255, 255), -1)


def edit_polygon_on_frame(
    frame: np.ndarray,
    *,
    camera_id: str,
    zone_id: str,
    zone_name: str,
    zone_type: ZoneType = ZoneType.GENERAL,
    window_name: str = "Zone Polygon Editor",
) -> Zone | None:
    """Interactive editor; returns :class:`Zone` or ``None`` if cancelled."""
    clicks: list[tuple[int, int]] = []
    closed = False
    display = frame.copy()
    result: list[Zone | None] = [None]

    def _redraw() -> None:
        nonlocal display
        display = frame.copy()
        _draw_polygon(display, clicks, closed=closed)
        status = "closed" if closed else f"{len(clicks)} point(s)"
        cv2.putText(
            display,
            f"Zone: {zone_name} ({zone_id}) — {status}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        cv2.imshow(window_name, display)

    def _close_polygon() -> bool:
        nonlocal closed
        if len(clicks) < 3:
            print("Need at least 3 points to close the polygon.")
            return False
        closed = True
        _redraw()
        return True

    def _build_zone() -> Zone | None:
        if not closed or len(clicks) < 3:
            return None
        coords = tuple((float(x), float(y)) for x, y in clicks)
        return Zone(
            zone_id=zone_id,
            zone_name=zone_name,
            camera_id=camera_id,
            polygon_coordinates=coords,
            zone_type=zone_type,
        )

    def _on_mouse(event, x, y, _flags, _param) -> None:
        nonlocal closed
        if event == cv2.EVENT_LBUTTONDOWN and not closed:
            clicks.append((x, y))
            _redraw()
        elif event == cv2.EVENT_RBUTTONDOWN and not closed:
            _close_polygon()

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, frame.shape[1], frame.shape[0])
    cv2.setMouseCallback(window_name, _on_mouse)
    _redraw()

    print(
        f"Displaying {frame.shape[1]}×{frame.shape[0]} "
        "(pipeline / zone coordinates).\n"
        "Click: polygon vertices. Right-click or 'c' to close. "
        "Keys: r=reset, s=save, q=quit"
    )

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key in (ord("q"), 27):
            result[0] = _build_zone()
            break
        if key == ord("r"):
            clicks.clear()
            closed = False
            _redraw()
        if key == ord("c"):
            _close_polygon()
        if key == ord("s"):
            if not closed:
                _close_polygon()
            zone = _build_zone()
            if zone is None:
                print("Need a closed polygon (≥ 3 points) before saving.")
            else:
                result[0] = zone
                break

    cv2.destroyWindow(window_name)
    return result[0]


def _read_first_frame(source: str | Path) -> np.ndarray:
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {source}")
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError(f"Could not read a frame from {source}")
    return frame


def _merge_zone_into_config(
    config_path: Path,
    zone: Zone,
    *,
    camera_id: str,
) -> ZoneConfig:
    if config_path.is_file():
        config = ZoneConfig.load_json(config_path)
        zones = [z for z in config.zones if z.zone_id != zone.zone_id]
        zones.append(zone)
        return ZoneConfig(camera_id=camera_id, zones=tuple(zones))
    return ZoneConfig(camera_id=camera_id, zones=(zone,))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draw a zone polygon on a video frame")
    parser.add_argument("source", help="Video or image path (first frame is used)")
    parser.add_argument("--camera-id", required=True, help="Camera id for the zone config")
    parser.add_argument("--zone-id", required=True, help="Stable zone identifier")
    parser.add_argument("--zone-name", required=True, help="Human-readable zone name")
    parser.add_argument(
        "--zone-type",
        default=ZoneType.GENERAL.value,
        choices=[t.value for t in ZoneType],
        help="Zone semantic type",
    )
    parser.add_argument(
        "--long-side",
        type=int,
        default=DEFAULT_LONG_SIDE,
        help="Downscale frame to this long-side px before editing (default: 640)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Save ZoneConfig JSON here (merges with existing zones)",
    )
    args = parser.parse_args(argv)

    raw = _read_first_frame(args.source)
    if raw.shape[1] > args.long_side or raw.shape[0] > args.long_side:
        print(
            f"Source frame {raw.shape[1]}×{raw.shape[0]} → "
            f"downscaling to {args.long_side}px long side for display."
        )
    frame = resize_long_side(raw, args.long_side)
    zone = edit_polygon_on_frame(
        frame,
        camera_id=args.camera_id,
        zone_id=args.zone_id,
        zone_name=args.zone_name,
        zone_type=ZoneType(args.zone_type),
    )
    if zone is None:
        print("No zone saved.")
        return 1

    print(zone.to_dict())
    if args.output:
        out = Path(args.output)
        config = _merge_zone_into_config(out, zone, camera_id=args.camera_id)
        config.save_json(out)
        print(f"Saved {len(config.zones)} zone(s) → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
