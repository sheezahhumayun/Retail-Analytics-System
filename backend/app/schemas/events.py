"""Event schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    camera_id: str
    zone_id: str | None = None
    track_id: str | None = None
    event_type: str
    timestamp: str
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_")


class EventListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: str = Field(alias="from", serialization_alias="from")
    to: str
    count: int
    events: list[EventResponse]
