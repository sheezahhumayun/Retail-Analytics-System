"""Superadmin organization CRUD (Phase 2)."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from database.models import Organization, User

from ..auth import ORG_STATUS_ACTIVE, ORG_STATUS_DISABLED, TokenPayload, get_current_superadmin
from ..deps import DbSession
from ..exceptions import ApiError
from ..schemas.extended.organizations_admin import (
    OrganizationAdminResponse,
    OrganizationCreate,
    OrganizationDeleteConfirm,
)
from ..schemas.extended.users import UserResponse
from ..schemas.stores import StoreResponse
from ..services.camera_process import kill_processing_runs_for_org
from ..services.org_delete import delete_organization_cascade
from ..services.org_scope import stores_for_org_stmt
from .users import _to_response as user_to_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["Admin — Organizations"])


def _to_response(org: Organization) -> OrganizationAdminResponse:
    status = org.status if org.status in (ORG_STATUS_ACTIVE, ORG_STATUS_DISABLED) else ORG_STATUS_ACTIVE
    return OrganizationAdminResponse(id=org.id, name=org.name, status=status)  # type: ignore[arg-type]


@router.post(
    "",
    response_model=OrganizationAdminResponse,
    status_code=201,
    summary="Create organization",
    description="Create a new organization. Superadmin only.",
)
def create_organization(
    body: OrganizationCreate,
    session: DbSession,
    _superadmin: Annotated[TokenPayload, Depends(get_current_superadmin)],
) -> OrganizationAdminResponse:
    if session.get(Organization, body.id) is not None:
        raise ApiError(409, "org_exists", f"Organization '{body.id}' already exists")
    org = Organization(id=body.id, name=body.name, status=ORG_STATUS_ACTIVE)
    session.add(org)
    session.flush()
    session.refresh(org)
    return _to_response(org)


@router.get(
    "",
    response_model=list[OrganizationAdminResponse],
    summary="List organizations",
    description="Return all organizations. Superadmin only.",
)
def list_organizations(
    session: DbSession,
    _superadmin: Annotated[TokenPayload, Depends(get_current_superadmin)],
) -> list[OrganizationAdminResponse]:
    rows = session.exec(select(Organization).order_by(Organization.name)).all()
    return [_to_response(org) for org in rows]


@router.get(
    "/{org_id}",
    response_model=OrganizationAdminResponse,
    summary="Get organization",
    description="Return one organization by id. Superadmin only.",
)
def get_organization(
    org_id: str,
    session: DbSession,
    _superadmin: Annotated[TokenPayload, Depends(get_current_superadmin)],
) -> OrganizationAdminResponse:
    org = session.get(Organization, org_id)
    if org is None:
        raise ApiError(404, "org_not_found", f"Organization '{org_id}' not found")
    return _to_response(org)


@router.get(
    "/{org_id}/users",
    response_model=list[UserResponse],
    summary="List organization users",
    description="Return all users in an organization. Superadmin only.",
)
def list_organization_users(
    org_id: str,
    session: DbSession,
    _superadmin: Annotated[TokenPayload, Depends(get_current_superadmin)],
) -> list[UserResponse]:
    if session.get(Organization, org_id) is None:
        raise ApiError(404, "org_not_found", f"Organization '{org_id}' not found")
    rows = session.exec(
        select(User).where(User.org_id == org_id).order_by(User.name)
    ).all()
    return [user_to_response(u) for u in rows]


@router.get(
    "/{org_id}/stores",
    response_model=list[StoreResponse],
    summary="List organization stores",
    description="Return all stores in an organization. Superadmin only.",
)
def list_organization_stores(
    org_id: str,
    session: DbSession,
    _superadmin: Annotated[TokenPayload, Depends(get_current_superadmin)],
) -> list[StoreResponse]:
    if session.get(Organization, org_id) is None:
        raise ApiError(404, "org_not_found", f"Organization '{org_id}' not found")
    return list(session.exec(stores_for_org_stmt(org_id)).all())


@router.post(
    "/{org_id}/toggle",
    response_model=OrganizationAdminResponse,
    summary="Toggle organization status",
    description="Flip organization status between active and disabled. Superadmin only.",
)
def toggle_organization(
    org_id: str,
    session: DbSession,
    _superadmin: Annotated[TokenPayload, Depends(get_current_superadmin)],
) -> OrganizationAdminResponse:
    org = session.get(Organization, org_id)
    if org is None:
        raise ApiError(404, "org_not_found", f"Organization '{org_id}' not found")
    new_status = (
        ORG_STATUS_DISABLED
        if org.status == ORG_STATUS_ACTIVE
        else ORG_STATUS_ACTIVE
    )
    org.status = new_status
    session.add(org)
    session.flush()
    session.refresh(org)
    if new_status == ORG_STATUS_DISABLED:
        session.commit()
        killed = kill_processing_runs_for_org(org_id)
        from ..services.live_analytics_worker import stop_live_workers_for_org

        stopped_live = stop_live_workers_for_org(org_id)
        if killed:
            logger.info(
                "Disabled organization %s; cancelled %d in-flight processing run(s)",
                org_id,
                killed,
            )
        if stopped_live:
            logger.info(
                "Disabled organization %s; stopped %d live analytics camera(s)",
                org_id,
                stopped_live,
            )
    return _to_response(org)


@router.delete(
    "/{org_id}",
    status_code=204,
    summary="Delete organization",
    description=(
        "Permanently delete an organization and all dependent data. "
        "Requires body.confirm to match org_id. Superadmin only."
    ),
)
def delete_organization(
    org_id: str,
    body: OrganizationDeleteConfirm,
    session: DbSession,
    _superadmin: Annotated[TokenPayload, Depends(get_current_superadmin)],
) -> None:
    if body.confirm != org_id:
        raise ApiError(
            400,
            "confirm_mismatch",
            f"Confirmation id '{body.confirm}' does not match organization '{org_id}'",
        )
    org = session.get(Organization, org_id)
    if org is None:
        raise ApiError(404, "org_not_found", f"Organization '{org_id}' not found")
    delete_organization_cascade(session, org_id)
