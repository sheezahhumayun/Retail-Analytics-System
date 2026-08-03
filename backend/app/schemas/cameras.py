"""Camera schemas."""



from __future__ import annotations



import re

from typing import Literal



from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator





RTSP_PATTERN = re.compile(r"^(rtsp|rtmp|http|https|file)://", re.IGNORECASE)

FILE_PATH_PATTERN = re.compile(r"^[a-zA-Z0-9_./\\-]+$")



SourceType = Literal["live", "recorded"]





class CameraResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)



    id: str

    store_id: str

    name: str

    location: str | None = None

    rtsp_url: str | None = None

    source_type: SourceType = "live"

    last_processed_at: str | None = None

    camera_type: str = "fixed"

    resolution: str | None = None

    fps: float | None = None

    status: str = "offline"





class CameraCreate(BaseModel):

    """Create payload — camera `id` is assigned by the server on POST /api/cameras."""



    store_id: str = Field(..., min_length=1, max_length=64)

    name: str = Field(..., min_length=1, max_length=255)

    location: str | None = Field(default=None, max_length=255)

    rtsp_url: str | None = Field(

        default=None,

        max_length=1024,

        description="Live: RTSP/HTTP stream URL. Recorded: local video file path (reuses this field).",

    )

    source_type: SourceType = Field(

        default="live",

        description="`live` = RTSP/webcam stream; `recorded` = video file processed on demand",

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



    @model_validator(mode="after")

    def validate_source_fields(self) -> CameraCreate:

        if self.source_type == "live":

            if not self.rtsp_url:

                raise ValueError("rtsp_url is required for live stream cameras")

            if self.rtsp_url and FILE_PATH_PATTERN.match(self.rtsp_url) and not RTSP_PATTERN.match(

                self.rtsp_url

            ):

                raise ValueError(

                    "live cameras require a stream URL (rtsp://, http://, …), not a file path"

                )

        elif self.source_type == "recorded":

            if not self.rtsp_url:

                raise ValueError("video file path is required for recorded cameras")

            if self.rtsp_url and RTSP_PATTERN.match(self.rtsp_url):

                raise ValueError(

                    "recorded cameras require a local video file path, not a stream URL"

                )

        return self





class CameraStatusResponse(BaseModel):

    id: str

    name: str

    store_id: str

    source_type: SourceType = "live"

    status: str = Field(description="online | offline | error")

    last_seen: str | None = Field(

        default=None,

        description="ISO timestamp of most recent analytics event, if any",

    )

    current_occupancy: int | None = Field(

        default=None,

        description="Latest occupancy reading for this camera",

    )

    processed: bool | None = Field(

        default=None,

        description="For recorded cameras: whether the video has been processed at least once",

    )

    last_processed_at: str | None = Field(

        default=None,

        description="For recorded cameras: ISO timestamp of last successful processing run",

    )





class CameraProcessResponse(BaseModel):

    camera_id: str

    status: Literal["running", "completed", "failed", "idle"]

    message: str | None = None

    started_at: str | None = None

    finished_at: str | None = None


