"""Camera schemas."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


RTSP_PATTERN = re.compile(r"^(rtsp|rtmp|http|https|file)://", re.IGNORECASE)
FILE_PATH_PATTERN = re.compile(r"^[a-zA-Z0-9_./\\-]+$")


class CameraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    store_id: str
    name: str
    location: str | None = None
    rtsp_url: str | None = None
    camera_type: str = "fixed"
    resolution: str | None = None
    fps: float | None = None
    status: str = "offline"


class CameraCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    store_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    location: str | None = Field(default=None, max_length=255)
    rtsp_url: str | None = Field(
        default=None,
        max_length=1024,
        description="RTSP/HTTP stream URL or local sample-data path",
    )
    camera_type: Literal["fixed", "ptz", "fisheye"] = "fixed"
    resolution: str | None = Field(default=None, pattern=r"^\d+x\d+$")
    fps: float | None = Field(default=None, gt=0, le=120)

    @field_validator("rtsp_url")
    @classmethod
    def validate_rtsp_url(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        if RTSP_PATTERN.match(value):
            return value
        if FILE_PATH_PATTERN.match(value):
            return value
        raise ValueError(
            "rtsp_url must be a valid stream URL (rtsp://, http://, …) "
            "or a local file path (e.g. sample-data/town.mp4)"
        )


class CameraStatusResponse(BaseModel):
    id: str
    name: str
    store_id: str
    status: str = Field(description="online | offline | error")
    last_seen: str | None = Field(
        default=None,
        description="ISO timestamp of most recent analytics event, if any",
    )
    current_occupancy: int | None = Field(
        default=None,
        description="Latest occupancy reading for this camera",
    )
