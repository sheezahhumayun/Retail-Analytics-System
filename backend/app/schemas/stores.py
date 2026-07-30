"""Store schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Unique store identifier")
    org_id: str = Field(description="Parent organization id")
    name: str
    address: str | None = None


class StoreCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    org_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    address: str | None = Field(default=None, max_length=512)
