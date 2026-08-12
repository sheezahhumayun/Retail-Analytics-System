"""Process-wide lock for OpenCV/FFmpeg I/O (decode/open/release)."""

from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Iterator

_lock = threading.Lock()


@contextmanager
def opencv_io() -> Iterator[None]:
    """Serialize all OpenCV/FFmpeg capture open, read, and release calls."""
    with _lock:
        yield
