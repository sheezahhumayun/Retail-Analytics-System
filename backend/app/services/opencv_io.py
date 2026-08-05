"""Process-wide lock for OpenCV/FFmpeg I/O (decode/open/release).

FFmpeg's libavcodec frame decoder is not safe for concurrent use across
threads in the same process. The MJPEG preview loop (``asyncio.to_thread``)
and the background camera-health worker can otherwise call
``cv2.VideoCapture`` / :class:`VideoSource` at the same time and trigger
native crashes (e.g. ``fctx->async_lock`` assertion failures).
"""

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
