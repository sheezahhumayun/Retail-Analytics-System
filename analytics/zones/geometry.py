"""Zone geometry helpers — point-in-polygon via OpenCV."""

from __future__ import annotations

import cv2
import numpy as np

from analytics.counting.geometry import foot_point_from_bbox

from .types import Zone

__all__ = ["foot_point_from_bbox", "point_in_polygon", "is_inside_zone"]


def point_in_polygon(
    polygon: tuple[tuple[float, float], ...],
    point: tuple[float, float],
) -> bool:
    """Return ``True`` when ``point`` is inside or on the polygon boundary.

    Uses :func:`cv2.pointPolygonTest` — positive/zero means inside or on edge.
    """
    if len(polygon) < 3:
        return False
    contour = np.array(polygon, dtype=np.float32).reshape((-1, 1, 2))
    result = cv2.pointPolygonTest(contour, point, measureDist=False)
    return result >= 0.0


def is_inside_zone(zone: Zone, point: tuple[float, float]) -> bool:
    """Return ``True`` when ``point`` lies inside ``zone``'s polygon."""
    return point_in_polygon(zone.polygon_coordinates, point)
