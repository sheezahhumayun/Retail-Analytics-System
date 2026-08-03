"""Recorded-video processing jobs (background subprocess, in-process status)."""

from __future__ import annotations

import subprocess
import sys
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]


class ProcessJobState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessJob:
    camera_id: str
    state: ProcessJobState = ProcessJobState.IDLE
    started_at: datetime | None = None
    finished_at: datetime | None = None
    message: str | None = None
    result: dict[str, Any] = field(default_factory=dict)


_lock = threading.Lock()
_jobs: dict[str, ProcessJob] = {}


def _inference_python() -> Path:
    win = REPO_ROOT / "inference" / ".venv" / "Scripts" / "python.exe"
    if win.is_file():
        return win
    unix = REPO_ROOT / "inference" / ".venv" / "bin" / "python"
    if unix.is_file():
        return unix
    return Path(sys.executable)


def get_process_job(camera_id: str) -> ProcessJob:
    with _lock:
        return _jobs.get(camera_id, ProcessJob(camera_id=camera_id))


def _set_job(camera_id: str, **kwargs: object) -> ProcessJob:
    with _lock:
        job = _jobs.setdefault(camera_id, ProcessJob(camera_id=camera_id))
        for key, value in kwargs.items():
            setattr(job, key, value)
        return job


def _run_subprocess(camera_id: str) -> None:
    python = _inference_python()
    try:
        completed = subprocess.run(
            [
                str(python),
                "-m",
                "inference.pipeline.process_recorded",
                "--camera-id",
                camera_id,
            ],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=3600,
            check=False,
        )
        if completed.returncode != 0:
            stderr = (completed.stderr or completed.stdout or "Processing failed").strip()
            _set_job(
                camera_id,
                state=ProcessJobState.FAILED,
                finished_at=datetime.now(timezone.utc),
                message=stderr[-2000:],
            )
            return
        _set_job(
            camera_id,
            state=ProcessJobState.COMPLETED,
            finished_at=datetime.now(timezone.utc),
            message="Video processed successfully",
            result={"stdout": (completed.stdout or "").strip()[-500:]},
        )
    except subprocess.TimeoutExpired:
        _set_job(
            camera_id,
            state=ProcessJobState.FAILED,
            finished_at=datetime.now(timezone.utc),
            message="Processing timed out after 1 hour",
        )
    except Exception as exc:
        _set_job(
            camera_id,
            state=ProcessJobState.FAILED,
            finished_at=datetime.now(timezone.utc),
            message=str(exc),
        )


def start_recorded_processing(camera_id: str) -> ProcessJob:
    """Start background processing if not already running."""
    with _lock:
        existing = _jobs.get(camera_id)
        if existing is not None and existing.state == ProcessJobState.RUNNING:
            return existing

    job = _set_job(
        camera_id,
        state=ProcessJobState.RUNNING,
        started_at=datetime.now(timezone.utc),
        finished_at=None,
        message="Processing video…",
        result={},
    )
    thread = threading.Thread(
        target=_run_subprocess,
        args=(camera_id,),
        name=f"process-camera-{camera_id}",
        daemon=True,
    )
    thread.start()
    return job
