"""Organization schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StoreSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    address: str | None = None


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    stores: list[StoreSummary] = []
