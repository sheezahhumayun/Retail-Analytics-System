"""Sampled PERSON_DETECTED publisher (PRD §31 — real-time only, not persisted)."""

from __future__ import annotations

import time

from inference.detection.types import Detection

from .adapters import person_detected_to_analytics
from .bus import EventBus


class PersonDetectionSampler:
    """Emit at most one PERSON_DETECTED event per interval per camera.

    Parameters
    ----------
    bus:
        Target event bus.
    camera_id:
        Camera to tag events with (must match detection ``camera_id``).
    sample_interval_seconds:
        Minimum wall-clock gap between published samples. Default ``1.0`` s.
    max_per_frame:
        When a sample fires, publish up to this many detections from the frame.
    """

    def __init__(
        self,
        bus: EventBus,
        camera_id: str,
        *,
        sample_interval_seconds: float = 1.0,
        max_per_frame: int = 3,
    ) -> None:
        self._bus = bus
        self._camera_id = camera_id
        self._interval = max(0.1, float(sample_interval_seconds))
        self._max_per_frame = max(1, int(max_per_frame))
        self._last_publish_at = 0.0
        self._sample_counter = 0

    @property
    def camera_id(self) -> str:
        return self._camera_id

    def maybe_publish(self, detections: list[Detection]) -> int:
        """Publish a sampled batch if the interval has elapsed.

        Returns the number of events published (0 if throttled).
        """
        if not detections:
            return 0

        now = time.monotonic()
        if now - self._last_publish_at < self._interval:
            return 0

        published = 0
        for det in detections[: self._max_per_frame]:
            if det.camera_id != self._camera_id:
                continue
            self._bus.publish(
                person_detected_to_analytics(det, sample_index=self._sample_counter)
            )
            self._sample_counter += 1
            published += 1

        if published:
            self._last_publish_at = now
        return published

    def reset(self) -> None:
        self._last_publish_at = 0.0
        self._sample_counter = 0
