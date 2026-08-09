"""Organization-scoping helpers for multi-tenant API enforcement."""

from __future__ import annotations

from sqlalchemy import and_, or_
from sqlmodel import Session, col, select
from sqlmodel.sql.expression import SelectOfScalar

from database.models import (
    Alert,
    AlertRule,
    Camera,
    CountingLine,
    Event,
    Store,
    User,
    Zone,
    ZoneShape,
)

from ..exceptions import ApiError


def require_same_org(user_org_id: str, resource_org_id: str, *, not_found_code: str, not_found_message: str) -> None:
    """Raise 404 when the resource belongs to a different organization (same as missing)."""
    if user_org_id != resource_org_id:
        raise ApiError(404, not_found_code, not_found_message)


def require_store_in_org(session: Session, store_id: str, org_id: str) -> Store:
    store = session.get(Store, store_id)
    if store is None or store.org_id != org_id:
        raise ApiError(404, "store_not_found", f"Store '{store_id}' not found")
    return store


def require_camera_in_org(session: Session, camera_id: str, org_id: str) -> Camera:
    camera = session.get(Camera, camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
    store = session.get(Store, camera.store_id)
    if store is None or store.org_id != org_id:
        raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
    return camera


def require_zone_in_org(session: Session, zone_id: str, org_id: str) -> Zone:
    zone = session.get(Zone, zone_id)
    if zone is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
    camera = session.get(Camera, zone.camera_id)
    if camera is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
    store = session.get(Store, camera.store_id)
    if store is None or store.org_id != org_id:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_id}' not found")
    return zone


def require_zone_shape_in_org(session: Session, zone_shape_id: str, org_id: str) -> ZoneShape:
    row = session.get(ZoneShape, zone_shape_id)
    if row is None:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_shape_id}' not found")
    try:
        require_camera_in_org(session, row.camera_id, org_id)
    except ApiError:
        raise ApiError(404, "zone_not_found", f"Zone '{zone_shape_id}' not found") from None
    return row


def require_line_in_org(session: Session, line_id: str, org_id: str) -> CountingLine:
    row = session.get(CountingLine, line_id)
    if row is None:
        raise ApiError(404, "line_not_found", f"Counting line '{line_id}' not found")
    try:
        require_camera_in_org(session, row.camera_id, org_id)
    except ApiError:
        raise ApiError(404, "line_not_found", f"Counting line '{line_id}' not found") from None
    return row


def require_user_in_org(session: Session, user_id: str, org_id: str) -> User:
    user = session.get(User, user_id)
    if user is None or user.org_id != org_id:
        raise ApiError(404, "user_not_found", f"User '{user_id}' not found")
    return user


def require_alert_rule_in_org(session: Session, rule_id: int, org_id: str) -> AlertRule:
    rule = session.get(AlertRule, rule_id)
    if rule is None:
        raise ApiError(404, "alert_rule_not_found", f"Alert rule '{rule_id}' not found")
    if rule.org_id is not None:
        if rule.org_id != org_id:
            raise ApiError(404, "alert_rule_not_found", f"Alert rule '{rule_id}' not found")
        return rule
    if rule.store_id is not None:
        try:
            require_store_in_org(session, rule.store_id, org_id)
        except ApiError:
            raise ApiError(404, "alert_rule_not_found", f"Alert rule '{rule_id}' not found") from None
        return rule
    if rule.zone_id is not None:
        try:
            require_zone_in_org(session, rule.zone_id, org_id)
        except ApiError:
            raise ApiError(404, "alert_rule_not_found", f"Alert rule '{rule_id}' not found") from None
        return rule
    if rule.camera_id is not None:
        try:
            require_camera_in_org(session, rule.camera_id, org_id)
        except ApiError:
            raise ApiError(404, "alert_rule_not_found", f"Alert rule '{rule_id}' not found") from None
        return rule
    raise ApiError(404, "alert_rule_not_found", f"Alert rule '{rule_id}' not found")


def _alert_store_id_from_metadata(alert: Alert) -> str | None:
    if not alert.metadata_:
        return None
    raw = alert.metadata_.get("store_id")
    if raw is None:
        return None
    return str(raw)


def _require_store_level_alert_in_org(session: Session, alert: Alert, org_id: str) -> None:
    store_id = _alert_store_id_from_metadata(alert)
    if store_id is None:
        raise ApiError(404, "alert_not_found", f"Alert '{alert.id}' not found")
    try:
        require_store_in_org(session, store_id, org_id)
    except ApiError:
        raise ApiError(404, "alert_not_found", f"Alert '{alert.id}' not found") from None


def require_alert_in_org(session: Session, alert_id: int, org_id: str) -> Alert:
    alert = session.get(Alert, alert_id)
    if alert is None:
        raise ApiError(404, "alert_not_found", f"Alert '{alert_id}' not found")
    if alert.camera_id is not None:
        try:
            require_camera_in_org(session, alert.camera_id, org_id)
        except ApiError:
            raise ApiError(404, "alert_not_found", f"Alert '{alert_id}' not found") from None
        return alert
    if alert.zone_id is not None:
        try:
            require_zone_in_org(session, alert.zone_id, org_id)
        except ApiError:
            raise ApiError(404, "alert_not_found", f"Alert '{alert_id}' not found") from None
        return alert
    _require_store_level_alert_in_org(session, alert, org_id)
    return alert


def require_analytics_scope(
    session: Session,
    org_id: str,
    *,
    store_id: str,
    camera_id: str | None = None,
    zone_id: str | None = None,
) -> None:
    """Validate store/camera/zone parameters belong to the caller's organization."""
    require_store_in_org(session, store_id, org_id)
    if camera_id is not None:
        camera = require_camera_in_org(session, camera_id, org_id)
        if camera.store_id != store_id:
            raise ApiError(
                400,
                "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'",
            )
    if zone_id is not None:
        zone = require_zone_in_org(session, zone_id, org_id)
        if camera_id is not None and zone.camera_id != camera_id:
            raise ApiError(
                400,
                "invalid_scope",
                f"Zone '{zone_id}' does not belong to camera '{camera_id}'",
            )


def stores_for_org_stmt(org_id: str) -> SelectOfScalar[Store]:
    return select(Store).where(Store.org_id == org_id).order_by(Store.name)


def cameras_for_org_stmt(org_id: str, *, store_id: str | None = None) -> SelectOfScalar[Camera]:
    stmt = (
        select(Camera)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
        .order_by(Camera.name)
    )
    if store_id is not None:
        stmt = stmt.where(Camera.store_id == store_id)
    return stmt


def zone_shapes_for_org_stmt(org_id: str, *, camera_id: str | None = None) -> SelectOfScalar[ZoneShape]:
    stmt = (
        select(ZoneShape)
        .join(Camera, ZoneShape.camera_id == Camera.id)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
        .order_by(ZoneShape.name)
    )
    if camera_id is not None:
        stmt = stmt.where(ZoneShape.camera_id == camera_id)
    return stmt


def counting_lines_for_org_stmt(
    org_id: str,
    *,
    camera_id: str | None = None,
) -> SelectOfScalar[CountingLine]:
    stmt = (
        select(CountingLine)
        .join(Camera, CountingLine.camera_id == Camera.id)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
        .order_by(CountingLine.name)
    )
    if camera_id is not None:
        stmt = stmt.where(CountingLine.camera_id == camera_id)
    return stmt


def events_for_org_stmt(org_id: str) -> SelectOfScalar[Event]:
    return (
        select(Event)
        .join(Camera, Event.camera_id == Camera.id)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
    )


def alerts_for_org_stmt(org_id: str) -> SelectOfScalar[Alert]:
    org_store_ids = select(Store.id).where(Store.org_id == org_id)
    camera_ids = select(Camera.id).join(Store, Camera.store_id == Store.id).where(Store.org_id == org_id)
    zone_ids = (
        select(Zone.id)
        .join(Camera, Zone.camera_id == Camera.id)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
    )
    metadata_store_id = Alert.metadata_["store_id"].as_string()
    store_level = and_(
        Alert.camera_id.is_(None),  # type: ignore[union-attr]
        Alert.zone_id.is_(None),  # type: ignore[union-attr]
        metadata_store_id.in_(org_store_ids),
    )
    return select(Alert).where(
        or_(
            col(Alert.camera_id).in_(camera_ids),
            col(Alert.zone_id).in_(zone_ids),
            store_level,
        )
    )


def alert_rules_for_org_stmt(org_id: str) -> SelectOfScalar[AlertRule]:
    return select(AlertRule).where(AlertRule.org_id == org_id)
