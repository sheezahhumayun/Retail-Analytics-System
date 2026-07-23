"""ONNX Runtime person detector — the production CPU backend.

Once detection is functionally correct in the Ultralytics (PyTorch) backend,
exporting to ONNX and running via ONNX Runtime's CPUExecutionProvider is
typically 20–40% faster than raw PyTorch on CPU at no accuracy cost (the export
is lossless). This backend implements the full pre/post-processing pipeline
that Ultralytics hides behind ``predict()``:

  frame -> letterbox(640) -> normalize -> NCHW -> session.run
        -> [1,84,8400] grid -> conf filter -> class filter -> XYXY -> NMS

Coordinate handling matters: the network sees a letterboxed image, so decoded
boxes must be unscaled back to the *original* input-frame pixels (the same
coordinate space the Ultralytics backend reports). That keeps the two backends
drop-in interchangeable.
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


def letterbox(
    image: "np.ndarray",
    new_shape: int = 640,
) -> tuple["np.ndarray", float, tuple[int, int]]:
    """Resize ``image`` to fit a ``new_shape`` x ``new_shape`` canvas, keeping
    aspect ratio and padding grey (114).

    Returns the padded image, the scale factor applied, and the
    ``(pad_w, pad_h)`` letterbox padding in px — both needed to map network
    boxes back to original coordinates.
    """
    import cv2
    import numpy as np

    h0, w0 = image.shape[:2]
    r = float(new_shape) / max(h0, w0)
    new_w, new_h = max(1, int(round(w0 * r))), max(1, int(round(h0 * r)))
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    pad_w = (new_shape - new_w) / 2.0
    pad_h = (new_shape - new_h) / 2.0
    top, bottom = int(round(pad_h)), new_shape - new_h - int(round(pad_h))
    left, right = int(round(pad_w)), new_shape - new_w - int(round(pad_w))
    padded = cv2.copyMakeBorder(
        resized, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114)
    )
    return padded, r, (int(round(pad_w)), int(round(pad_h)))


class ONNXDetector(PersonDetector):
    """Person detector backed by ONNX Runtime (CPUExecutionProvider).

    Parameters
    ----------
    model_path:
        Path to a ``.onnx`` export of a YOLOv8 model (produce one via
        :meth:`inference.detection.ultralytics_detector.UltralyticsDetector.export_onnx`).
    conf_threshold, iou_threshold, person_only, input_size:
        See :class:`~inference.detection.base.PersonDetector`.
    """

    def __init__(
        self,
        model_path: str | Path,
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
        self._session, self._input_name, self._output_name = self._load_session(
            self._model_path
        )

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #
    def _load_session(self, model_path: str):
        try:
            import onnxruntime as ort
        except ImportError as exc:  # pragma: no cover - env-dependent
            raise DetectorError(
                "onnxruntime not installed; run `pip install onnxruntime`"
            ) from exc

        p = Path(model_path)
        if not p.exists():
            raise DetectorError(f"ONNX model not found: {model_path}")

        try:
            session = ort.InferenceSession(
                model_path, providers=["CPUExecutionProvider"]
            )
        except Exception as exc:
            raise DetectorError(f"Failed to init ONNX session: {exc}") from exc

        input_name = session.get_inputs()[0].name
        output_name = session.get_outputs()[0].name
        return session, input_name, output_name

    # ------------------------------------------------------------------ #
    # Inference
    # ------------------------------------------------------------------ #
    def _raw_infer(self, frame: "np.ndarray") -> list[Detection]:
        import cv2
        import numpy as np

        h0, w0 = frame.shape[:2]

        # --- Preprocess: letterbox + normalize + NCHW --------------------- #
        padded, r, (pad_w, pad_h) = letterbox(frame, self._input_size)
        blob = padded[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
        blob = blob[None]  # add batch dim -> (1, 3, H, W)

        # --- Inference ---------------------------------------------------- #
        preds = self._session.run([self._output_name], {self._input_name: blob})[0]

        # --- Postprocess -------------------------------------------------- #
        return self._postprocess(preds, r, pad_w, pad_h, w0, h0)

    def _postprocess(
        self,
        preds: "np.ndarray",
        scale: float,
        pad_w: int,
        pad_h: int,
        orig_w: int,
        orig_h: int,
    ) -> list[Detection]:
        """Decode YOLOv8 output grid -> person detections in original coords.

        Ultralytics-exported YOLOv8 ONNX emits ``(1, 84, 8400)``:
        rows = [cx, cy, w, h, <80 class scores>], columns = anchor predictions.
        We take the max class score per anchor, threshold by conf, convert
        cxcywh->xyxy, undo letterbox (scale + un-pad + clip), then NMS.
        """
        import cv2
        import numpy as np

        # preds: (1, 84, 8400) -> (8400, 84) for easier row-wise work.
        pred = preds[0].T
        if pred.shape[1] < 5:
            return []

        boxes_cxcywh = pred[:, :4]
        scores_all = pred[:, 4:]
        # Best class + score per anchor.
        class_ids = scores_all.argmax(axis=1)
        max_scores = scores_all.max(axis=1)

        # Confidence filter (applies to all classes; person-only filter is the
        # ABC's job, but we still conf-filter here to shrink the NMS input).
        keep_mask = max_scores >= self._conf_threshold
        boxes_cxcywh = boxes_cxcywh[keep_mask]
        class_ids = class_ids[keep_mask]
        max_scores = max_scores[keep_mask]

        if len(boxes_cxcywh) == 0:
            return []

        # --- Undo letterbox: network coords -> original frame coords ------- #
        # cxcywh in network space -> xyxy -> scale down -> remove pad -> clip.
        cx, cy, w, h = (
            boxes_cxcywh[:, 0],
            boxes_cxcywh[:, 1],
            boxes_cxcywh[:, 2],
            boxes_cxcywh[:, 3],
        )
        x1 = (cx - w / 2.0 - pad_w) / scale
        y1 = (cy - h / 2.0 - pad_h) / scale
        x2 = (cx + w / 2.0 - pad_w) / scale
        y2 = (cy + h / 2.0 - pad_h) / scale
        x1 = np.clip(x1, 0, orig_w)
        y1 = np.clip(y1, 0, orig_h)
        x2 = np.clip(x2, 0, orig_w)
        y2 = np.clip(y2, 0, orig_h)
        valid = (x2 > x1) & (y2 > y1)
        x1, y1, x2, y2 = x1[valid], y1[valid], x2[valid], y2[valid]
        class_ids, max_scores = class_ids[valid], max_scores[valid]
        # cv2.dnn.NMSBoxes wants (x, y, w, h) boxes in original space.
        nms_boxes = np.stack([x1, y1, x2 - x1, y2 - y1], axis=1).tolist()
        confs = max_scores.tolist()

        idxs = cv2.dnn.NMSBoxes(
            nms_boxes, confs, self._conf_threshold, self._iou_threshold
        )
        if len(idxs) == 0:
            return []
        # NMSBoxes returns [[i], ...] in newer OpenCV; flatten defensively.
        idxs = [i[0] if isinstance(i, (list, tuple, np.ndarray)) else i for i in idxs]

        # COCO class names for the 80 classes YOLOv8 ships with. We only ever
        # report "person" by default (ABC filters), but keep the real label for
        # any multi-class use.
        out: list[Detection] = []
        for i in idxs:
            cls_int = int(class_ids[i])
            out.append(
                Detection(
                    bbox=(float(x1[i]), float(y1[i]), float(x2[i]), float(y2[i])),
                    confidence=float(max_scores[i]),
                    class_id=cls_int,
                    class_name=_COCO_NAMES.get(cls_int, str(cls_int)),
                    timestamp=0.0,   # stamped authoritatively by detect()
                    camera_id="",    # stamped authoritatively by detect()
                )
            )
        return out

    # ------------------------------------------------------------------ #
    def backend(self) -> DetectionBackend:
        return DetectionBackend.ONNX

    def release(self) -> None:
        self._session = None


# COCO 80-class label table (class 0 = person is the only one used by default).
# Inlined so the ONNX path doesn't need Ultralytics loaded at inference time.
_COCO_NAMES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane",
    5: "bus", 6: "train", 7: "truck", 8: "boat", 9: "traffic light",
    10: "fire hydrant", 11: "stop sign", 12: "parking meter", 13: "bench",
    14: "bird", 15: "cat", 16: "dog", 17: "horse", 18: "sheep", 19: "cow",
    20: "elephant", 21: "bear", 22: "zebra", 23: "giraffe", 24: "backpack",
    25: "umbrella", 26: "handbag", 27: "tie", 28: "suitcase", 29: "frisbee",
    30: "skis", 31: "snowboard", 32: "sports ball", 33: "kite", 34: "baseball bat",
    35: "baseball glove", 36: "skateboard", 37: "surfboard", 38: "tennis racket",
    39: "bottle", 40: "wine glass", 41: "cup", 42: "fork", 43: "knife",
    44: "spoon", 45: "bowl", 46: "banana", 47: "apple", 48: "sandwich",
    49: "orange", 50: "broccoli", 51: "carrot", 52: "hot dog", 53: "pizza",
    54: "donut", 55: "cake", 56: "chair", 57: "couch", 58: "potted plant",
    59: "bed", 60: "dining table", 61: "toilet", 62: "tv", 63: "laptop",
    64: "mouse", 65: "remote", 66: "keyboard", 67: "cell phone", 68: "microwave",
    69: "oven", 70: "toaster", 71: "sink", 72: "refrigerator", 73: "book",
    74: "clock", 75: "vase", 76: "scissors", 77: "teddy bear", 78: "hair drier",
    79: "toothbrush",
}
