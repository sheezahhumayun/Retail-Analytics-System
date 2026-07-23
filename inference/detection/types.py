"""Detection return types (PRD §10 contract).

PRD §10 says detection must return: bounding box, confidence, class, timestamp,
camera ID. :class:`Detection` carries exactly those fields so every downstream
module (tracking, counting, zones, dwell, heatmaps, queues) consumes one shape.

The type is frozen + slotted: detections are produced in tight loops and passed
around immutably, so we make them cheap to allocate and impossible to mutate
in place.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DetectionBackend(str, Enum):
    """Which inference runtime a detector uses. PRD §10 mandates the model be
    swappable without changing downstream code; this enum labels the seam."""

    ULTRALYTICS = "ultralytics"  # PyTorch via Ultralytics (dev / accuracy work)
    ONNX = "onnx"                # ONNX Runtime, CPU EP (production / fastest CPU)


@dataclass(frozen=True, slots=True)
class Detection:
    """One person detection in one frame.

    Attributes
    ----------
    bbox:
        ``(x1, y1, x2, y2)`` pixel coordinates in the *input frame* that was
        passed to ``detect()`` (i.e. the downscaled frame from Module 1, not the
        letterboxed network input). Top-left origin, x right / y down.
    confidence:
        Model confidence in ``[0.0, 1.0]``.
    class_id:
        COCO class id. After the default ``person_only`` filter this is always
        ``0``; kept on the object so multi-class extensions later don't need a
        schema change.
    class_name:
        Human-readable label (``"person"`` by default).
    timestamp:
        Frame time as epoch seconds. Defaults to the moment of detection if the
        caller doesn't supply one (e.g. from the source's frame clock).
    camera_id:
        Which camera/source produced the frame. Required for the event
        architecture in Module 10 / DB in Module 11.
    """

    bbox: tuple[float, float, float, float]
    confidence: float
    class_id: int
    class_name: str
    timestamp: float
    camera_id: str

    @property
    def x1(self) -> float:
        return self.bbox[0]

    @property
    def y1(self) -> float:
        return self.bbox[1]

    @property
    def x2(self) -> float:
        return self.bbox[2]

    @property
    def y2(self) -> float:
        return self.bbox[3]

    @property
    def width(self) -> float:
        return self.bbox[2] - self.bbox[0]

    @property
    def height(self) -> float:
        return self.bbox[3] - self.bbox[1]

    @property
    def center(self) -> tuple[float, float]:
        """Centroid ``(cx, cy)`` — the point zones/heatmaps key off."""
        return (
            (self.bbox[0] + self.bbox[2]) / 2.0,
            (self.bbox[1] + self.bbox[3]) / 2.0,
        )
