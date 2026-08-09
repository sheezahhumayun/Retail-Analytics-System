"""JWT authentication (MVP session tokens for Module 16 RBAC)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database.models import Organization, Superadmin, User

from .config import get_settings
from .deps import DbSession
from .exceptions import ApiError
from .services.passwords import verify_password

security = HTTPBearer(auto_error=False)

ROLE_ADMIN = "admin"
ROLE_USER = "user"
USER_STATUS_ACTIVE = "active"
USER_STATUS_DISABLED = "disabled"
ORG_STATUS_ACTIVE = "active"
ORG_STATUS_DISABLED = "disabled"
UserRole = Literal["admin", "user"]
AccountType = Literal["org_user", "superadmin"]


def normalize_role(role: str) -> UserRole:
    """Map legacy ``viewer`` / ``manager`` values (and unknowns) to ``user``."""
    if role == ROLE_ADMIN:
        return ROLE_ADMIN
    return ROLE_USER


class TokenPayload(BaseModel):
    sub: str = Field(description="User id")
    email: str
    role: UserRole
    org_id: str | None
    exp: int
    account_type: AccountType = "org_user"


@dataclass(frozen=True)
class UserAdminCaller:
    payload: TokenPayload
    is_superadmin: bool


class LoginRequest(BaseModel):
    email: str = Field(..., examples=["admin@demo-retail.local"])
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserInfo"


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    org_id: str | None
    account_type: AccountType = "org_user"


def create_access_token(user: User) -> tuple[str, int]:
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.jwt_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    role = normalize_role(user.role)
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": role,
        "org_id": user.org_id,
        "account_type": "org_user",
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def create_superadmin_access_token(admin: Superadmin) -> tuple[str, int]:
    settings = get_settings()
    expires_delta = timedelta(minutes=settings.jwt_expire_minutes)
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": admin.id,
        "email": admin.email,
        "role": ROLE_ADMIN,
        "org_id": None,
        "account_type": "superadmin",
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    settings = get_settings()
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        return None
    if user.status == USER_STATUS_DISABLED:
        return None
    if user.password_hash:
        # Real per-user password (set via POST /api/users or
        # POST /api/users/{id}/reset-password) — check against its hash.
        if not verify_password(password, user.password_hash):
            return None
        return user
    # Seed/demo users are created without an individual password_hash and
    # fall back to the shared API_DEFAULT_PASSWORD. Once a user has a hash
    # (created or reset through the admin API), that hash is authoritative
    # and the shared default no longer applies to them.
    if password != settings.api_default_password:
        return None
    return user


def decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        data = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        data["role"] = normalize_role(data.get("role", ROLE_USER))
        if "account_type" not in data:
            data["account_type"] = "org_user"
        return TokenPayload(**data)
    except JWTError as exc:
        raise ApiError(401, "invalid_token", "Invalid or expired access token") from exc


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: DbSession,
) -> TokenPayload:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "not_authenticated", "Missing or invalid Authorization header")
    payload = decode_token(credentials.credentials)

    if payload.account_type != "org_user":
        raise ApiError(
            403,
            "superadmin_token_not_allowed",
            "Superadmin tokens cannot access organization-scoped resources",
        )

    # A previously issued JWT stays cryptographically valid until it expires,
    # but the user it names may have been deleted (or had their role changed)
    # since it was issued. Re-checking against the DB on every request means
    # a deleted user loses access immediately rather than being able to keep
    # using the API until the token's natural expiry.
    user = session.get(User, payload.sub)
    if user is None:
        raise ApiError(401, "invalid_token", "User no longer exists")
    if user.status == USER_STATUS_DISABLED:
        raise ApiError(401, "account_disabled", "Account disabled")
    org = session.get(Organization, user.org_id)
    if org is not None and org.status == ORG_STATUS_DISABLED:
        raise ApiError(401, "account_disabled", "Account disabled")
    return TokenPayload(
        sub=user.id,
        email=user.email,
        role=normalize_role(user.role),
        org_id=user.org_id,
        exp=payload.exp,
        account_type="org_user",
    )


async def get_current_superadmin(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: DbSession,
) -> TokenPayload:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "not_authenticated", "Missing or invalid Authorization header")
    payload = decode_token(credentials.credentials)

    if payload.account_type != "superadmin":
        raise ApiError(403, "forbidden", "Requires superadmin account")

    admin = session.get(Superadmin, payload.sub)
    if admin is None:
        raise ApiError(401, "invalid_token", "User no longer exists")
    if admin.status == USER_STATUS_DISABLED:
        raise ApiError(401, "account_disabled", "Account disabled")
    return TokenPayload(
        sub=admin.id,
        email=admin.email,
        role=ROLE_ADMIN,
        org_id=None,
        exp=payload.exp,
        account_type="superadmin",
    )


async def require_admin(
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> TokenPayload:
    if user.role != ROLE_ADMIN:
        raise ApiError(403, "forbidden", "Requires admin role")
    return user


async def require_user_admin_or_superadmin(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: DbSession,
) -> UserAdminCaller:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "not_authenticated", "Missing or invalid Authorization header")
    payload = decode_token(credentials.credentials)

    if payload.account_type == "superadmin":
        admin = session.get(Superadmin, payload.sub)
        if admin is None:
            raise ApiError(401, "invalid_token", "User no longer exists")
        if admin.status == USER_STATUS_DISABLED:
            raise ApiError(401, "account_disabled", "Account disabled")
        return UserAdminCaller(
            payload=TokenPayload(
                sub=admin.id,
                email=admin.email,
                role=ROLE_ADMIN,
                org_id=None,
                exp=payload.exp,
                account_type="superadmin",
            ),
            is_superadmin=True,
        )

    if payload.account_type != "org_user":
        raise ApiError(403, "forbidden", "Requires admin role")

    user = session.get(User, payload.sub)
    if user is None:
        raise ApiError(401, "invalid_token", "User no longer exists")
    if user.status == USER_STATUS_DISABLED:
        raise ApiError(401, "account_disabled", "Account disabled")
    org = session.get(Organization, user.org_id)
    if org is not None and org.status == ORG_STATUS_DISABLED:
        raise ApiError(401, "account_disabled", "Account disabled")
    role = normalize_role(user.role)
    if role != ROLE_ADMIN:
        raise ApiError(403, "forbidden", "Requires admin role")
    return UserAdminCaller(
        payload=TokenPayload(
            sub=user.id,
            email=user.email,
            role=role,
            org_id=user.org_id,
            exp=payload.exp,
            account_type="org_user",
        ),
        is_superadmin=False,
    )


def _user_from_raw_token(raw_token: str, session: Session) -> TokenPayload:
    payload = decode_token(raw_token)
    if payload.account_type != "org_user":
        raise ApiError(
            403,
            "superadmin_token_not_allowed",
            "Superadmin tokens cannot access organization-scoped resources",
        )
    user = session.get(User, payload.sub)
    if user is None:
        raise ApiError(401, "invalid_token", "User no longer exists")
    if user.status == USER_STATUS_DISABLED:
        raise ApiError(401, "account_disabled", "Account disabled")
    return TokenPayload(
        sub=user.id,
        email=user.email,
        role=normalize_role(user.role),
        org_id=user.org_id,
        exp=payload.exp,
        account_type="org_user",
    )


async def get_current_user_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: DbSession,
    token: Annotated[
        str | None,
        Query(
            description=(
                "JWT access token for contexts that cannot send Authorization "
                "headers (e.g. HTML <img> MJPEG streams)."
            ),
        ),
    ] = None,
) -> TokenPayload:
    """Authenticate via ``Authorization: Bearer`` header or ``?token=`` query param."""
    raw_token: str | None = None
    if credentials is not None and credentials.scheme.lower() == "bearer":
        raw_token = credentials.credentials
    elif token is not None:
        raw_token = token
    if raw_token is None:
        raise ApiError(
            401,
            "not_authenticated",
            "Missing or invalid Authorization header or token query parameter",
        )
    return _user_from_raw_token(raw_token, session)


TokenResponse.model_rebuild()

