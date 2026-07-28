"""Queue length sample aggregation (avg / max over time)."""

from __future__ import annotations


class QueueLengthAggregator:
    """Track average and peak queue length from periodic occupancy samples."""

    def __init__(self) -> None:
        self._samples: list[int] = []
        self._max_length = 0

    def reset(self) -> None:
        self._samples.clear()
        self._max_length = 0

    def sample(self, queue_length: int) -> None:
        length = max(0, int(queue_length))
        self._samples.append(length)
        if length > self._max_length:
            self._max_length = length

    @property
    def sample_count(self) -> int:
        return len(self._samples)

    @property
    def max_queue_length(self) -> int:
        return self._max_length

    def avg_queue_length(self) -> float:
        if not self._samples:
            return 0.0
        return sum(self._samples) / len(self._samples)
