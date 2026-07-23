"""Detector factory — pick the right :class:`PersonDetector` backend.

Single entry point so downstream modules never branch on PyTorch-vs-ONNX or on
which model file is in use (PRD §10: "detection model should be replaceable
without changing downstream analytics modules"). Swap backends by changing one
argument to :func:`create_detector` — nothing downstream changes.
"""

from __future__ import annotations

import os
from pathlib import Path

from .base import DEFAULT_INPUT_SIZE, PersonDetector
from .types import DetectionBackend
from .ultralytics_detector import DEFAULT_MODEL, UltralyticsDetector

# Default location for downloaded/exported weights. Kept out of git (.gitignore).
DEFAULT_MODELS_DIR = Path(__file__).resolve().parent.parent / "models"


def _resolve_model_path(
    model_path: str | Path | None,
    backend: str,
    models_dir: Path = DEFAULT_MODELS_DIR,
) -> str | Path:
    """Pick the default model file for a backend, rooted under ``models/``.

    - Ultralytics: ``models/yolov8n.pt`` (Ultralytics auto-downloads on first
      use if missing).
    - ONNX: ``models/yolov8n.onnx`` (must be produced by export_onnx first).
    """
    if model_path is not None:
        return model_path

    models_dir.mkdir(parents=True, exist_ok=True)
    if backend == DetectionBackend.ONNX.value:
        return models_dir / "yolov8n.onnx"
    return models_dir / DEFAULT_MODEL  # yolov8n.pt


def create_detector(
    model_path: str | Path | None = None,
    *,
    backend: str = DetectionBackend.ULTRALYTICS.value,
    conf_threshold: float | None = None,
    iou_threshold: float | None = None,
    person_only: bool = True,
    input_size: int = DEFAULT_INPUT_SIZE,
) -> PersonDetector:
    """Construct a :class:`PersonDetector`.

    Parameters
    ----------
    model_path:
        Model file. If None, a sensible default is chosen per backend under
        ``inference/models/`` (``yolov8n.pt`` for Ultralytics, ``yolov8n.onnx``
        for ONNX).
    backend:
        ``"ultralytics"`` (PyTorch, default — for development/accuracy work) or
        ``"onnx"`` (ONNX Runtime CPU — for the faster production path).
    conf_threshold, iou_threshold:
        Detection thresholds; default to the package constants when None.
    person_only:
        Keep only COCO class 0 (person). Default True for CCTV use.
    input_size:
        Network input edge (640 matches Module 1's downscale).
    """
    common: dict = {
        "person_only": person_only,
        "input_size": input_size,
    }
    if conf_threshold is not None:
        common["conf_threshold"] = conf_threshold
    if iou_threshold is not None:
        common["iou_threshold"] = iou_threshold

    resolved = _resolve_model_path(model_path, backend)

    if backend == DetectionBackend.ULTRALYTICS.value:
        return UltralyticsDetector(resolved, **common)
    if backend == DetectionBackend.ONNX.value:
        from .onnx_detector import ONNXDetector

        return ONNXDetector(resolved, **common)

    raise ValueError(
        f"Unknown backend {backend!r}; use "
        f"{DetectionBackend.ULTRALYTICS.value!r} or {DetectionBackend.ONNX.value!r}"
    )
