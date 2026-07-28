"""2D heatmap accumulator — foot-point density + trajectory raster (PRD §17)."""

from __future__ import annotations

import cv2
import numpy as np

from .types import HeatmapFrameSpec


class HeatmapAccumulator:
    """Float32 density grid aligned to a camera frame via :class:`HeatmapFrameSpec`.

    Foot-points map from frame coordinates to grid cells using ``grid_scale``
  (default 1/4 resolution). On render the grid is upsampled back to the
    reference frame size so overlays align without offset/scaling bugs.
    """

    def __init__(self, spec: HeatmapFrameSpec) -> None:
        self._spec = spec
        gw, gh = spec.grid_width, spec.grid_height
        self._density = np.zeros((gh, gw), dtype=np.float32)
        self._trajectory = np.zeros((gh, gw), dtype=np.float32)

    @property
    def spec(self) -> HeatmapFrameSpec:
        return self._spec

    @property
    def density(self) -> np.ndarray:
        return self._density

    @property
    def trajectory(self) -> np.ndarray:
        return self._trajectory

    def copy(self) -> HeatmapAccumulator:
        out = HeatmapAccumulator(self._spec)
        out._density = self._density.copy()
        out._trajectory = self._trajectory.copy()
        return out

    def clear(self) -> None:
        self._density.fill(0.0)
        self._trajectory.fill(0.0)

    def add_point(self, x: float, y: float, *, weight: float = 1.0) -> None:
        """Accumulate one foot-point hit."""
        gx, gy = self._frame_to_grid(x, y)
        if 0 <= gx < self._spec.grid_width and 0 <= gy < self._spec.grid_height:
            self._density[gy, gx] += weight

    def add_segment(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        *,
        weight: float = 1.0,
    ) -> None:
        """Rasterize a movement segment onto the trajectory grid."""
        p1 = self._frame_to_grid_float(x1, y1)
        p2 = self._frame_to_grid_float(x2, y2)
        canvas = np.zeros_like(self._trajectory, dtype=np.uint8)
        cv2.line(
            canvas,
            (int(round(p1[0])), int(round(p1[1]))),
            (int(round(p2[0])), int(round(p2[1]))),
            color=1,
            thickness=1,
            lineType=cv2.LINE_AA,
        )
        self._trajectory += canvas.astype(np.float32) * weight

    def merge_inplace(self, other: HeatmapAccumulator) -> None:
        if other.spec != self._spec:
            raise ValueError("Cannot merge accumulators with different frame specs")
        self._density += other._density
        self._trajectory += other._trajectory

    def total_hits(self) -> float:
        return float(self._density.sum() + self._trajectory.sum())

    def _frame_to_grid(self, x: float, y: float) -> tuple[int, int]:
        gx = int(x / self._spec.grid_scale)
        gy = int(y / self._spec.grid_scale)
        return gx, gy

    def _frame_to_grid_float(self, x: float, y: float) -> tuple[float, float]:
        return x / self._spec.grid_scale, y / self._spec.grid_scale

    def to_arrays(self) -> dict[str, np.ndarray | dict[str, int]]:
        return {
            "density": self._density.copy(),
            "trajectory": self._trajectory.copy(),
            "spec": {
                "width": self._spec.width,
                "height": self._spec.height,
                "grid_scale": self._spec.grid_scale,
            },
        }

    @classmethod
    def from_arrays(cls, data: dict) -> HeatmapAccumulator:
        spec = HeatmapFrameSpec(
            width=int(data["spec"]["width"]),
            height=int(data["spec"]["height"]),
            grid_scale=int(data["spec"].get("grid_scale", 4)),
        )
        acc = cls(spec)
        acc._density = np.asarray(data["density"], dtype=np.float32)
        acc._trajectory = np.asarray(data["trajectory"], dtype=np.float32)
        if acc._density.shape != (spec.grid_height, spec.grid_width):
            raise ValueError("density shape does not match spec")
        return acc
