"""Load configurable alert thresholds from alert_rules table (Module 15, Phase 2)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from analytics.modules import QUEUE_ZONE_TYPES
from sqlmodel import select

from database import AlertRule
from database.session import session_scope

if TYPE_CHECKING:
    from database.session import Session

logger = logging.getLogger(__name__)


def get_dwell_thresholds(
    zone_ids: list[str] | None = None,
    store_id: str | None = None,
) -> dict[str, float | None]:
    """Load DWELL_THRESHOLD rules for specified zones.

    Parameters
    ----------
    zone_ids : list[str] | None
        Zone IDs to load. If None, loads for all zones with active rules.
    store_id : str | None
        Store ID for store-specific overrides (future phase).

    Returns
    -------
    dict[str, float | None]
        Mapping of zone_id → threshold_seconds.
        Includes all zones with enabled DWELL_THRESHOLD rules.
        Falls back to org-wide default if no zone-specific rule exists.
    """
    return _load_thresholds("DWELL_THRESHOLD", zone_ids, store_id)


def get_queue_length_thresholds(
    zone_ids: list[str] | None = None,
    store_id: str | None = None,
) -> dict[str, int | None]:
    """Load QUEUE_THRESHOLD (length) rules for specified zones.

    Parameters
    ----------
    zone_ids : list[str] | None
        Zone IDs to load. If None, loads for all zones with active rules.
    store_id : str | None
        Store ID for store-specific overrides (future phase).

    Returns
    -------
    dict[str, int | None]
        Mapping of zone_id → threshold_persons.
    """
    thresholds = _load_thresholds("QUEUE_THRESHOLD", zone_ids, store_id)
    return {zid: int(val) if val is not None else None for zid, val in thresholds.items()}


def get_queue_duration_thresholds(
    zone_ids: list[str] | None = None,
    store_id: str | None = None,
) -> dict[str, float | None]:
    """Load QUEUE_THRESHOLD_DURATION rules for specified zones.

    Parameters
    ----------
    zone_ids : list[str] | None
        Zone IDs to load. If None, loads for all zones with active rules.
    store_id : str | None
        Store ID for store-specific overrides (future phase).

    Returns
    -------
    dict[str, float | None]
        Mapping of zone_id → threshold_seconds.
    """
    return _load_thresholds("QUEUE_THRESHOLD_DURATION", zone_ids, store_id)


_OCCUPANCY_THRESHOLD_DEFAULT = 30.0


def get_occupancy_threshold(store_id: str) -> float | None:
    """Load OCCUPANCY_THRESHOLD rule for a store.

    Parameters
    ----------
    store_id : str
        Store ID for store-specific lookup.

    Returns
    -------
    float | None
        Threshold person count. Falls back to org-wide default, then seeded
        default (30.0) if no row exists.
    """
    loaded = _load_occupancy_rule(store_id)
    if loaded is not None:
        return loaded[0]
    return _OCCUPANCY_THRESHOLD_DEFAULT


def get_occupancy_severity(store_id: str) -> str:
    """Severity from the matched OCCUPANCY_THRESHOLD rule (default ``warning``)."""
    loaded = _load_occupancy_rule(store_id)
    if loaded is not None:
        return loaded[1]
    return "warning"


def get_camera_offline_duration_rule(
    camera_id: str,
    store_id: str,
    session: Session | None = None,
) -> tuple[float, str] | None:
    """Load CAMERA_OFFLINE_DURATION rule for a camera.

    Lookup order: per-camera → store-wide → org-wide default.
    Returns ``(threshold_seconds, severity)`` or ``None`` if no enabled rule exists.
    """
    if session is not None:
        return _load_camera_offline_duration_rule(session, camera_id, store_id)

    with session_scope() as sess:
        return _load_camera_offline_duration_rule(sess, camera_id, store_id)


def _load_camera_offline_duration_rule(
    session: Session,
    camera_id: str,
    store_id: str,
) -> tuple[float, str] | None:
    stmt = select(AlertRule).where(
        AlertRule.rule_type == "CAMERA_OFFLINE_DURATION",
        AlertRule.enabled == True,
    )
    all_rules = session.exec(stmt).all()

    camera_rule: AlertRule | None = None
    store_rule: AlertRule | None = None
    org_default: AlertRule | None = None

    for rule in all_rules:
        if rule.camera_id == camera_id:
            camera_rule = rule
        elif (
            rule.camera_id is None
            and rule.zone_id is None
            and rule.store_id == store_id
        ):
            store_rule = rule
        elif (
            rule.camera_id is None
            and rule.zone_id is None
            and rule.store_id is None
        ):
            org_default = rule

    matched = camera_rule if camera_rule is not None else store_rule
    if matched is None:
        matched = org_default
    if matched is None:
        return None
    return matched.threshold, matched.severity


def _load_occupancy_rule(store_id: str) -> tuple[float, str] | None:
    """Load store-level OCCUPANCY_THRESHOLD rule with org-wide fallback."""
    with session_scope() as session:
        stmt = select(AlertRule).where(
            AlertRule.rule_type == "OCCUPANCY_THRESHOLD",
            AlertRule.enabled == True,
            AlertRule.zone_id.is_(None),  # type: ignore[union-attr]
        )
        all_rules = session.exec(stmt).all()

        store_rule: AlertRule | None = None
        org_default: AlertRule | None = None

        for rule in all_rules:
            if rule.store_id == store_id:
                store_rule = rule
            elif rule.store_id is None:
                org_default = rule

        matched = store_rule if store_rule is not None else org_default
        if matched is not None:
            return matched.threshold, matched.severity
    return None


def _load_thresholds(
    rule_type: str,
    zone_ids: list[str] | None = None,
    store_id: str | None = None,
) -> dict[str, float | None]:
    """Internal: Load alert rules from database with fallback hierarchy.

    Lookup order (Phase 2):
    1. Per-zone rule (store_id=NULL, zone_id=<id>, enabled=true)
    2. Store-specific rule (store_id=<store_id>, zone_id=NULL) — future phase
    3. Org-wide default (store_id=NULL, zone_id=NULL)

    For each requested zone_id:
    - If a zone-specific rule exists, use it
    - Else if a store-specific rule exists, use it (future phase)
    - Else use the org-wide default
    """
    thresholds: dict[str, float | None] = {}

    with session_scope() as session:
        # Load all enabled rules for this rule_type
        stmt = select(AlertRule).where(
            AlertRule.rule_type == rule_type,
            AlertRule.enabled == True,
        )
        all_rules = session.exec(stmt).all()

        # Organize rules by lookup key
        zone_rules: dict[str, AlertRule] = {}  # zone_id -> rule
        store_rules: dict[str, AlertRule] = {}  # store_id -> rule (future phase)
        org_default: AlertRule | None = None

        for rule in all_rules:
            if rule.zone_id is not None:
                # Per-zone rule (highest priority)
                zone_rules[rule.zone_id] = rule
            elif rule.store_id is not None:
                # Store-specific rule (future phase, medium priority)
                store_rules[rule.store_id] = rule
            else:
                # Org-wide default (lowest priority)
                org_default = rule

        # Build result dict: requested zone_ids with fallback hierarchy
        if zone_ids:
            for zid in zone_ids:
                if zid in zone_rules:
                    thresholds[zid] = zone_rules[zid].threshold
                elif store_id and store_id in store_rules:
                    thresholds[zid] = store_rules[store_id].threshold
                elif org_default is not None:
                    thresholds[zid] = org_default.threshold
        else:
            # Load all zones with explicit rules (not org default)
            for zid, rule in zone_rules.items():
                thresholds[zid] = rule.threshold

    return thresholds


def _get_org_default_rule(session: Session, rule_type: str) -> AlertRule | None:
    """Return the org-wide default row (store_id=NULL, zone_id=NULL) for a rule type."""
    stmt = select(AlertRule).where(
        AlertRule.rule_type == rule_type,
        AlertRule.store_id.is_(None),  # type: ignore[union-attr]
        AlertRule.zone_id.is_(None),  # type: ignore[union-attr]
    )
    return session.exec(stmt).first()


def _upsert_alert_rule(
    session: Session,
    *,
    rule_type: str,
    threshold: float,
    now: datetime,
    store_id: str | None = None,
    zone_id: str | None = None,
    severity: str = "warning",
    enabled: bool = True,
) -> None:
    """Insert or update one alert_rules row (idempotent on rule_type + store_id + zone_id)."""
    stmt = select(AlertRule).where(AlertRule.rule_type == rule_type)
    if store_id is None:
        stmt = stmt.where(AlertRule.store_id.is_(None))  # type: ignore[union-attr]
    else:
        stmt = stmt.where(AlertRule.store_id == store_id)
    if zone_id is None:
        stmt = stmt.where(AlertRule.zone_id.is_(None))  # type: ignore[union-attr]
    else:
        stmt = stmt.where(AlertRule.zone_id == zone_id)

    existing = session.exec(stmt).first()
    if existing is None:
        session.add(
            AlertRule(
                rule_type=rule_type,
                store_id=store_id,
                zone_id=zone_id,
                threshold=threshold,
                severity=severity,
                enabled=enabled,
                created_at=now,
                updated_at=now,
            )
        )
    else:
        existing.threshold = threshold
        existing.severity = severity
        existing.enabled = enabled
        existing.updated_at = now
        session.add(existing)


def provision_zone_alert_rules(
    zone_id: str,
    zone_type: str,
    store_id: str | None = None,
    session: Session | None = None,
) -> None:
    """Create per-zone alert_rules rows copied from current org-wide defaults.

    Queue rule types are provisioned only when ``zone_type`` is in ``QUEUE_ZONE_TYPES``.
    ``OCCUPANCY_THRESHOLD`` is never provisioned per zone (store-level only).
    """
    now = datetime.now(timezone.utc)

    def _provision(sess: Session) -> None:
        dwell_default = _get_org_default_rule(sess, "DWELL_THRESHOLD")
        if dwell_default is None:
            logger.warning(
                "No org-wide DWELL_THRESHOLD default; skipping alert_rules for zone %s",
                zone_id,
            )
            return

        _upsert_alert_rule(
            sess,
            rule_type="DWELL_THRESHOLD",
            threshold=dwell_default.threshold,
            severity=dwell_default.severity,
            enabled=dwell_default.enabled,
            zone_id=zone_id,
            now=now,
        )

        if zone_type not in QUEUE_ZONE_TYPES:
            return

        for rule_type in ("QUEUE_THRESHOLD", "QUEUE_THRESHOLD_DURATION"):
            queue_default = _get_org_default_rule(sess, rule_type)
            if queue_default is None:
                logger.warning(
                    "No org-wide %s default; skipping for zone %s",
                    rule_type,
                    zone_id,
                )
                continue
            _upsert_alert_rule(
                sess,
                rule_type=rule_type,
                threshold=queue_default.threshold,
                severity=queue_default.severity,
                enabled=queue_default.enabled,
                zone_id=zone_id,
                now=now,
            )

    if session is not None:
        _provision(session)
        return

    with session_scope() as sess:
        _provision(sess)
