"""Current user profile."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from ...auth import UserRole


class MeResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    org_id: str
    store_id: str | None = Field(default=None, description="Optional store scope for this user")
    store_ids: list[str] = Field(
        default_factory=list,
        description="Stores visible under the user's organization",
    )


class SuperadminMeResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    org_id: None = None
    account_type: Literal["superadmin"] = "superadmin"
    store_id: None = None
    store_ids: list[str] = Field(default_factory=list)
