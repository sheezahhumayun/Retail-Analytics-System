"""FastAPI application entry point (Module 12, PRD §32)."""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.session import POOL_SIZE, MAX_OVERFLOW, get_engine, log_pool_settings

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


@app.on_event("startup")
def log_database_pool_settings() -> None:
    log_pool_settings(get_engine())
    startup_logger = logging.getLogger("uvicorn.error")
    startup_logger.info(
        "Database pool limits: up to %d concurrent connections per process "
        "(pool_size=%d + max_overflow=%d)",
        POOL_SIZE + MAX_OVERFLOW,
        POOL_SIZE,
        MAX_OVERFLOW,
    )


@app.get("/health", tags=["Health"], summary="Health check")
def health() -> dict[str, str]:
    return {"status": "ok"}
