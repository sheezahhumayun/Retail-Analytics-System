"""Current user profile (Module 12.5)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from database.models import Store, User

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.extended.me import MeResponse

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
