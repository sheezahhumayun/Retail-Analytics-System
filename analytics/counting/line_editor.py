"""MVP counting-line editor — click-to-define geometry in OpenCV.

Full admin UI for line configuration is Module 16; this is enough for dev and
test against sample footage.

Usage
-----
PowerShell — single line (bash ``\\`` continuation does not work in PS)::

    python -m analytics.counting.line_editor sample-data/entrance.mp4 --camera-id entrance --output tests/videos/entrance_line.json

Or with PowerShell line continuation (backtick at end of line)::

    python -m analytics.counting.line_editor sample-data/entrance.mp4 `
        --camera-id entrance --output tests/videos/entrance_line.json

Controls
--------
- Left-click: set line endpoint 1, then endpoint 2, then a point on the
  *inside* side of the store.
- ``r``: reset clicks.
- ``s``: save JSON (requires all three clicks).
- ``q`` / ESC: quit (saves first if complete).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from inference.video import DEFAULT_LONG_SIDE, resize_long_side

from .geometry import cross_product_z, is_inside, point_side
from .types import CountingLine, InsideSide


def _shade_inside_half(
    frame: np.ndarray,
    p1: tuple[int, int],
    p2: tuple[int, int],
    inside_side: InsideSide,
) -> None:
    """Tint the *inside* half-plane green so the user can verify direction."""
    h, w = frame.shape[:2]
    probe = CountingLine(
        x1=float(p1[0]),
        y1=float(p1[1]),
        x2=float(p2[0]),
        y2=float(p2[1]),
        inside_side=inside_side,
        camera_id="",
    )
    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    inside_corners = [c for c in corners if is_inside(probe, c)]
    if not inside_corners:
        return
    poly = np.array([p1, p2, *inside_corners[::-1]], dtype=np.int32)
    overlay = frame.copy()
    cv2.fillPoly(overlay, [poly], (0, 160, 0))
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)


def _read_first_frame(source: str | Path) -> np.ndarray:
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {source}")
    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        raise RuntimeError(f"Could not read a frame from {source}")
    return frame


def _inside_side_from_click(
    line_start: tuple[float, float],
    line_end: tuple[float, float],
    inside_click: tuple[float, float],
) -> InsideSide:
    """Pick LEFT/RIGHT so the clicked point is on the inside."""
    clicked = point_side(
        CountingLine(
            x1=line_start[0],
            y1=line_start[1],
            x2=line_end[0],
            y2=line_end[1],
            inside_side=InsideSide.LEFT,
            camera_id="",
        ),
        inside_click,
    )
    return clicked


def edit_line_on_frame(
    frame: np.ndarray,
    *,
    camera_id: str,
    name: str = "line_1",
    window_name: str = "Counting Line Editor",
) -> CountingLine | None:
    """Interactive editor; returns :class:`CountingLine` or ``None`` if cancelled."""
    clicks: list[tuple[int, int]] = []
    display = frame.copy()
    result: list[CountingLine | None] = [None]

    def _redraw() -> None:
        nonlocal display
        display = frame.copy()
        if len(clicks) >= 1:
            cv2.circle(display, clicks[0], 6, (0, 255, 255), -1)
        if len(clicks) >= 2:
            cv2.circle(display, clicks[1], 6, (0, 255, 255), -1)
            cv2.line(display, clicks[0], clicks[1], (0, 200, 255), 2)
        if len(clicks) >= 3:
            p1, p2, inside_pt = clicks[0], clicks[1], clicks[2]
            side = _inside_side_from_click(p1, p2, inside_pt)
            _shade_inside_half(display, p1, p2, side)
            cv2.circle(display, inside_pt, 6, (0, 255, 0), -1)
            mid = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
            cp = cross_product_z(p1, p2, inside_pt)
            # Arrow from midpoint toward inside (perpendicular to line).
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            length = max((dx * dx + dy * dy) ** 0.5, 1.0)
            nx, ny = -dy / length, dx / length
            if cp < 0:
                nx, ny = -nx, -ny
            tip = (int(mid[0] + nx * 40), int(mid[1] + ny * 40))
            cv2.arrowedLine(display, mid, tip, (0, 255, 0), 2, tipLength=0.3)
            cv2.putText(
                display,
                f"inside={side.value} (green tint = store floor)",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
                cv2.LINE_AA,
            )
        cv2.imshow(window_name, display)

    def _on_mouse(event, x, y, _flags, _param) -> None:
        if event != cv2.EVENT_LBUTTONDOWN:
            return
        if len(clicks) < 3:
            clicks.append((x, y))
            _redraw()

    def _build_line() -> CountingLine | None:
        if len(clicks) < 3:
            return None
        p1, p2, inside_pt = clicks[0], clicks[1], clicks[2]
        side = _inside_side_from_click(p1, p2, inside_pt)
        return CountingLine(
            x1=float(p1[0]),
            y1=float(p1[1]),
            x2=float(p2[0]),
            y2=float(p2[1]),
            inside_side=side,
            camera_id=camera_id,
            name=name,
        )

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, frame.shape[1], frame.shape[0])
    cv2.setMouseCallback(window_name, _on_mouse)
    _redraw()

    print(
        f"Displaying {frame.shape[1]}×{frame.shape[0]} "
        "(pipeline / counting-line coordinates).\n"
        "Click: (1) line start, (2) line end, (3) inside side. "
        "Keys: r=reset, s=save, q=quit"
    )

    while True:
        key = cv2.waitKey(20) & 0xFF
        if key in (ord("q"), 27):
            line = _build_line()
            result[0] = line
            break
        if key == ord("r"):
            clicks.clear()
            _redraw()
        if key == ord("s"):
            line = _build_line()
            if line is None:
                print("Need 3 clicks before saving.")
            else:
                result[0] = line
                break

    cv2.destroyWindow(window_name)
    return result[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Draw a counting line on a video frame")
    parser.add_argument("source", help="Video or image path (first frame is used)")
    parser.add_argument("--camera-id", required=True, help="Camera id for the line config")
    parser.add_argument("--name", default="line_1", help="Line name")
    parser.add_argument(
        "--long-side",
        type=int,
        default=DEFAULT_LONG_SIDE,
        help="Downscale frame to this long-side px before editing (default: 640, "
        "matches Module 1 / detection pipeline)",
    )
    parser.add_argument("--output", "-o", help="Save CountingLine JSON here")
    args = parser.parse_args(argv)

    raw = _read_first_frame(args.source)
    if raw.shape[1] > args.long_side or raw.shape[0] > args.long_side:
        print(
            f"Source frame {raw.shape[1]}×{raw.shape[0]} → "
            f"downscaling to {args.long_side}px long side for display "
            "(saved coordinates match the detection pipeline)."
        )
    frame = resize_long_side(raw, args.long_side)
    line = edit_line_on_frame(frame, camera_id=args.camera_id, name=args.name)
    if line is None:
        print("No line saved.")
        return 1

    print(line.to_dict())
    if args.output:
        line.save_json(args.output)
        print(f"Saved → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
