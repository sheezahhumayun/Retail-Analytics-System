"""Zone geometry schemas (zone_shapes table)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ZoneShapeType = Literal["entrance", "checkout_queue", "general"]


class ZoneShapeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    camera_id: str
    name: str
    type: str = Field(validation_alias="shape_type", serialization_alias="type")
    polygon_points: list[Any]
    created_at: str
    status: str = "offline"


class ZoneShapeCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    camera_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    type: ZoneShapeType = "general"
    polygon_points: list[list[float]]

    @field_validator("polygon_points")
    @classmethod
    def validate_polygon(cls, value: list[list[float]]) -> list[list[float]]:
        if len(value) < 3:
            raise ValueError("polygon_points must contain at least 3 vertices")
        for point in value:
            if len(point) != 2:
                raise ValueError("each polygon point must be [x, y]")
        return value


class ZoneShapeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: ZoneShapeType | None = None
    polygon_points: list[list[float]] | None = None

    @field_validator("polygon_points")
    @classmethod
    def validate_polygon(cls, value: list[list[float]] | None) -> list[list[float]] | None:
        if value is None:
            return None
        if len(value) < 3:
            raise ValueError("polygon_points must contain at least 3 vertices")
        for point in value:
            if len(point) != 2:
                raise ValueError("each polygon point must be [x, y]")
        return value
