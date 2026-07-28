"""Heatmap visualization — blur, colormap, reference-frame overlay (PRD §17)."""

from __future__ import annotations

import cv2
import numpy as np

from .accumulator import HeatmapAccumulator


def _upsample_grid(grid: np.ndarray, width: int, height: int) -> np.ndarray:
    """Resize accumulator grid to match reference frame dimensions."""
    if grid.shape[1] == width and grid.shape[0] == height:
        return grid
    return cv2.resize(grid, (width, height), interpolation=cv2.INTER_LINEAR)


def _normalize_uint8(grid: np.ndarray) -> np.ndarray:
    if grid.size == 0:
        return np.zeros_like(grid, dtype=np.uint8)
    peak = float(grid.max())
    if peak <= 1e-6:
        return np.zeros(grid.shape, dtype=np.uint8)
    scaled = (grid / peak * 255.0).clip(0, 255)
    return scaled.astype(np.uint8)


def render_heatmap_overlay(
    accumulator: HeatmapAccumulator,
    reference_frame: np.ndarray,
    *,
    blur_sigma: float = 15.0,
    colormap: int = cv2.COLORMAP_JET,
    density_alpha: float = 0.55,
    trajectory_alpha: float = 0.35,
    draw_trajectories: bool = True,
) -> np.ndarray:
    """Blur density, apply colormap, alpha-blend over ``reference_frame``.

    ``reference_frame`` must be BGR with shape ``(spec.height, spec.width, 3)``
    — the same dimensions stored in the accumulator spec. The internal grid is
    upsampled to this size before blending so there is no offset/scaling mismatch.
    """
    ref = reference_frame
    if ref.ndim != 3 or ref.shape[2] != 3:
        raise ValueError("reference_frame must be a BGR image (H, W, 3)")
    h, w = ref.shape[:2]
    spec = accumulator.spec
    if (w, h) != (spec.width, spec.height):
        raise ValueError(
            f"reference_frame {w}x{h} does not match accumulator spec "
            f"{spec.width}x{spec.height}"
        )

    density = accumulator.density
    ksize = int(max(3, round(blur_sigma * 4))) | 1
    density_blur = cv2.GaussianBlur(density, (ksize, ksize), blur_sigma)
    density_up = _upsample_grid(density_blur, w, h)
    heat_gray = _normalize_uint8(density_up)
    heat_color = cv2.applyColorMap(heat_gray, colormap)

    out = ref.copy()
    mask = heat_gray > 0
    if mask.any():
        blended = cv2.addWeighted(
            ref, 1.0 - density_alpha, heat_color, density_alpha, 0
        )
        out[mask] = blended[mask]

    if draw_trajectories and accumulator.trajectory.max() > 0:
        traj = accumulator.trajectory
        traj_blur = cv2.GaussianBlur(traj, (ksize, ksize), blur_sigma * 0.6)
        traj_up = _upsample_grid(traj_blur, w, h)
        traj_gray = _normalize_uint8(traj_up)
        traj_color = cv2.applyColorMap(traj_gray, cv2.COLORMAP_HOT)
        tmask = traj_gray > 0
        if tmask.any():
            blended_t = cv2.addWeighted(
                out, 1.0 - trajectory_alpha, traj_color, trajectory_alpha, 0
            )
            out[tmask] = blended_t[tmask]

    return out
