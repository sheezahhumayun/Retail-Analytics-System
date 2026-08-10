"""Backend configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Retail Analytics API"
    api_prefix: str = "/api"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 8
    api_default_password: str = "demo"
    heatmap_data_dir: str = str(REPO_ROOT / "data" / "heatmaps")
    store_timezone: str = "UTC"
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    camera_health_interval_seconds: int = 120
    live_analytics_reconcile_interval_seconds: int = 30


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
