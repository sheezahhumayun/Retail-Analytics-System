"""Superadmin organization management schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

OrganizationStatus = Literal["active", "disabled"]


class OrganizationAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: OrganizationStatus


class OrganizationCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=255)


class OrganizationDeleteConfirm(BaseModel):
    confirm: str = Field(..., min_length=1, max_length=64)
