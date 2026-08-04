"""Extended camera schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from analytics.modules import ALL_ANALYTICS_MODULES, normalize_modules

from ..cameras import FILE_PATH_PATTERN, RTSP_PATTERN, CameraCreate, SourceType


class CameraUpdate(BaseModel):
    """Same mutable fields as POST /api/cameras (id comes from path)."""

    store_id: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    rtsp_url: str | None = Field(default=None, max_length=1024)
    source_type: SourceType | None = None
    camera_type: Literal["fixed", "ptz", "fisheye"] | None = None
    resolution: str | None = Field(default=None, pattern=r"^\d+x\d+$")
    fps: float | None = Field(default=None, gt=0, le=120)

    status: Literal["offline", "disabled"] | None = Field(
        default=None,
        description=(
            "Manual admin enable/disable switch. `disabled` soft-disables the "
            "camera (skips health probes, excluded from default camera lists); "
            "`offline` re-enables it (the next health check cycle will refresh it "
            "to `online`/`error`). `online`/`error` are probe-derived and can't "
            "be set directly."
        ),
    )

    analytics_modules: list[str] | None = Field(
        default=None,
        description="Replace assigned analytics modules for this camera",
    )

    @field_validator("analytics_modules")
    @classmethod
    def validate_analytics_modules(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        unknown = sorted({m for m in value if m not in ALL_ANALYTICS_MODULES})
        if unknown:
            raise ValueError(
                f"Unknown analytics module(s): {', '.join(unknown)}. "
                f"Allowed: {', '.join(sorted(ALL_ANALYTICS_MODULES))}"
            )
        return normalize_modules(value)

    @field_validator("rtsp_url")
    @classmethod
    def validate_rtsp_url(cls, value: str | None) -> str | None:
        return CameraCreate.validate_rtsp_url(value)

    @model_validator(mode="after")
    def validate_source_fields(self) -> CameraUpdate:
        if self.source_type == "live" and self.rtsp_url:
            if FILE_PATH_PATTERN.match(self.rtsp_url) and not RTSP_PATTERN.match(self.rtsp_url):
                raise ValueError(
                    "live cameras require a stream URL (rtsp://, http://, …), not a file path"
                )
        if self.source_type == "recorded" and self.rtsp_url:
            if RTSP_PATTERN.match(self.rtsp_url):
                raise ValueError(
                    "recorded cameras require a local video file path, not a stream URL"
                )
        return self


class CameraTestResponse(BaseModel):
    status: Literal["success", "error"]
    latency_ms: int | None = None
    resolution: str | None = None
    fps: float | None = None
    message: str | None = None
    camera_status: Literal["online", "offline", "error", "disabled", "processing"] | None = Field(
        default=None,
        description="Persisted camera status after this probe (live cameras only).",
    )
