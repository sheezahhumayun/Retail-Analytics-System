"""Store CRUD endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from database.models import Camera, Organization, Store

from ..auth import TokenPayload, get_current_user, require_admin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.stores import StoreCreate, StoreResponse, StoreUpdate
from ..services.org_scope import require_store_in_org, stores_for_org_stmt

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get(
    "",
    response_model=list[StoreResponse],
    summary="List stores",
    description="Return stores in the authenticated user's organization.",
)
def list_stores(
    session: DbSession,
    user: Annotated[TokenPayload, Depends(get_current_user)],
) -> list[Store]:
    return list(session.exec(stores_for_org_stmt(user.org_id)).all())


@router.post(
    "",
    response_model=StoreResponse,
    status_code=201,
    summary="Create store",
    description="Create a new store in the caller's organization. Requires admin role.",
)
def create_store(
    body: StoreCreate,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> Store:
    if body.org_id != admin.org_id:
        raise ApiError(404, "org_not_found", f"Organization '{body.org_id}' not found")
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


@router.put(
    "/{store_id}",
    response_model=StoreResponse,
    summary="Update store",
    description="Update store name or address. Admin only; store must belong to caller's org.",
)
def update_store(
    store_id: str,
    body: StoreUpdate,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> Store:
    store = require_store_in_org(session, store_id, admin.org_id)
    if body.name is not None:
        store.name = body.name
    if body.address is not None:
        store.address = body.address
    session.add(store)
    session.flush()
    session.refresh(store)
    return store


@router.delete(
    "/{store_id}",
    status_code=204,
    summary="Delete store",
    description=(
        "Delete a store when it has no cameras. Admin only; store must belong to caller's org."
    ),
)
def delete_store(
    store_id: str,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> None:
    require_store_in_org(session, store_id, admin.org_id)
    has_cameras = session.exec(
        select(Camera.id).where(Camera.store_id == store_id).limit(1)
    ).first()
    if has_cameras is not None:
        raise ApiError(
            409,
            "store_has_cameras",
            "Cannot delete a store that still has cameras assigned",
        )
    store = session.get(Store, store_id)
    assert store is not None
    session.delete(store)
