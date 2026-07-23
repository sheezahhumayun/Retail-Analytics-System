"""Person detection — swappable-model interface (PRD §10).

PRD §10: "The detection model should be replaceable without changing downstream
analytics modules." This module defines the seam: a :class:`PersonDetector` ABC
whose concrete backends (PyTorch via Ultralytics, ONNX Runtime) are
interchangeable. Downstream modules call ``detect(frame)`` and never know or
care which model produced the detections.

Cross-cutting policy lives in the ABC so the backends don't reimplement it:

* **Person-only filtering** — CCTV footage triggers detections on bags,
  mannequins, shopping carts, reflections, etc. By default we keep only COCO
  class 0 (person). This is the single biggest lever on false-positive rate and
  belongs at the detector boundary, not scattered through every consumer.
* **Timestamp + camera_id stamping** — these come from the caller/source, not
  the model, so they're attached uniformly regardless of backend.
"""

from __future__ import annotations

import abc
import time
from typing import TYPE_CHECKING

from .types import Detection, DetectionBackend

if TYPE_CHECKING:  # pragma: no cover - typing only
    import numpy as np


# Defaults centralised so every backend behaves the same and downstream can
# rely on consistent knobs. These are starting values; PRD §33 targets and
# Module 18's precision/recall work will tune them against real footage.
DEFAULT_CONF_THRESHOLD = 0.4   # Task: start at 0.4, adjust in Module 18.
DEFAULT_IOU_THRESHOLD = 0.5    # NMS IoU for overlapping-box suppression.
DEFAULT_INPUT_SIZE = 640       # YOLOv8n native input edge; matches Module 1's
                               # 640px downscale so no extra resize is needed.
PERSON_CLASS_ID = 0            # COCO "person".
PERSON_CLASS_NAME = "person"


class DetectorError(RuntimeError):
    """Raised on detector setup/inference failures a caller can react to
    (missing model file, bad frame, backend init failure)."""


class PersonDetector(abc.ABC):
    """Abstract person detector. Implementations only do raw inference; the
    common :meth:`detect` applies class filtering and stamps timestamp/camera_id.

    Parameters
    ----------
    conf_threshold:
        Minimum confidence to keep a detection. Start at 0.4 (per task) and
        tune in Module 18: too low -> mannequins/posters; too high -> missed
        people in crowds/occlusion.
    iou_threshold:
        NMS IoU threshold for suppressing overlapping detections.
    person_only:
        If True (default), drop everything except COCO class 0. CCTV footage is
        full of carts/mannequins/bags; this filter is the default for a reason.
    input_size:
        Network input edge length in px. 640 matches Module 1's downscale cap,
        so the frame handed in is already the right size.
    """

    def __init__(
        self,
        *,
        conf_threshold: float = DEFAULT_CONF_THRESHOLD,
        iou_threshold: float = DEFAULT_IOU_THRESHOLD,
        person_only: bool = True,
        input_size: int = DEFAULT_INPUT_SIZE,
    ) -> None:
        self._conf_threshold = float(conf_threshold)
        self._iou_threshold = float(iou_threshold)
        self._person_only = bool(person_only)
        self._input_size = int(input_size)

    # ------------------------------------------------------------------ #
    # Abstract API — each backend fills in raw inference + lifecycle.
    # ------------------------------------------------------------------ #
    @abc.abstractmethod
    def _raw_infer(self, frame: "np.ndarray") -> list[Detection]:
        """Run the model on ``frame`` and return *unfiltered* detections.

        Implementations must NOT apply person-only filtering or stamp
        timestamp/camera_id — :meth:`detect` does that uniformly. They should
        still honour conf/IoU thresholds internally where the backend supports
        it (Ultralytics predict, NMS in the ONNX path).
        """

    @abc.abstractmethod
    def backend(self) -> DetectionBackend:
        """Which runtime this detector uses."""

    @abc.abstractmethod
    def release(self) -> None:
        """Release model resources. Idempotent."""

    # ------------------------------------------------------------------ #
    # Concrete API — the contract every downstream module relies on.
    # ------------------------------------------------------------------ #
    def detect(
        self,
        frame: "np.ndarray",
        *,
        timestamp: float | None = None,
        camera_id: str = "default",
    ) -> list[Detection]:
        """Detect people in ``frame``.

        Returns a list of :class:`Detection` (PRD §10 contract: bbox,
        confidence, class, timestamp, camera_id). Applies the person-only filter
        and stamps timestamp (defaults to now) + camera_id uniformly across
        backends.
        """
        if frame is None or frame.size == 0:
            return []

        raw = self._raw_infer(frame)

        if self._person_only:
            raw = [d for d in raw if d.class_id == PERSON_CLASS_ID]

        if timestamp is None:
            timestamp = time.time()

        # Re-stamp every detection with the caller's timestamp/camera_id. The
        # backend's _raw_infer fills bbox/confidence/class; we overwrite the
        # context fields so they're always caller-authoritative.
        return [
            Detection(
                bbox=d.bbox,
                confidence=d.confidence,
                class_id=d.class_id,
                class_name=d.class_name,
                timestamp=timestamp,
                camera_id=camera_id,
            )
            for d in raw
        ]

    # ----- Accessors --------------------------------------------------- #
    @property
    def conf_threshold(self) -> float:
        return self._conf_threshold

    @property
    def iou_threshold(self) -> float:
        return self._iou_threshold

    @property
    def person_only(self) -> bool:
        return self._person_only

    @property
    def input_size(self) -> int:
        return self._input_size

    # ----- Context manager: a detector owns model resources ------------ #
    def __enter__(self) -> "PersonDetector":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.release()
