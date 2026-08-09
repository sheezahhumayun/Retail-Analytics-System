"""Organization listing (Module 12.5)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select

from database.models import Organization, Store

from ..auth import TokenPayload, get_current_user
from ..deps import DbSession
from ..schemas.extended.organizations import OrganizationResponse, StoreSummary

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get(
    "/scoped",
    response_model=list[OrganizationResponse],
    summary="List organizations",
    description="Return organizations visible to the authenticated user with nested store list.",
)
def list_organizations(
    session: DbSession,
    token: Annotated[TokenPayload, Depends(get_current_user)],
) -> list[OrganizationResponse]:
    org = session.get(Organization, token.org_id)
    if org is None:
        return []
    stores = session.exec(select(Store).where(Store.org_id == org.id).order_by(Store.name)).all()
    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            stores=[StoreSummary(id=s.id, name=s.name, address=s.address) for s in stores],
        )
    ]
