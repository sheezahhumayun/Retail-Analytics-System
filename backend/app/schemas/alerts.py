"""Alert schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    alert_type: str
    camera_id: str | None = None
    zone_id: str | None = None
    timestamp: str
    severity: str
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_")


class AlertListResponse(BaseModel):
    count: int
    alerts: list[AlertResponse]
