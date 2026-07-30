"""Extended camera schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from ..cameras import CameraCreate


class CameraUpdate(BaseModel):
    """Same mutable fields as POST /api/cameras (id comes from path)."""

    store_id: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    rtsp_url: str | None = Field(default=None, max_length=1024)
    camera_type: Literal["fixed", "ptz", "fisheye"] | None = None
    resolution: str | None = Field(default=None, pattern=r"^\d+x\d+$")
    fps: float | None = Field(default=None, gt=0, le=120)

    @field_validator("rtsp_url")
    @classmethod
    def validate_rtsp_url(cls, value: str | None) -> str | None:
        return CameraCreate.validate_rtsp_url(value)


class CameraTestResponse(BaseModel):
    status: Literal["success", "error"]
    latency_ms: int | None = None
    resolution: str | None = None
    fps: float | None = None
    message: str | None = None
