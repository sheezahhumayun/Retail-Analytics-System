"""Current user profile (Module 12.5)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from database.models import Store, Superadmin, User

from ..auth import TokenPayload, get_current_superadmin, get_current_user
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.extended.me import MeResponse, SuperadminMeResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Current user profile",
    description="Return the authenticated user's id, email, role, org, and visible stores.",
)
def get_me(
    session: DbSession,
    token: Annotated[TokenPayload, Depends(get_current_user)],
) -> MeResponse:
    user = session.get(User, token.sub)
    if user is None:
        raise ApiError(404, "user_not_found", "User no longer exists")

    stores = session.exec(select(Store).where(Store.org_id == user.org_id).order_by(Store.name)).all()
    store_ids = [s.id for s in stores]
    return MeResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=token.role,
        org_id=user.org_id,
        store_id=user.store_id,
        store_ids=store_ids,
    )


@router.get(
    "/superadmin/me",
    response_model=SuperadminMeResponse,
    summary="Current superadmin profile",
    description="Return the authenticated superadmin's id, email, and name.",
)
def get_superadmin_me(
    session: DbSession,
    token: Annotated[TokenPayload, Depends(get_current_superadmin)],
) -> SuperadminMeResponse:
    admin = session.get(Superadmin, token.sub)
    if admin is None:
        raise ApiError(404, "user_not_found", "Superadmin no longer exists")

    return SuperadminMeResponse(
        id=admin.id,
        email=admin.email,
        name=admin.name,
        role=token.role,
    )
