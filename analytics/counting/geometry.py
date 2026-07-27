"""Line-crossing geometry helpers.

Uses the foot-point (bottom-center of bbox) rather than the centroid — more
stable for overhead / angled CCTV where the feet cross the threshold before
the body center does.
"""

from __future__ import annotations

from .types import CountingLine, InsideSide

_EPS = 1e-9


def foot_point_from_bbox(bbox: tuple[float, float, float, float]) -> tuple[float, float]:
    """Bottom-center of a bounding box ``(x1, y1, x2, y2)``."""
    x1, _y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, y2)


def tracking_point_from_bbox(
    bbox: tuple[float, float, float, float],
    *,
    height_frac: float = 0.85,
) -> tuple[float, float]:
    """Point used for line-crossing — lower torso by default.

    Foot (``height_frac=1.0``) is ideal on high-res footage. On low-res CCTV the
    bbox bottom often lags the doorway; 0.85 catches crossings once the upper
    body has passed the line while staying near the feet.
    """
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, y1 + height_frac * (y2 - y1))


def cross_product_z(
    line_start: tuple[float, float],
    line_end: tuple[float, float],
    point: tuple[float, float],
) -> float:
    """Signed cross product (z-component) of ``line_start→line_end`` vs ``line_start→point``.

    Positive → point is to the *left* of the directed line; negative → right.
    """
    ax, ay = line_start
    bx, by = line_end
    px, py = point
    return (bx - ax) * (py - ay) - (by - ay) * (px - ax)


def point_side(
    line: CountingLine,
    point: tuple[float, float],
) -> InsideSide:
    """Which side of the line ``point`` lies on (left or right of A→B)."""
    cp = cross_product_z(line.start, line.end, point)
    if cp >= -_EPS:
        return InsideSide.LEFT
    return InsideSide.RIGHT


def is_inside(line: CountingLine, point: tuple[float, float]) -> bool:
    """Return True when ``point`` is on the configured *inside* side."""
    return point_side(line, point) == line.inside_side


def _extend_segment(
    a: tuple[float, float],
    b: tuple[float, float],
    margin: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Lengthen a segment by ``margin`` px at both ends (foot-point tolerance)."""
    import math

    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    length = math.hypot(dx, dy)
    if length < _EPS:
        return a, b
    ux, uy = dx / length, dy / length
    return (
        (ax - ux * margin, ay - uy * margin),
        (bx + ux * margin, by + uy * margin),
    )


def segment_intersection_point(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> tuple[float, float] | None:
    """Return where segments ``a1–a2`` and ``b1–b2`` meet, or ``None``."""
    x1, y1 = a1
    x2, y2 = a2
    x3, y3 = b1
    x4, y4 = b2
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < _EPS:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if -_EPS <= t <= 1.0 + _EPS and -_EPS <= u <= 1.0 + _EPS:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


def infinite_line_intersection_point(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> tuple[float, float] | None:
    """Where the infinite lines through ``a1–a2`` and ``b1–b2`` meet."""
    x1, y1 = a1
    x2, y2 = a2
    x3, y3 = b1
    x4, y4 = b2
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < _EPS:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def point_on_segment(
    point: tuple[float, float],
    seg_start: tuple[float, float],
    seg_end: tuple[float, float],
    *,
    margin: float = 0.0,
) -> bool:
    """True if ``point`` lies on ``seg_start–seg_end`` (± ``margin`` along the segment)."""
    import math

    ax, ay = seg_start
    bx, by = seg_end
    px, py = point
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq < _EPS:
        return math.hypot(px - ax, py - ay) <= margin
    t = ((px - ax) * dx + (py - ay) * dy) / length_sq
    length = math.sqrt(length_sq)
    t_margin = margin / length if length > _EPS else 0.0
    if t < -t_margin - _EPS or t > 1.0 + t_margin + _EPS:
        return False
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return math.hypot(px - proj_x, py - proj_y) <= margin + _EPS


def segments_intersect(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> bool:
    """True when open segments ``a1–a2`` and ``b1–b2`` intersect."""

    def _orient(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    o1 = _orient(a1, a2, b1)
    o2 = _orient(a1, a2, b2)
    o3 = _orient(b1, b2, a1)
    o4 = _orient(b1, b2, a2)

    if o1 * o2 < -_EPS and o3 * o4 < -_EPS:
        return True

    # Collinear / endpoint touches — treat as crossing for counting lines.
    def _on_segment(
        p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]
    ) -> bool:
        return (
            min(p[0], r[0]) - _EPS <= q[0] <= max(p[0], r[0]) + _EPS
            and min(p[1], r[1]) - _EPS <= q[1] <= max(p[1], r[1]) + _EPS
        )

    if abs(o1) <= _EPS and _on_segment(a1, b1, a2):
        return True
    if abs(o2) <= _EPS and _on_segment(a1, b2, a2):
        return True
    if abs(o3) <= _EPS and _on_segment(b1, a1, b2):
        return True
    if abs(o4) <= _EPS and _on_segment(b1, a2, b2):
        return True
    return False


def movement_crosses_line(
    line: CountingLine,
    p1: tuple[float, float],
    p2: tuple[float, float],
    *,
    margin: float = 15.0,
) -> bool:
    """True when movement ``p1→p2`` crosses the counting line segment.

    Requires an inside/outside side change and either a segment intersection
    (with endpoint margin) or the movement midpoint passing near the line.
    """
    if is_inside(line, p1) == is_inside(line, p2):
        return False

    extended = _extend_segment(line.start, line.end, margin)
    if segment_intersection_point(p1, p2, extended[0], extended[1]) is not None:
        return True

    midpoint = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
    if point_on_segment(midpoint, extended[0], extended[1], margin=margin):
        return True

    cross_pt = infinite_line_intersection_point(p1, p2, line.start, line.end)
    if cross_pt is not None and point_on_segment(
        cross_pt, line.start, line.end, margin=margin
    ):
        return True

    # Side changed while one step is near the counting segment (bbox slop).
    return point_on_segment(p1, line.start, line.end, margin=margin) or point_on_segment(
        p2, line.start, line.end, margin=margin
    )
