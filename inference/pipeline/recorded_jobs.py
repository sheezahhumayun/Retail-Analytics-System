"""Poll Postgres for pending recorded-video jobs and execute them in-process."""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone

from sqlmodel import select

from database.models import ProcessingRun
from database.processing_runs import (
    finalize_processing_run,
    is_processing_run_cancel_requested,
)
from database.session import session_scope

from inference.pipeline.process_recorded import (
    ProcessingCancelledError,
    process_recorded_camera,
)

logger = logging.getLogger(__name__)

_active_lock = threading.Lock()
_active_threads: dict[str, threading.Thread] = {}

ORG_DISABLE_CANCEL_MESSAGE = "Cancelled: organization disabled"


def _claim_next_pending_run() -> ProcessingRun | None:
    with session_scope() as session:
        pending = session.exec(
            select(ProcessingRun)
            .where(ProcessingRun.status == "pending")
            .order_by(ProcessingRun.started_at)  # type: ignore[attr-defined]
            .with_for_update(skip_locked=True)
            .limit(1)
        ).first()
        if pending is None:
            return None
        if pending.cancel_requested:
            pending.status = "failed"
            pending.finished_at = datetime.now(timezone.utc)
            pending.message = ORG_DISABLE_CANCEL_MESSAGE
            pending.cancel_requested = False
            session.add(pending)
            session.flush()
            session.refresh(pending)
            session.expunge(pending)
            return None

        pending.status = "running"
        pending.message = "Processing video…"
        session.add(pending)
        session.flush()
        session.refresh(pending)
        session.expunge(pending)
        return pending


def _execute_run(run: ProcessingRun) -> None:
    run_id = run.id
    camera_id = run.camera_id
    status = "failed"
    message = "Processing failed"
    preview_frame_path: str | None = None
    try:
        explicit_recording_start = run.recording_start is not None
        recording_start = None
        if run.recording_start is not None:
            from inference.pipeline.process_recorded import _parse_recording_start

            recording_start = _parse_recording_start(run.recording_start)

        result = process_recorded_camera(
            camera_id,
            run_id=run_id,
            recording_start=recording_start,
            explicit_recording_start=explicit_recording_start,
            cancel_check=lambda: is_processing_run_cancel_requested(run_id),
        )
        status = "completed"
        message = "Video processed successfully"
        preview_path = result.get("preview_frame_path")
        if isinstance(preview_path, str) and preview_path:
            preview_frame_path = preview_path
    except ProcessingCancelledError as exc:
        message = str(exc)
    except Exception as exc:
        logger.exception("Recorded processing failed for run %s", run_id)
        message = str(exc)[-2000:]
    finally:
        finalize_processing_run(
            run_id,
            status=status,
            message=message,
            preview_frame_path=preview_frame_path,
        )
        with _active_lock:
            current = _active_threads.get(camera_id)
            if current is threading.current_thread():
                _active_threads.pop(camera_id, None)


def _start_run_thread(run: ProcessingRun) -> bool:
    with _active_lock:
        existing = _active_threads.get(run.camera_id)
        if existing is not None and existing.is_alive():
            return False
        thread = threading.Thread(
            target=_execute_run,
            args=(run,),
            name=f"recorded-job-{run.id}",
            daemon=True,
        )
        _active_threads[run.camera_id] = thread
    thread.start()
    return True


def poll_recorded_jobs() -> int:
    """Claim pending runs and start in-process workers. Returns jobs started."""
    started = 0
    while True:
        run = _claim_next_pending_run()
        if run is None:
            break
        if _start_run_thread(run):
            started += 1
            logger.info("Started recorded processing run %s for camera %s", run.id, run.camera_id)
        else:
            with session_scope() as session:
                db_run = session.get(ProcessingRun, run.id)
                if db_run is not None and db_run.status == "running":
                    db_run.status = "pending"
                    db_run.message = "Queued for processing…"
                    session.add(db_run)
    return started


def get_active_recorded_job_threads() -> list[str]:
    with _active_lock:
        return [name for name, thread in _active_threads.items() if thread.is_alive()]
