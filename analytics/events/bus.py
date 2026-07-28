"""In-process event bus between producers and the Analytics Engine (MVP)."""

from __future__ import annotations

import queue
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import AnalyticsEvent

Subscriber = Callable[["AnalyticsEvent"], None]


class EventBus:
    """Thread-safe in-process queue with synchronous subscriber dispatch.

  For MVP this is ``queue.Queue`` plus immediate callback fan-out. Module 19
  replaces this with Kafka/RabbitMQ without changing the :class:`AnalyticsEvent`
  schema or producer call sites.
    """

    def __init__(self) -> None:
        self._queue: queue.Queue[AnalyticsEvent] = queue.Queue()
        self._subscribers: list[Subscriber] = []
        self._log: list[AnalyticsEvent] = []

    @property
    def event_log(self) -> tuple[AnalyticsEvent, ...]:
        """Every event published since construction (for tests / demos)."""
        return tuple(self._log)

    def subscribe(self, callback: Subscriber) -> None:
        """Register a consumer — typically the Analytics Engine."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Subscriber) -> None:
        self._subscribers.remove(callback)

    def publish(self, event: AnalyticsEvent) -> None:
        """Enqueue and synchronously notify all subscribers."""
        self._log.append(event)
        self._queue.put(event)
        for subscriber in list(self._subscribers):
            subscriber(event)

    def drain(self) -> list[AnalyticsEvent]:
        """Remove and return all queued events (does not re-notify subscribers)."""
        drained: list[AnalyticsEvent] = []
        while True:
            try:
                drained.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return drained

    def clear_log(self) -> None:
        """Reset the diagnostic event log."""
        self._log.clear()
