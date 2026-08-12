#!/usr/bin/env python
"""One-off backfill — org-wide alert_rules defaults for orgs missing any rules.

For each organization with zero alert_rules rows scoped to its org_id, seeds the
four org-wide defaults (same values as org creation). Then provisions per-zone rules
for existing zones that have no rules for that org (Phase 6 logic).

Usage (from repo root, Postgres running):

    set DATABASE_URL=postgresql+psycopg2://retail:retail@localhost:5433/retail_analytics
    backend\\.venv\\Scripts\\python.exe tests/scripts/backfill_alert_rules_for_existing_orgs.py

Safe to re-run (idempotent upserts).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from backend.app.services.alert_rules import (  # noqa: E402
    provision_zone_alert_rules,
    seed_org_wide_default_alert_rules,
)
from database.models import AlertRule, Camera, Organization, Store, Zone  # noqa: E402
from database.session import session_scope  # noqa: E402
from sqlmodel import func, select  # noqa: E402


def _alert_rule_count_for_org(session, org_id: str) -> int:
    return session.exec(
        select(func.count()).select_from(AlertRule).where(AlertRule.org_id == org_id)
    ).one()


def _zones_for_org(session, org_id: str) -> list[Zone]:
    store_ids = session.exec(select(Store.id).where(Store.org_id == org_id)).all()
    if not store_ids:
        return []
    camera_ids = session.exec(
        select(Camera.id).where(Camera.store_id.in_(store_ids))  # type: ignore[attr-defined]
    ).all()
    if not camera_ids:
        return []
    return list(
        session.exec(select(Zone).where(Zone.camera_id.in_(camera_ids))).all()  # type: ignore[attr-defined]
    )


def _zone_rule_count_for_org(session, org_id: str, zone_id: str) -> int:
    return session.exec(
        select(func.count())
        .select_from(AlertRule)
        .where(AlertRule.org_id == org_id, AlertRule.zone_id == zone_id)
    ).one()


def _camera_store_id(session, camera_id: str) -> str | None:
    camera = session.get(Camera, camera_id)
    return camera.store_id if camera is not None else None


def backfill() -> None:
    with session_scope() as session:
        orgs = session.exec(select(Organization).order_by(Organization.id)).all()
        targets = [org for org in orgs if _alert_rule_count_for_org(session, org.id) == 0]

        if not targets:
            print("No organizations need backfill (all have at least one alert_rules row).")
            return

        print(f"Backfilling {len(targets)} organization(s) with zero alert_rules...")
        for org in targets:
            before = _alert_rule_count_for_org(session, org.id)
            print(f"\n=== {org.id} ({org.name!r}) — rules before: {before} ===")

            seed_org_wide_default_alert_rules(session, org.id)
            session.flush()

            org_wide = session.exec(
                select(AlertRule).where(
                    AlertRule.org_id == org.id,
                    AlertRule.store_id.is_(None),  # type: ignore[union-attr]
                    AlertRule.zone_id.is_(None),  # type: ignore[union-attr]
                )
            ).all()
            print(f"  org-wide defaults: {len(org_wide)} rows")
            for rule in org_wide:
                print(
                    f"    {rule.rule_type}: threshold={rule.threshold} "
                    f"severity={rule.severity} enabled={rule.enabled}"
                )

            zones = _zones_for_org(session, org.id)
            print(f"  zones in org: {len(zones)}")
            for zone in zones:
                zone_before = _zone_rule_count_for_org(session, org.id, zone.id)
                if zone_before > 0:
                    print(f"    zone {zone.id}: already has {zone_before} rule(s), skip")
                    continue
                store_id = _camera_store_id(session, zone.camera_id)
                provision_zone_alert_rules(
                    zone.id,
                    zone.zone_type,
                    store_id=store_id,
                    org_id=org.id,
                    session=session,
                )
                zone_after = _zone_rule_count_for_org(session, org.id, zone.id)
                print(f"    zone {zone.id} ({zone.zone_type}): provisioned {zone_after} rule(s)")

            after = _alert_rule_count_for_org(session, org.id)
            print(f"  rules after: {after}")

        session.commit()
        print("\nBackfill complete.")


if __name__ == "__main__":
    backfill()
