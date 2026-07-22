"""Shared pytest fixtures + config for the video ingestion tests.

Tests run against the real sample videos checked into ``sample-data/`` (Module 0)
using OpenCV in ``inference/.venv`` — no network, no downloads. Webcam and
real-RTSP tests are gated behind markers since there's no hardware here.
"""
from __future__ import annotations
from dotenv import load_dotenv

load_dotenv()
import os
import sys
from pathlib import Path

import pytest

# Make the ``inference`` package importable when tests run from the repo root.
# (inference/ is a namespace-ish package; we add its parent to sys.path.)
REPO_ROOT = Path(__file__).resolve().parent.parent
INFERENCE_PARENT = REPO_ROOT  # ``inference`` lives directly under repo root
if str(INFERENCE_PARENT) not in sys.path:
    sys.path.insert(0, str(INFERENCE_PARENT))

SAMPLE_DATA = REPO_ROOT / "sample-data"


# ---- Skip markers ---------------------------------------------------------- #
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with -m 'not slow')",
    )
    config.addinivalue_line(
        "markers",
        "webcam: requires a physical webcam (deselect with -m 'not webcam')",
    )
    config.addinivalue_line(
        "markers",
        "rtsp: requires a live RTSP stream (deselect with -m 'not rtsp')",
    )


# ---- Fixtures -------------------------------------------------------------- #
@pytest.fixture(scope="session")
def sample_data_dir() -> Path:
    if not SAMPLE_DATA.is_dir():
        pytest.skip(f"sample-data directory not found at {SAMPLE_DATA}")
    return SAMPLE_DATA


@pytest.fixture(scope="session")
def entrance_video(sample_data_dir: Path) -> Path:
    p = sample_data_dir / "entrance.mp4"
    if not p.exists():
        pytest.skip(f"{p} not present")
    return p


@pytest.fixture(scope="session")
def store_floor_video(sample_data_dir: Path) -> Path:
    p = sample_data_dir / "store-floor.mp4"
    if not p.exists():
        pytest.skip(f"{p} not present")
    return p


@pytest.fixture(scope="session")
def checkout_video(sample_data_dir: Path) -> Path:
    p = sample_data_dir / "checkout.mp4"
    if not p.exists():
        pytest.skip(f"{p} not present")
    return p


@pytest.fixture(scope="session")
def sample_videos(sample_data_dir: Path) -> list[Path]:
    """All available sample videos (used for parametrised sweeps)."""
    out = []
    for name in ("entrance.mp4", "store-floor.mp4", "checkout.mp4"):
        p = sample_data_dir / name
        if p.exists():
            out.append(p)
    if not out:
        pytest.skip("no sample videos present")
    return out
