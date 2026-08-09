"""Resolve repo-relative local media paths (recorded videos)."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_local_media_path(url: str) -> Path:
    """Resolve a local video path the same way as recorded-video processing."""
    path = Path(url)
    if path.is_file():
        return path
    candidate = REPO_ROOT / url
    if candidate.is_file():
        return candidate
    return candidate if candidate.exists() else path


def resolve_repo_data_path(relative_path: str) -> Path:
    """Resolve a repo-relative data file (e.g. ``data/frame-previews/...``)."""
    path = Path(relative_path)
    if path.is_file():
        return path
    candidate = REPO_ROOT / relative_path
    return candidate
