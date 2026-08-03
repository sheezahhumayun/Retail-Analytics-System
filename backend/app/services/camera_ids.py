"""Server-side camera id allocation."""

from __future__ import annotations

import re
import uuid

from sqlmodel import Session

from database.models import Camera

_SLUG_RE = re.compile(r"[^a-zA-Z0-9]+")
_MAX_ID_LEN = 64


def _name_slug(name: str, max_len: int = 24) -> str:
    slug = _SLUG_RE.sub("_", name.strip().lower()).strip("_")
    if not slug:
        return "camera"
    return slug[:max_len]


def generate_camera_id(session: Session, name: str) -> str:
    """Allocate a unique camera id (`cam_{name_slug}_{suffix}`)."""
    slug = _name_slug(name)
    for _ in range(12):
        suffix = uuid.uuid4().hex[:6]
        candidate = f"cam_{slug}_{suffix}"
        if len(candidate) > _MAX_ID_LEN:
            candidate = f"cam_{uuid.uuid4().hex[:8]}"
        if session.get(Camera, candidate) is None:
            return candidate
    return f"cam_{uuid.uuid4().hex[:12]}"
