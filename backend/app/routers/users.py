"""User administration (Module 12.5)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from database.models import Organization, Store, User

from ..auth import TokenPayload, normalize_role, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.extended.users import ResetPasswordRequest, UserCreate, UserResponse, UserUpdate
from ..services.passwords import hash_password

router = APIRouter(prefix="/users", tags=["Users"])


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=normalize_role(user.role),
        org_id=user.org_id,
        store_id=user.store_id,
    )


@router.get(
    "",
    response_model=list[UserResponse],
    summary="List users",
    description="List users in the system. Admin only.",
)
def list_users(
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> list[UserResponse]:
    rows = session.exec(select(User).order_by(User.name)).all()
    return [_to_response(u) for u in rows]


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    summary="Create user",
    description="Create a new user with hashed password. Admin only.",
)
def create_user(
    body: UserCreate,
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> UserResponse:
    if session.get(User, body.id) is not None:
        raise ApiError(409, "user_exists", f"User '{body.id}' already exists")
    if session.get(Organization, body.org_id) is None:
        raise ApiError(404, "org_not_found", f"Organization '{body.org_id}' not found")
    if body.store_id is not None and session.get(Store, body.store_id) is None:
        raise ApiError(404, "store_not_found", f"Store '{body.store_id}' not found")

    existing_email = session.exec(select(User).where(User.email == body.email)).first()
    if existing_email is not None:
        raise ApiError(409, "email_exists", f"Email '{body.email}' already in use")

    user = User(
        id=body.id,
        org_id=body.org_id,
        store_id=body.store_id,
        name=body.name,
        email=body.email,
        role=body.role,
        password_hash=hash_password(body.password),
    )
    session.add(user)
    session.flush()
    session.refresh(user)
    return _to_response(user)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user",
    description="Update user profile fields. Admin only.",
)
def update_user(
    user_id: str,
    body: UserUpdate,
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> UserResponse:
    user = session.get(User, user_id)
    if user is None:
        raise ApiError(404, "user_not_found", f"User '{user_id}' not found")

    if body.email is not None:
        conflict = session.exec(select(User).where(User.email == body.email)).first()
        if conflict is not None and conflict.id != user_id:
            raise ApiError(409, "email_exists", f"Email '{body.email}' already in use")
        user.email = body.email
    if body.name is not None:
        user.name = body.name
    if body.role is not None:
        user.role = body.role
    if body.store_id is not None:
        if session.get(Store, body.store_id) is None:
            raise ApiError(404, "store_not_found", f"Store '{body.store_id}' not found")
        user.store_id = body.store_id

    session.add(user)
    session.flush()
    session.refresh(user)
    return _to_response(user)


@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete user",
    description="Remove a user account. Admin only.",
)
def delete_user(
    user_id: str,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> None:
    if user_id == admin.sub:
        raise ApiError(400, "cannot_delete_self", "Cannot delete your own user account")
    user = session.get(User, user_id)
    if user is None:
        raise ApiError(404, "user_not_found", f"User '{user_id}' not found")
    session.delete(user)


@router.post(
    "/{user_id}/reset-password",
    status_code=204,
    summary="Reset user password",
    description="Set a new password hash for a user. Admin only.",
)
def reset_password(
    user_id: str,
    body: ResetPasswordRequest,
    session: DbSession,
    _admin: Annotated[TokenPayload, Depends(require_admin)],
) -> None:
    user = session.get(User, user_id)
    if user is None:
        raise ApiError(404, "user_not_found", f"User '{user_id}' not found")
    user.password_hash = hash_password(body.new_password)
    session.add(user)
