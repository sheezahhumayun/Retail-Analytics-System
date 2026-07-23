"""Person detection layer (Module 2).

A swappable-model interface (PRD §10) so downstream modules call ``detect(frame)``
and never depend on whether the model is PyTorch-YOLOv8n or an ONNX export.

Quick start
-----------
>>> from inference.detection import create_detector
>>> with create_detector() as det:               # Ultralytics YOLOv8n, CPU
...     detections = det.detect(frame, camera_id="cam_1")
...     print(len(detections), "people")

Swap to the faster ONNX backend with one argument — nothing else changes:
>>> det = create_detector(backend="onnx")
"""

from .base import (
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_INPUT_SIZE,
    DEFAULT_IOU_THRESHOLD,
    DetectorError,
    PERSON_CLASS_ID,
    PERSON_CLASS_NAME,
    PersonDetector,
)
from .factory import DEFAULT_MODELS_DIR, create_detector
from .onnx_detector import ONNXDetector
from .types import Detection, DetectionBackend
from .ultralytics_detector import DEFAULT_MODEL, UltralyticsDetector

__all__ = [
    # Interface + types
    "PersonDetector",
    "Detection",
    "DetectionBackend",
    "DetectorError",
    # Implementations
    "UltralyticsDetector",
    "ONNXDetector",
    # Construction
    "create_detector",
    "DEFAULT_MODELS_DIR",
    # Defaults + constants
    "DEFAULT_MODEL",
    "DEFAULT_CONF_THRESHOLD",
    "DEFAULT_IOU_THRESHOLD",
    "DEFAULT_INPUT_SIZE",
    "PERSON_CLASS_ID",
    "PERSON_CLASS_NAME",
]
