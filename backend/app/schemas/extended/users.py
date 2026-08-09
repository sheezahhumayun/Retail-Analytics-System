"""User admin schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from ...auth import UserRole

UserAccountStatus = Literal["active", "disabled"]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    name: str
    role: UserRole
    org_id: str
    store_id: str | None = None
    status: UserAccountStatus = "active"


class UserCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    role: UserRole = "user"
    org_id: str = Field(..., min_length=1, max_length=64)
    store_id: str | None = None
    password: str = Field(..., min_length=4, max_length=128)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = None
    store_id: str | None = None
    status: UserAccountStatus | None = None


class ResetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=4, max_length=128)
