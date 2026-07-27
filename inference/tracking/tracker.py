"""Multi-object tracking — ByteTrack wrapper (PRD §11).

Assigns temporary, anonymous track IDs to detected people so downstream modules
(counting, dwell, zones, heatmaps) reason about *individuals*, not per-frame
detection blobs.

Uses :class:`trackers.ByteTrackTracker` (Roboflow's ``trackers`` package),
which speaks :class:`supervision.Detections` natively and is the successor to
the deprecated ``supervision.ByteTrack``. No re-ID embedding model — motion +
IoU association only, which keeps CPU cost negligible on top of detection.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

import numpy as np
import supervision as sv
from trackers import ByteTrackTracker

from inference.detection.types import Detection

from .types import PositionRecord, TrackedObject, freeze_history

if TYPE_CHECKING:  # pragma: no cover - typing only
    pass


# Defaults aligned with Module 2 detection thresholds and Module 1's ~30fps
# sample footage. Tune against real footage in Module 18.
DEFAULT_CONF_THRESHOLD = 0.4
DEFAULT_NMS_IOU_THRESHOLD = 0.5
DEFAULT_TRACK_BUFFER = 30          # frames a lost track is remembered (occlusion)
DEFAULT_FRAME_RATE = 30.0
DEFAULT_MIN_CONFIRMATION_FRAMES = 2  # suppress single-frame flicker tracks
DEFAULT_HISTORY_LENGTH = 30          # positions kept for line-cross / dwell
DEFAULT_TRACK_ACTIVATION_THRESHOLD = 0.25
DEFAULT_HIGH_CONF_DET_THRESHOLD = 0.6
DEFAULT_MIN_MATCHING_IOU = 0.1


def _bbox_iou(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> float:
    """Axis-aligned IoU between two ``(x1, y1, x2, y2)`` boxes."""
    ix1 = max(a[0], b[0])
    iy1 = max(a[1], b[1])
    ix2 = min(a[2], b[2])
    iy2 = min(a[3], b[3])
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - inter
    return inter / union if union > 0.0 else 0.0


def _detections_to_sv(detections: list[Detection]) -> sv.Detections:
    """Convert Module 2 :class:`Detection` objects to supervision format."""
    if not detections:
        return sv.Detections.empty()
    xyxy = np.asarray([d.bbox for d in detections], dtype=np.float32)
    confidence = np.asarray([d.confidence for d in detections], dtype=np.float32)
    class_id = np.asarray([d.class_id for d in detections], dtype=np.int32)
    return sv.Detections(xyxy=xyxy, confidence=confidence, class_id=class_id)


def _apply_pre_tracking_nms(
    detections: list[Detection],
    *,
    conf_threshold: float,
    nms_iou_threshold: float,
) -> list[Detection]:
    """Confidence filter + IoU NMS before tracking (duplicate-track reduction)."""
    filtered = [d for d in detections if d.confidence >= conf_threshold]
    if len(filtered) <= 1:
        return filtered

    sv_dets = _detections_to_sv(filtered).with_nms(
        threshold=nms_iou_threshold,
        class_agnostic=False,
    )
    if len(sv_dets) == 0:
        return []

    kept: list[Detection] = []
    for i in range(len(sv_dets)):
        bbox = tuple(float(v) for v in sv_dets.xyxy[i])
        # Match back to the highest-IoU source detection for metadata fields.
        best = max(filtered, key=lambda d: _bbox_iou(d.bbox, bbox))
        kept.append(
            Detection(
                bbox=bbox,
                confidence=float(sv_dets.confidence[i]),
                class_id=int(sv_dets.class_id[i]),
                class_name=best.class_name,
                timestamp=best.timestamp,
                camera_id=best.camera_id,
            )
        )
    return kept


class Tracker:
    """ByteTrack-based multi-object tracker for person detections.

  Parameters
  ----------
  camera_id:
      Default camera id stamped on outputs when detections don't carry one.
  conf_threshold:
      Minimum detection confidence before NMS / tracking.
  nms_iou_threshold:
      IoU threshold for pre-tracking non-max suppression.
  track_buffer:
      How many frames a lost track is remembered before being dropped
      (ByteTrack ``lost_track_buffer``). Increase for brief occlusions behind
      shelving or other shoppers; decrease to shed stale tracks faster.
  frame_rate:
      Source frame rate — scales the effective lost-track window when the
      processing rate differs from 30fps (e.g. Module 1's 10fps throttle).
  min_confirmation_frames:
      Consecutive frames a track must be seen before it is returned. Filters
      single-frame flicker detections (PRD §11 duplicate-track reduction).
  history_length:
      Number of recent positions stored per track for line-crossing and dwell.
  track_activation_threshold:
      ByteTrack high-confidence association threshold.
  high_conf_det_threshold:
      ByteTrack split between high- and low-confidence detection pools.
  minimum_matching_iou:
      Minimum IoU for associating a detection to an existing track.
  """

    def __init__(
        self,
        *,
        camera_id: str = "default",
        conf_threshold: float = DEFAULT_CONF_THRESHOLD,
        nms_iou_threshold: float = DEFAULT_NMS_IOU_THRESHOLD,
        track_buffer: int = DEFAULT_TRACK_BUFFER,
        frame_rate: float = DEFAULT_FRAME_RATE,
        min_confirmation_frames: int = DEFAULT_MIN_CONFIRMATION_FRAMES,
        history_length: int = DEFAULT_HISTORY_LENGTH,
        track_activation_threshold: float = DEFAULT_TRACK_ACTIVATION_THRESHOLD,
        high_conf_det_threshold: float = DEFAULT_HIGH_CONF_DET_THRESHOLD,
        minimum_matching_iou: float = DEFAULT_MIN_MATCHING_IOU,
    ) -> None:
        self._camera_id = camera_id
        self._conf_threshold = float(conf_threshold)
        self._nms_iou_threshold = float(nms_iou_threshold)
        self._history_length = int(history_length)
        self._track_buffer = int(track_buffer)

        self._byte_tracker = ByteTrackTracker(
            lost_track_buffer=track_buffer,
            frame_rate=frame_rate,
            minimum_consecutive_frames=min_confirmation_frames,
            track_activation_threshold=track_activation_threshold,
            high_conf_det_threshold=high_conf_det_threshold,
            minimum_iou_threshold=minimum_matching_iou,
        )

        self._histories: dict[int, deque[PositionRecord]] = {}
        self._last_seen_frame: dict[int, int] = {}
        self._frame_index = 0
        # Buffer positions from tracker_id=-1 frames so crossings during the
        # confirmation window are not lost (e.g. track 0 on entrance footage).
        self._preconfirm_chains: list[deque[PositionRecord]] = []
        self._preconfirm_bboxes: list[tuple[float, float, float, float]] = []

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def update(self, detections: list[Detection]) -> list[TrackedObject]:
        """Associate detections to tracks and return confirmed :class:`TrackedObject`s.

        Only tracks that have been seen for at least ``min_confirmation_frames``
        consecutive frames are returned (ByteTrack assigns ``tracker_id=-1`` until
        then).
        """
        self._frame_index += 1

        if not detections:
            self._prune_stale_histories()
            return []

        filtered = _apply_pre_tracking_nms(
            detections,
            conf_threshold=self._conf_threshold,
            nms_iou_threshold=self._nms_iou_threshold,
        )
        if not filtered:
            self._prune_stale_histories()
            return []

        frame_timestamp = filtered[0].timestamp
        frame_camera_id = filtered[0].camera_id or self._camera_id

        sv_dets = _detections_to_sv(filtered)
        tracked = self._byte_tracker.update(sv_dets)

        if len(tracked) == 0 or tracked.tracker_id is None:
            self._prune_stale_histories()
            return []

        outputs: list[TrackedObject] = []
        active_ids: set[int] = set()
        used_chains: set[int] = set()

        for i in range(len(tracked)):
            track_id = int(tracked.tracker_id[i])
            bbox = tuple(float(v) for v in tracked.xyxy[i])
            confidence = float(tracked.confidence[i])
            class_id = int(tracked.class_id[i])

            meta = max(filtered, key=lambda d: _bbox_iou(d.bbox, bbox))
            class_name = meta.class_name
            timestamp = meta.timestamp if meta.timestamp else frame_timestamp
            camera_id = meta.camera_id or frame_camera_id

            center = (
                (bbox[0] + bbox[2]) / 2.0,
                (bbox[1] + bbox[3]) / 2.0,
            )
            record = PositionRecord(center=center, timestamp=timestamp, bbox=bbox)

            if track_id < 0:
                self._append_preconfirm(bbox, record)
                continue

            active_ids.add(track_id)
            self._last_seen_frame[track_id] = self._frame_index

            history = self._histories.setdefault(
                track_id, deque(maxlen=self._history_length)
            )
            if len(history) == 0:
                chain_idx = self._match_preconfirm_chain(bbox, used_chains)
                if chain_idx is not None:
                    used_chains.add(chain_idx)
                    for rec in self._preconfirm_chains[chain_idx]:
                        history.append(rec)
            history.append(record)

            outputs.append(
                TrackedObject(
                    track_id=track_id,
                    bbox=bbox,
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    camera_id=camera_id,
                    timestamp=timestamp,
                    position_history=freeze_history(history),
                )
            )

        self._prune_preconfirm_chains()
        self._prune_stale_histories(active_ids)
        return outputs

    def reset(self) -> None:
        """Clear all track state — call when switching cameras or starting a new clip."""
        self._byte_tracker.reset()
        self._histories.clear()
        self._last_seen_frame.clear()
        self._preconfirm_chains.clear()
        self._preconfirm_bboxes.clear()
        self._frame_index = 0

    # ------------------------------------------------------------------ #
    # Accessors
    # ------------------------------------------------------------------ #
    @property
    def camera_id(self) -> str:
        return self._camera_id

    @property
    def conf_threshold(self) -> float:
        return self._conf_threshold

    @property
    def nms_iou_threshold(self) -> float:
        return self._nms_iou_threshold

    @property
    def track_buffer(self) -> int:
        return self._track_buffer

    @property
    def history_length(self) -> int:
        return self._history_length

    @property
    def frame_index(self) -> int:
        """Number of :meth:`update` calls since construction / last :meth:`reset`."""
        return self._frame_index

    # ------------------------------------------------------------------ #
    # Internals
    # ------------------------------------------------------------------ #
    _PRECONFIRM_IOU = 0.25
    _PRECONFIRM_MAX_CHAINS = 32

    def _append_preconfirm(
        self,
        bbox: tuple[float, float, float, float],
        record: PositionRecord,
    ) -> None:
        best_idx = -1
        best_iou = 0.0
        for idx, last_bbox in enumerate(self._preconfirm_bboxes):
            iou = _bbox_iou(bbox, last_bbox)
            if iou > best_iou:
                best_iou = iou
                best_idx = idx
        if best_iou >= self._PRECONFIRM_IOU and best_idx >= 0:
            self._preconfirm_chains[best_idx].append(record)
            self._preconfirm_bboxes[best_idx] = bbox
            return
        if len(self._preconfirm_chains) >= self._PRECONFIRM_MAX_CHAINS:
            self._preconfirm_chains.pop(0)
            self._preconfirm_bboxes.pop(0)
        self._preconfirm_chains.append(deque([record], maxlen=self._history_length))
        self._preconfirm_bboxes.append(bbox)

    def _match_preconfirm_chain(
        self,
        bbox: tuple[float, float, float, float],
        used: set[int],
    ) -> int | None:
        best_idx = None
        best_iou = 0.0
        for idx, last_bbox in enumerate(self._preconfirm_bboxes):
            if idx in used:
                continue
            iou = _bbox_iou(bbox, last_bbox)
            if iou > best_iou:
                best_iou = iou
                best_idx = idx
        if best_idx is not None and best_iou >= self._PRECONFIRM_IOU:
            return best_idx
        return None

    def _prune_preconfirm_chains(self) -> None:
        max_chains = self._byte_tracker.minimum_consecutive_frames + 2
        if len(self._preconfirm_chains) <= max_chains:
            return
        drop = len(self._preconfirm_chains) - max_chains
        del self._preconfirm_chains[:drop]
        del self._preconfirm_bboxes[:drop]

    def _prune_stale_histories(self, active_ids: set[int] | None = None) -> None:
        """Drop position buffers for tracks gone longer than ``track_buffer`` frames."""
        active_ids = active_ids or set()
        stale = [
            tid
            for tid, last_frame in self._last_seen_frame.items()
            if tid not in active_ids
            and (self._frame_index - last_frame) > self._track_buffer
        ]
        for tid in stale:
            self._histories.pop(tid, None)
            self._last_seen_frame.pop(tid, None)
