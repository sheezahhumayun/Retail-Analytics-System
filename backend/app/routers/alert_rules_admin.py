"""Admin alert_rules endpoints (Module 15, Phase 4)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import col

from database.models import AlertRule

from ..auth import TokenPayload, require_admin
from ..deps import DbSession
from ..schemas.extended.alert_rules import AlertRuleResponse, AlertRuleUpdate
from ..services.org_scope import alert_rules_for_org_stmt, require_alert_rule_in_org

router = APIRouter(prefix="/admin/alert-rules", tags=["Admin — Alert Rules"])


def _to_response(rule: AlertRule) -> AlertRuleResponse:
    return AlertRuleResponse(
        id=rule.id,  # type: ignore[arg-type]
        rule_type=rule.rule_type,
        store_id=rule.store_id,
        zone_id=rule.zone_id,
        threshold=rule.threshold,
        severity=rule.severity,
        enabled=rule.enabled,
        created_at=rule.created_at.isoformat(),
        updated_at=rule.updated_at.isoformat(),
    )


@router.get(
    "",
    response_model=list[AlertRuleResponse],
    summary="List alert rules",
    description="Return alert_rules rows for the caller's organization. Admin only.",
)
def list_alert_rules(
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> list[AlertRuleResponse]:
    rows = session.exec(
        alert_rules_for_org_stmt(admin.org_id).order_by(AlertRule.rule_type, col(AlertRule.id))
    ).all()
    return [_to_response(row) for row in rows]


@router.put(
    "/{rule_id}",
    response_model=AlertRuleResponse,
    summary="Update alert rule",
    description="Update threshold, severity, and enabled flag on an existing rule. Admin only.",
)
def update_alert_rule(
    rule_id: int,
    body: AlertRuleUpdate,
    session: DbSession,
    admin: Annotated[TokenPayload, Depends(require_admin)],
) -> AlertRuleResponse:
    rule = require_alert_rule_in_org(session, rule_id, admin.org_id)

    rule.threshold = body.threshold
    rule.severity = body.severity
    rule.enabled = body.enabled
    rule.updated_at = datetime.now(timezone.utc)
    session.add(rule)
    session.flush()
    session.refresh(rule)
    return _to_response(rule)
