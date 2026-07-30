"""FastAPI application entry point (Module 12, PRD §32)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .exceptions import register_exception_handlers
from .routers import alerts, analytics, auth, cameras, events, stores

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
app.include_router(stores.router, prefix=api)
app.include_router(cameras.router, prefix=api)
app.include_router(analytics.router, prefix=api)
app.include_router(events.router, prefix=api)
app.include_router(alerts.router, prefix=api)


@app.get("/health", tags=["Health"], summary="Health check")
def health() -> dict[str, str]:
    return {"status": "ok"}
