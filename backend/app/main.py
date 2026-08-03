"""FastAPI application entry point (Module 12, PRD §32)."""

from __future__ import annotations

import logging
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import POOL_SIZE, MAX_OVERFLOW, get_engine, log_pool_settings, session_scope
from .services.camera_health import refresh_all_live_camera_statuses

from .config import get_settings
from .exceptions import register_exception_handlers
from .routers import (
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
app.include_router(stores.router, prefix=api)
app.include_router(cameras.router, prefix=api)
app.include_router(cameras_extended.router, prefix=api)
app.include_router(zones_config.router, prefix=api)
app.include_router(lines.router, prefix=api)
app.include_router(analytics.router, prefix=api)
app.include_router(events.router, prefix=api)
app.include_router(alerts.router, prefix=api)
app.include_router(alerts_extended.router, prefix=api)
app.include_router(reports.router, prefix=api)
app.include_router(users.router, prefix=api)


_health_logger = logging.getLogger("uvicorn.error")


def _camera_health_worker(interval_seconds: int) -> None:
    """Background loop: probe live cameras and persist status."""
    while True:
        try:
            with session_scope() as session:
                count = refresh_all_live_camera_statuses(session)
            _health_logger.info("Camera health check updated %d live camera(s)", count)
        except Exception:
            _health_logger.exception("Camera health check failed")
        time.sleep(interval_seconds)


@app.on_event("startup")
def log_database_pool_settings() -> None:
    log_pool_settings(get_engine())
    _health_logger.info(
        "Database pool limits: up to %d concurrent connections per process "
        "(pool_size=%d + max_overflow=%d)",
        POOL_SIZE + MAX_OVERFLOW,
        POOL_SIZE,
        MAX_OVERFLOW,
    )
    interval = settings.camera_health_interval_seconds
    if interval > 0:
        thread = threading.Thread(
            target=_camera_health_worker,
            args=(interval,),
            name="camera-health",
            daemon=True,
        )
        thread.start()
        _health_logger.info(
            "Camera health worker started (interval=%ds)", interval,
        )


@app.get("/health", tags=["Health"], summary="Health check")
def health() -> dict[str, str]:
    return {"status": "ok"}
