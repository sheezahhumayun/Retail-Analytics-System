"""Store CRUD endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from database.models import Organization, Store

from ..auth import TokenPayload, get_current_user, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.stores import StoreCreate, StoreResponse

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get(
    "",
    response_model=list[StoreResponse],
    summary="List stores",
    description="Return all stores in the organization hierarchy.",
)
def list_stores(
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(get_current_user)],
) -> list[Store]:
    return list(session.exec(select(Store).order_by(Store.name)).all())


@router.post(
    "",
    response_model=StoreResponse,
    status_code=201,
    summary="Create store",
    description="Create a new store. Requires admin role.",
)
def create_store(
    body: StoreCreate,
    session: DbSession,
    _user: Annotated[TokenPayload, Depends(require_admin)],
) -> Store:
    if session.get(Store, body.id) is not None:
        raise ApiError(409, "store_exists", f"Store '{body.id}' already exists")
    org = session.get(Organization, body.org_id)
    if org is None:
        raise ApiError(404, "org_not_found", f"Organization '{body.org_id}' not found")
    store = Store(**body.model_dump())
    session.add(store)
    session.flush()
    session.refresh(store)
    return store
