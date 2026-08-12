"""Recorded-video processing jobs (Postgres-backed run history)."""

from __future__ import annotations

import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database.models import Camera, CountingLine, ProcessingRun, Zone
from database.session import session_scope

from .org_scope import cameras_for_org_stmt

REPO_ROOT = Path(__file__).resolve().parents[3]

PID_FILE = REPO_ROOT / "data" / "run" / "live_analytics_worker.pid"
LOCK_FILE = REPO_ROOT / "data" / "run" / "live_analytics_worker.lock"
LIVE_ANALYTICS_WORKER_CMD = "inference.pipeline.live_analytics_worker"
_LOCK_RETRY_INTERVAL_SECONDS = 0.2
_LOCK_TIMEOUT_SECONDS = 2.0

logger = logging.getLogger(__name__)

_processing_workers: dict[str, threading.Thread] = {}
_processing_procs: dict[str, subprocess.Popen[str]] = {}
_workers_lock = threading.Lock()


class ProcessJobState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingRunActiveError(Exception):
    """Another processing run is already active for this camera."""


RESTART_INTERRUPT_MESSAGE = "interrupted by server restart"
ORG_DISABLE_CANCEL_MESSAGE = "Cancelled: organization disabled"


@dataclass
class ProcessJob:
    camera_id: str
    run_id: str | None = None
    state: ProcessJobState = ProcessJobState.IDLE
    started_at: datetime | None = None
    finished_at: datetime | None = None
    message: str | None = None


def _inference_python() -> Path:
    win = REPO_ROOT / "inference" / ".venv" / "Scripts" / "python.exe"
    if win.is_file():
        return win
    unix = REPO_ROOT / "inference" / ".venv" / "bin" / "python"
    if unix.is_file():
        return unix
    return Path(sys.executable)


def _zone_snapshot_rows(zones: list[Zone]) -> list[dict[str, object]]:
    return [
        {
            "id": zone.id,
            "name": zone.name,
            "zone_type": zone.zone_type,
            "polygon_coords": zone.polygon_coords,
        }
        for zone in zones
    ]


def _line_snapshot_rows(lines: list[CountingLine]) -> list[dict[str, object]]:
    return [
        {
            "id": line.id,
            "name": line.name,
            "point_a": line.point_a,
            "point_b": line.point_b,
            "direction": line.direction,
        }
        for line in lines
    ]


def reconcile_orphaned_processing_runs() -> int:
    """Mark stale ``running`` rows as failed — no worker survives a process restart."""
    now = datetime.now(timezone.utc)
    count = 0
    with session_scope() as session:
        rows = list(
            session.exec(
                select(ProcessingRun).where(ProcessingRun.status == "running")
            ).all()
        )
        for run in rows:
            run.status = "failed"
            run.finished_at = now
            run.message = RESTART_INTERRUPT_MESSAGE
            session.add(run)
            count += 1
    if count:
        logger.info("Reconciled %d orphaned processing run(s) after startup", count)
    return count


def claim_processing_run(camera_id: str) -> str:
    """Insert a running processing_run row; return run id or raise if one is active."""
    run_id = f"run_{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    try:
        with session_scope() as session:
            camera = session.get(Camera, camera_id)
            if camera is None:
                raise ValueError(f"Camera '{camera_id}' not found")
            if not camera.rtsp_url:
                raise ValueError(f"Camera '{camera_id}' has no video path configured")

            zones = list(
                session.exec(
                    select(Zone).where(
                        Zone.camera_id == camera_id,
                        Zone.status != "disabled",
                    )
                ).all()
            )
            lines = list(
                session.exec(
                    select(CountingLine).where(
                        CountingLine.camera_id == camera_id,
                        CountingLine.status != "disabled",
                    )
                ).all()
            )

            run = ProcessingRun(
                id=run_id,
                camera_id=camera_id,
                status="running",
                started_at=now,
                finished_at=None,
                message="Processing video…",
                source_path=camera.rtsp_url,
                zones_snapshot=_zone_snapshot_rows(zones),
                lines_snapshot=_line_snapshot_rows(lines),
            )
            session.add(run)
            session.flush()
    except IntegrityError as exc:
        raise ProcessingRunActiveError() from exc
    return run_id


def _finish_run(
    run_id: str,
    *,
    status: str,
    message: str | None,
    preview_frame_path: str | None = None,
) -> None:
    finished_at = datetime.now(timezone.utc)
    try:
        with session_scope() as session:
            run = session.get(ProcessingRun, run_id)
            if run is None:
                return
            if run.status != "running":
                return
            run.status = status
            run.finished_at = finished_at
            run.message = message
            if preview_frame_path is not None:
                run.preview_frame_path = preview_frame_path
            session.add(run)
    except Exception:
        logger.exception("Failed to finalize processing run %s", run_id)


def _unregister_worker(camera_id: str, thread: threading.Thread) -> None:
    with _workers_lock:
        current = _processing_workers.get(camera_id)
        if current is thread:
            _processing_workers.pop(camera_id, None)
            _processing_procs.pop(camera_id, None)


def join_processing_worker(camera_id: str, *, timeout: float | None = None) -> None:
    """Block until the in-process worker for ``camera_id`` exits (tests / shutdown hooks)."""
    with _workers_lock:
        thread = _processing_workers.get(camera_id)
    if thread is not None and thread.is_alive():
        thread.join(timeout=timeout)


def _parse_subprocess_result(stdout: str) -> str | None:
    """Extract ``preview_frame_path`` from the JSON line printed by process_recorded."""
    for line in reversed(stdout.strip().splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            path = payload.get("preview_frame_path")
            if isinstance(path, str) and path:
                return path
    return None


def _terminate_proc(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    try:
        proc.terminate()
    except OSError:
        return
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
        except OSError:
            return
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


_live_analytics_shutdown_requested = False


def _acquire_cleanup_lock() -> int | None:
    deadline = time.monotonic() + _LOCK_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        try:
            return os.open(str(LOCK_FILE), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            time.sleep(_LOCK_RETRY_INTERVAL_SECONDS)
    return None


def _release_cleanup_lock(lock_fd: int | None) -> None:
    if lock_fd is not None:
        try:
            os.close(lock_fd)
        except OSError:
            pass
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def _is_process_alive(pid: int) -> bool:
    if sys.platform == "win32":
        check = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            check=False,
        )
        return str(pid) in check.stdout and "No tasks" not in check.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _process_command_line(pid: int) -> str | None:
    if sys.platform == "win32":
        result = subprocess.run(
            ["wmic", "process", "where", f"ProcessId={pid}", "get", "CommandLine"],
            capture_output=True,
            text=True,
            check=False,
        )
        lines = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip() and line.strip() != "CommandLine"
        ]
        return lines[0] if lines else None
    try:
        raw = Path(f"/proc/{pid}/cmdline").read_bytes()
    except OSError:
        return None
    return raw.replace(b"\x00", b" ").decode("utf-8", errors="replace").strip()


def _terminate_external_pid(pid: int) -> None:
    if not _is_process_alive(pid):
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T"],
                capture_output=True,
                check=False,
            )
        return
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if not _is_process_alive(pid):
            return
        time.sleep(0.1)
    try:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/T", "/F"],
                capture_output=True,
                check=False,
            )
        else:
            os.kill(pid, signal.SIGKILL)
    except OSError:
        pass


def _remove_live_analytics_pid_file() -> None:
    try:
        PID_FILE.unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("Failed to remove live analytics PID file %s: %s", PID_FILE, exc)


def _cleanup_stale_live_analytics_worker() -> None:
    try:
        LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
        lock_fd: int | None = None
        try:
            lock_fd = _acquire_cleanup_lock()
            if lock_fd is None:
                logger.warning(
                    "Could not acquire live analytics cleanup lock at %s within %.1fs; "
                    "skipping stale worker cleanup",
                    LOCK_FILE,
                    _LOCK_TIMEOUT_SECONDS,
                )
                return

            if not PID_FILE.is_file():
                return

            try:
                pid = int(PID_FILE.read_text(encoding="utf-8").strip())
            except (OSError, ValueError) as exc:
                logger.warning(
                    "Ignoring corrupt live analytics PID file %s: %s",
                    PID_FILE,
                    exc,
                )
                _remove_live_analytics_pid_file()
                return

            alive = _is_process_alive(pid)
            cmdline = _process_command_line(pid) if alive else None
            matches = (
                alive
                and cmdline is not None
                and LIVE_ANALYTICS_WORKER_CMD in cmdline
            )

            if matches:
                logger.info(
                    "Cleaning up stale live analytics worker (pid=%s, cmdline=%r)",
                    pid,
                    cmdline,
                )
                _terminate_external_pid(pid)
                if _is_process_alive(pid):
                    logger.warning(
                        "Stale live analytics worker pid=%s may still be running "
                        "after termination attempt",
                        pid,
                    )
                else:
                    logger.info(
                        "Terminated stale live analytics worker pid=%s "
                        "(verified cmdline contained %r)",
                        pid,
                        LIVE_ANALYTICS_WORKER_CMD,
                    )
            elif alive:
                logger.info(
                    "Live analytics PID file referenced pid=%s but cmdline did not match "
                    "%r (%r); not killing",
                    pid,
                    LIVE_ANALYTICS_WORKER_CMD,
                    cmdline,
                )
            else:
                logger.info(
                    "Live analytics PID file referenced stale pid=%s "
                    "(process not running); removing PID file",
                    pid,
                )

            _remove_live_analytics_pid_file()
        finally:
            _release_cleanup_lock(lock_fd)
    except Exception:
        logger.warning("Stale live analytics worker cleanup failed", exc_info=True)


def start_live_analytics_subprocess(
    reconcile_interval_seconds: int,
) -> subprocess.Popen[str]:
    """Launch the continuous live-analytics worker in the inference venv."""
    global _live_analytics_shutdown_requested
    _live_analytics_shutdown_requested = False

    _cleanup_stale_live_analytics_worker()

    python = _inference_python()
    proc = subprocess.Popen(
        [
            str(python),
            "-m",
            "inference.pipeline.live_analytics_worker",
            "--reconcile-interval",
            str(reconcile_interval_seconds),
        ],
        cwd=str(REPO_ROOT),
    )
    logger.info(
        "Started live analytics worker subprocess (pid=%s, python=%s)",
        proc.pid,
        python,
    )

    try:
        PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        PID_FILE.write_text(f"{proc.pid}\n", encoding="utf-8")
    except OSError as exc:
        logger.warning("Failed to write live analytics PID file %s: %s", PID_FILE, exc)

    def _watch() -> None:
        code = proc.wait()
        if not _live_analytics_shutdown_requested:
            logger.error(
                "Live analytics worker subprocess exited unexpectedly (code=%s)",
                code,
            )

    threading.Thread(
        target=_watch,
        daemon=True,
        name="live-analytics-watchdog",
    ).start()
    return proc


def stop_live_analytics_subprocess(proc: subprocess.Popen[str] | None) -> None:
    """Terminate the live-analytics worker subprocess."""
    global _live_analytics_shutdown_requested
    if proc is None:
        return
    _live_analytics_shutdown_requested = True
    _terminate_proc(proc)
    _remove_live_analytics_pid_file()


def kill_processing_runs_for_org(org_id: str) -> int:
    """Terminate in-flight recorded-video workers for ``org_id`` and mark runs failed."""
    with session_scope() as session:
        org_camera_ids = {
            camera.id for camera in session.exec(cameras_for_org_stmt(org_id)).all()
        }

    with _workers_lock:
        targets = [
            (camera_id, proc)
            for camera_id, proc in list(_processing_procs.items())
            if camera_id in org_camera_ids
        ]

    if not targets:
        return 0

    now = datetime.now(timezone.utc)
    killed = 0
    with session_scope() as session:
        for camera_id, proc in targets:
            try:
                _terminate_proc(proc)
                run = session.exec(
                    select(ProcessingRun).where(
                        ProcessingRun.camera_id == camera_id,
                        ProcessingRun.status == "running",
                    )
                ).first()
                if run is not None:
                    run.status = "failed"
                    run.finished_at = now
                    run.message = ORG_DISABLE_CANCEL_MESSAGE
                    session.add(run)
                    killed += 1
            except Exception:
                logger.exception(
                    "Failed to cancel processing run for camera %s in org %s",
                    camera_id,
                    org_id,
                )

    if killed:
        logger.info(
            "Cancelled %d processing run(s) for disabled organization %s",
            killed,
            org_id,
        )
    return killed


def _run_subprocess(
    run_id: str,
    camera_id: str,
    recording_start: str | None = None,
) -> None:
    python = _inference_python()
    status = "failed"
    message = "Processing failed"
    preview_frame_path: str | None = None
    proc: subprocess.Popen[str] | None = None
    try:
        cmd = [
            str(python),
            "-m",
            "inference.pipeline.process_recorded",
            "--camera-id",
            camera_id,
            "--run-id",
            run_id,
        ]
        if recording_start is not None:
            cmd.extend(["--recording-start", recording_start])
        proc = subprocess.Popen(
            cmd,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        with _workers_lock:
            _processing_procs[camera_id] = proc
        try:
            stdout, stderr = proc.communicate(timeout=3600)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate()
            message = "Processing timed out after 1 hour"
        else:
            if proc.returncode != 0:
                stderr_text = (stderr or stdout or "Processing failed").strip()
                message = stderr_text[-2000:]
            else:
                status = "completed"
                message = "Video processed successfully"
                preview_frame_path = _parse_subprocess_result(stdout or "")
    except Exception as exc:
        message = str(exc)
    finally:
        _finish_run(
            run_id,
            status=status,
            message=message,
            preview_frame_path=preview_frame_path,
        )
        current_thread = threading.current_thread()
        _unregister_worker(camera_id, current_thread)


def start_recorded_processing(
    camera_id: str,
    *,
    recording_start: str | None = None,
) -> str:
    """Claim a DB run row, then spawn the background subprocess thread."""
    run_id = claim_processing_run(camera_id)
    thread = threading.Thread(
        target=_run_subprocess,
        args=(run_id, camera_id, recording_start),
        name=f"process-camera-{camera_id}",
        daemon=True,
    )
    with _workers_lock:
        _processing_workers[camera_id] = thread
    thread.start()
    return run_id


def get_latest_processing_run(session: Session, camera_id: str) -> ProcessingRun | None:
    return session.exec(
        select(ProcessingRun)
        .where(ProcessingRun.camera_id == camera_id)
        .order_by(ProcessingRun.started_at.desc())  # type: ignore[attr-defined]
    ).first()


def get_latest_completed_processing_run(
    session: Session,
    camera_id: str,
) -> ProcessingRun | None:
    """Most recent completed run for snapshot lookup (recorded cameras)."""
    return session.exec(
        select(ProcessingRun)
        .where(
            ProcessingRun.camera_id == camera_id,
            ProcessingRun.status == "completed",
        )
        .order_by(ProcessingRun.started_at.desc())  # type: ignore[attr-defined]
    ).first()


def get_process_job(session: Session, camera_id: str) -> ProcessJob:
    run = get_latest_processing_run(session, camera_id)
    if run is None:
        return ProcessJob(camera_id=camera_id)
    try:
        state = ProcessJobState(run.status)
    except ValueError:
        state = ProcessJobState.FAILED
    return ProcessJob(
        camera_id=camera_id,
        run_id=run.id,
        state=state,
        started_at=run.started_at,
        finished_at=run.finished_at,
        message=run.message,
    )
