"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from sqlmodel import select

from database.models import Superadmin, User

from ..auth import (
    USER_STATUS_DISABLED,
    LoginRequest,
    TokenResponse,
    UserInfo,
    authenticate_user,
    create_access_token,
    create_superadmin_access_token,
    normalize_role,
)
from ..deps import DbSession
from ..exceptions import ApiError
from ..services.passwords import verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Obtain JWT access token",
    description=(
        "Authenticate with email and password. MVP uses the seeded demo users "
        "(`admin@demo-retail.local` or `user@demo-retail.local`) and password from "
        "`API_DEFAULT_PASSWORD` (default: `demo`). Roles: `admin` or `user`."
    ),
)
def login(body: LoginRequest, session: DbSession) -> TokenResponse:
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing is not None:
        if existing.status == USER_STATUS_DISABLED:
            raise ApiError(401, "account_disabled", "Account disabled")
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
                role=normalize_role(user.role),
                org_id=user.org_id,
                account_type="org_user",
            ),
        )

    superadmin = session.exec(select(Superadmin).where(Superadmin.email == body.email)).first()
    if superadmin is not None:
        if superadmin.status == USER_STATUS_DISABLED:
            raise ApiError(401, "account_disabled", "Account disabled")
        if not verify_password(body.password, superadmin.password_hash):
            raise ApiError(401, "invalid_credentials", "Invalid email or password")
        token, expires_in = create_superadmin_access_token(superadmin)
        return TokenResponse(
            access_token=token,
            expires_in=expires_in,
            user=UserInfo(
                id=superadmin.id,
                email=superadmin.email,
                name=superadmin.name,
                role="admin",
                org_id=None,
                account_type="superadmin",
            ),
        )

    raise ApiError(401, "invalid_credentials", "Invalid email or password")
