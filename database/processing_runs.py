"""Shared processing-run persistence helpers (backend + inference)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlmodel import Session, select

from .models import ProcessingRun
from .session import session_scope

logger = logging.getLogger(__name__)


def finalize_processing_run(
    run_id: str,
    *,
    status: str,
    message: str | None,
    preview_frame_path: str | None = None,
) -> None:
    """Mark a run terminal if it is still active (``running``)."""
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
            run.cancel_requested = False
            if preview_frame_path is not None:
                run.preview_frame_path = preview_frame_path
            session.add(run)
    except Exception:
        logger.exception("Failed to finalize processing run %s", run_id)


def is_processing_run_cancel_requested(run_id: str) -> bool:
    with session_scope() as session:
        run = session.get(ProcessingRun, run_id)
        if run is None:
            return True
        return bool(run.cancel_requested)


def request_processing_run_cancellation(
    session: Session,
    *,
    camera_ids: set[str],
    message: str,
) -> int:
    """Flag active runs for cooperative cancellation."""
    now = datetime.now(timezone.utc)
    rows = list(
        session.exec(
            select(ProcessingRun).where(
                ProcessingRun.camera_id.in_(camera_ids),  # type: ignore[attr-defined]
                ProcessingRun.status.in_(("pending", "running")),  # type: ignore[attr-defined]
            )
        ).all()
    )
    count = 0
    for run in rows:
        run.cancel_requested = True
        if run.status == "pending":
            run.status = "failed"
            run.finished_at = now
            run.message = message
            count += 1
        else:
            count += 1
        session.add(run)
    return count
