"""Ultralytics (PyTorch) person detector — the reference backend.

This is the canonical implementation: YOLOv8n via Ultralytics, on CPU. It's what
we develop and tune accuracy against, and it's also the source we export ONNX
from (:meth:`UltralyticsDetector.export_onnx`) for the faster production path in
:mod:`inference.detection.onnx_detector`.

Heavy deps (``ultralytics`` + ``torch``) are imported lazily in ``__init__`` so
importing the package is cheap and so the ONNX-only path doesn't drag in torch.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .base import (
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_INPUT_SIZE,
    DEFAULT_IOU_THRESHOLD,
    DetectorError,
    PersonDetector,
    PERSON_CLASS_NAME,
)
from .types import Detection, DetectionBackend

if TYPE_CHECKING:  # pragma: no cover - typing only
    import numpy as np


# Default model. YOLOv8n (nano) per the task spec — fast on CPU, good enough as
# a baseline; swap the path for yolov8s/m if Module 18 shows accuracy is the
# bottleneck before FPS.
DEFAULT_MODEL = "yolov8n.pt"


class UltralyticsDetector(PersonDetector):
    """Person detector backed by ``ultralytics.YOLO`` (PyTorch on CPU).

    Parameters
    ----------
    model_path:
        Path or Ultralytics model name (``"yolov8n.pt"`` by default). A bare
        name auto-downloads into Ultralytics' cache on first use; an explicit
        path is loaded directly.
    conf_threshold, iou_threshold, person_only, input_size:
        See :class:`~inference.detection.base.PersonDetector`.
    """

    def __init__(
        self,
        model_path: str | Path = DEFAULT_MODEL,
        *,
        conf_threshold: float = DEFAULT_CONF_THRESHOLD,
        iou_threshold: float = DEFAULT_IOU_THRESHOLD,
        person_only: bool = True,
        input_size: int = DEFAULT_INPUT_SIZE,
    ) -> None:
        super().__init__(
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold,
            person_only=person_only,
            input_size=input_size,
        )
        self._model_path = str(model_path)
        self._model = self._load_model(self._model_path)

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def _load_model(self, model_path: str):
        
        try:
            # torch is an ultralytics dependency; importing here makes the lazy
            # boundary explicit and gives a clearer error if it's missing.
            import torch  # noqa: F401
            from ultralytics import YOLO
        except ImportError as exc:  # pragma: no cover - env-dependent
            raise DetectorError(
                "ultralytics/torch not installed; run "
                "`pip install ultralytics` to use UltralyticsDetector"
            ) from exc

        try:
            return YOLO(model_path)
        except Exception as exc:  # malformed path, download failure, corrupt weights
            raise DetectorError(f"Failed to load model '{model_path}': {exc}") from exc

    # ------------------------------------------------------------------ #
    # Inference
    # ------------------------------------------------------------------ #
    def _raw_infer(self, frame: "np.ndarray") -> list[Detection]:
        # verbose=False keeps the hot loop off stdout. imgsz=input_size matches
        # Module 1's 640px downscale so there's no extra resize. We do NOT pass
        # classes=[0] here even when person_only: the ABC's detect() filters,
        # and keeping _raw_infer unfiltered lets multi-class callers bypass it.
        results = self._model.predict(
            frame,
            conf=self._conf_threshold,
            iou=self._iou_threshold,
            imgsz=self._input_size,
            verbose=False,
        )
        if not results:
            return []
        return self._results_to_detections(results[0])

    def _results_to_detections(self, result) -> list[Detection]:
        """Map an Ultralytics ``Results`` object to ``Detection`` records.

        Ultralytics returns boxes in the original input-frame coordinate space
        (it undoes letterboxing internally), so no coordinate rescale is needed
        here. timestamp/camera_id are filled with placeholders; the ABC
        overwrites them authoritatively.
        """
        boxes = result.boxes
        if boxes is None or len(boxes) == 0:
            return []

        # .xyxy -> (N,4) tensor; .conf -> (N,1); .cls -> (N,1). Convert once.
        xyxy = boxes.xyxy.cpu().numpy()
        confs = boxes.conf.cpu().numpy()
        clses = boxes.cls.cpu().numpy()

        names = result.names  # {int: str}, e.g. {0: "person", ...}

        out: list[Detection] = []
        for (x1, y1, x2, y2), conf, cls_id in zip(xyxy, confs, clses):
            cls_int = int(cls_id)
            out.append(
                Detection(
                    bbox=(float(x1), float(y1), float(x2), float(y2)),
                    confidence=float(conf),
                    class_id=cls_int,
                    class_name=str(names.get(cls_int, str(cls_int))),
                    timestamp=0.0,   # stamped authoritatively by detect()
                    camera_id="",    # stamped authoritatively by detect()
                )
            )
        return out

    # ------------------------------------------------------------------ #
    # Backend identity + ONNX export + release
    # ------------------------------------------------------------------ #
    def backend(self) -> DetectionBackend:
        return DetectionBackend.ULTRALYTICS

    def export_onnx(self, path: str | Path | None = None) -> Path:
        """Export the loaded model to ONNX (PRD §10 swappability enabler).

        Produces ``<model_stem>.onnx`` next to the weights (or at ``path``).
        Run once after detection is functionally correct; the resulting .onnx is
        consumed by :class:`~inference.detection.onnx_detector.ONNXDetector`.
        """
        if path is None:
            base = Path(self._model_path)
            path = base.with_suffix(".onnx")
        try:
            out = self._model.export(format="onnx", imgsz=self._input_size)
        except Exception as exc:
            raise DetectorError(f"ONNX export failed: {exc}") from exc
        # export() returns the output path (str) in recent Ultralytics versions.
        exported = Path(out) if not isinstance(out, Path) else out
        if Path(path) != exported and exported.exists():
            # Honour an explicit requested path by moving the exported file.
            target = Path(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            exported.replace(target)
            return target
        return exported

    def release(self) -> None:
        self._model = None
