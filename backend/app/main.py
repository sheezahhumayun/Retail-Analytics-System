"""FastAPI application entry point (Module 12, PRD §32)."""

from __future__ import annotations

import logging
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import POOL_SIZE, MAX_OVERFLOW, get_engine, log_pool_settings, session_scope
from .services.camera_health import (
    evaluate_camera_offline_duration_alerts,
    refresh_all_live_camera_statuses,
    refresh_all_recorded_camera_statuses,
)
from .services.camera_process import reconcile_orphaned_processing_runs

from .config import get_settings
from .exceptions import register_exception_handlers
from .routers import (
    alert_rules_admin,
    alerts,
    alerts_extended,
    analytics,
    auth,
    auth_me,
    cameras,
    cameras_extended,
    events,
    lines,
    organizations,
    organizations_admin,
    processing_runs,
    reports,
    stores,
    users,
    zones_config,
)

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=(
        "REST API for the Retail Analytics computer-vision platform. "
        "Serves store/camera configuration, aggregated analytics, events, and alerts "
        "from the Module 11 PostgreSQL schema. Authenticate via POST /api/auth/login "
        "then pass `Authorization: Bearer <token>` on protected routes."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

api = settings.api_prefix
app.include_router(auth.router, prefix=api)
app.include_router(auth_me.router, prefix=api)
app.include_router(organizations.router, prefix=api)
app.include_router(organizations_admin.router, prefix=api)
app.include_router(stores.router, prefix=api)
app.include_router(cameras.router, prefix=api)
app.include_router(cameras_extended.router, prefix=api)
app.include_router(processing_runs.router, prefix=api)
app.include_router(zones_config.router, prefix=api)
app.include_router(lines.router, prefix=api)
app.include_router(analytics.router, prefix=api)
app.include_router(events.router, prefix=api)
app.include_router(alerts.router, prefix=api)
app.include_router(alerts_extended.router, prefix=api)
app.include_router(alert_rules_admin.router, prefix=api)
app.include_router(reports.router, prefix=api)
app.include_router(users.router, prefix=api)


_health_logger = logging.getLogger("uvicorn.error")
_health_stop_event = threading.Event()
_health_thread: threading.Thread | None = None
_health_thread_lock = threading.Lock()


def _camera_health_worker(interval_seconds: int) -> None:
    """Background loop: probe live cameras and check recorded source files."""
    while not _health_stop_event.is_set():
        try:
            with session_scope() as session:
                live_count = refresh_all_live_camera_statuses(session)
                recorded_count = refresh_all_recorded_camera_statuses(session)
                alerts_created = evaluate_camera_offline_duration_alerts(session)
            _health_logger.info(
                "Camera health check updated %d live and %d recorded camera(s), "
                "created %d offline-duration alert(s)",
                live_count,
                recorded_count,
                alerts_created,
            )
        except Exception:
            _health_logger.exception("Camera health check failed")
        if _health_stop_event.wait(timeout=interval_seconds):
            break


def _start_camera_health_worker(interval_seconds: int) -> None:
    global _health_thread
    with _health_thread_lock:
        if interval_seconds <= 0 or _health_thread is not None:
            return
        _health_stop_event.clear()
        _health_thread = threading.Thread(
            target=_camera_health_worker,
            args=(interval_seconds,),
            name="camera-health",
            daemon=True,
        )
        _health_thread.start()
        _health_logger.info(
            "Camera health worker started (interval=%ds)", interval_seconds,
        )


def _stop_camera_health_worker() -> None:
    global _health_thread
    _health_stop_event.set()
    with _health_thread_lock:
        thread = _health_thread
        if thread is None:
            return
        thread.join(timeout=5)
        _health_thread = None


@app.on_event("startup")
def log_database_pool_settings() -> None:
    log_pool_settings(get_engine())
    reconciled = reconcile_orphaned_processing_runs()
    if reconciled:
        _health_logger.info(
            "Marked %d orphaned processing run(s) as failed after startup",
            reconciled,
        )
    _health_logger.info(
        "Database pool limits: up to %d concurrent connections per process "
        "(pool_size=%d + max_overflow=%d)",
        POOL_SIZE + MAX_OVERFLOW,
        POOL_SIZE,
        MAX_OVERFLOW,
    )
    _start_camera_health_worker(settings.camera_health_interval_seconds)


@app.on_event("shutdown")
def shutdown_camera_health_worker() -> None:
    _stop_camera_health_worker()


@app.get("/health", tags=["Health"], summary="Health check")
def health() -> dict[str, str]:
    return {"status": "ok"}
