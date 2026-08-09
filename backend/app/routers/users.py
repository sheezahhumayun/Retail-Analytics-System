"""User administration (Module 12.5)."""



from __future__ import annotations



from typing import Annotated



from fastapi import APIRouter, Depends

from sqlmodel import select



from database.models import Organization, Store, Superadmin, User



from ..auth import (
    TokenPayload,
    UserAdminCaller,
    normalize_role,
    require_admin,
    require_user_admin_or_superadmin,
)

from ..deps import DbSession

from ..exceptions import ApiError

from ..schemas.extended.users import ResetPasswordRequest, UserCreate, UserResponse, UserUpdate

from ..services.org_scope import require_store_in_org, require_user_in_org

from ..services.passwords import hash_password



router = APIRouter(prefix="/users", tags=["Users"])





def _to_response(user: User) -> UserResponse:

    status = user.status if user.status in ("active", "disabled") else "active"

    return UserResponse(

        id=user.id,

        email=user.email,

        name=user.name,

        role=normalize_role(user.role),

        org_id=user.org_id,

        store_id=user.store_id,

        status=status,

    )





@router.get(

    "",

    response_model=list[UserResponse],

    summary="List users",

    description="List users in the caller's organization. Admin only.",

)

def list_users(

    session: DbSession,

    admin: Annotated[TokenPayload, Depends(require_admin)],

) -> list[UserResponse]:

    rows = session.exec(

        select(User).where(User.org_id == admin.org_id).order_by(User.name)

    ).all()

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

    caller: Annotated[UserAdminCaller, Depends(require_user_admin_or_superadmin)],

) -> UserResponse:

    if not caller.is_superadmin and body.org_id != caller.payload.org_id:
        raise ApiError(404, "org_not_found", f"Organization '{body.org_id}' not found")

    if session.get(User, body.id) is not None:

        raise ApiError(409, "user_exists", f"User '{body.id}' already exists")

    if session.get(Organization, body.org_id) is None:

        raise ApiError(404, "org_not_found", f"Organization '{body.org_id}' not found")

    if body.store_id is not None:

        require_store_in_org(session, body.store_id, body.org_id)



    existing_email = session.exec(select(User).where(User.email == body.email)).first()

    if existing_email is not None:

        raise ApiError(409, "email_exists", f"Email '{body.email}' already in use")

    existing_superadmin_email = session.exec(
        select(Superadmin).where(Superadmin.email == body.email)
    ).first()

    if existing_superadmin_email is not None:

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

    caller: Annotated[UserAdminCaller, Depends(require_user_admin_or_superadmin)],

) -> UserResponse:

    if caller.is_superadmin:
        user = session.get(User, user_id)
        if user is None:
            raise ApiError(404, "user_not_found", f"User '{user_id}' not found")
    else:
        user = require_user_in_org(session, user_id, caller.payload.org_id)



    if body.email is not None:

        conflict = session.exec(select(User).where(User.email == body.email)).first()

        if conflict is not None and conflict.id != user_id:

            raise ApiError(409, "email_exists", f"Email '{body.email}' already in use")

        user.email = body.email

    if body.name is not None:

        user.name = body.name

    if body.role is not None:

        user.role = body.role

    if "store_id" in body.model_fields_set:
        if body.store_id is not None:
            require_store_in_org(session, body.store_id, user.org_id)
        user.store_id = body.store_id

    if body.status is not None:

        user.status = body.status



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

    caller: Annotated[UserAdminCaller, Depends(require_user_admin_or_superadmin)],

) -> None:

    if not caller.is_superadmin and user_id == caller.payload.sub:

        raise ApiError(400, "cannot_delete_self", "Cannot delete your own user account")

    if caller.is_superadmin:
        user = session.get(User, user_id)
        if user is None:
            raise ApiError(404, "user_not_found", f"User '{user_id}' not found")
    else:
        user = require_user_in_org(session, user_id, caller.payload.org_id)

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

    caller: Annotated[UserAdminCaller, Depends(require_user_admin_or_superadmin)],

) -> None:

    if caller.is_superadmin:
        user = session.get(User, user_id)
        if user is None:
            raise ApiError(404, "user_not_found", f"User '{user_id}' not found")
    else:
        user = require_user_in_org(session, user_id, caller.payload.org_id)

    user.password_hash = hash_password(body.new_password)

    session.add(user)

