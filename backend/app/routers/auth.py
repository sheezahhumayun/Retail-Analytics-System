"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from ..auth import (
    LoginRequest,
    TokenResponse,
    UserInfo,
    authenticate_user,
    create_access_token,
)
from ..deps import DbSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain JWT access token",
    description=(
        "Authenticate with email and password. MVP uses the seeded demo user "
        "(`admin@demo-retail.local`) and password from `API_DEFAULT_PASSWORD` (default: `demo`)."
    ),
)
def login(body: LoginRequest, session: DbSession) -> TokenResponse:
    from ..exceptions import ApiError

    user = authenticate_user(session, body.email, body.password)
    if user is None:
        raise ApiError(401, "invalid_credentials", "Invalid email or password")
    token, expires_in = create_access_token(user)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserInfo(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role,
            org_id=user.org_id,
        ),
    )
