"""Counting line schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

LineDirection = Literal["left_is_inside", "right_is_inside"]


class Point(BaseModel):
    x: float
    y: float


class CountingLineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    camera_id: str
    name: str
    point_a: Point
    point_b: Point
    direction: LineDirection
    created_at: str
    status: str = "offline"


class CountingLineCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    camera_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    point_a: Point
    point_b: Point
    direction: LineDirection = "left_is_inside"


class CountingLineUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    point_a: Point | None = None
    point_b: Point | None = None
    direction: LineDirection | None = None
