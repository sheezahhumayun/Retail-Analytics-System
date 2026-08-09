"""Cascade-delete an organization and all dependent rows."""

from __future__ import annotations

from sqlalchemy import and_, delete, or_
from sqlmodel import Session, col, select

from database.models import (
    Alert,
    AlertRule,
    Camera,
    CountingLine,
    DwellEventRow,
    Event,
    OccupancyMetric,
    Organization,
    ProcessingRun,
    QueueMetric,
    Store,
    Track,
    User,
    VisitorMetric,
    Zone,
    ZoneMetric,
    ZoneShape,
)


def delete_organization_cascade(session: Session, org_id: str) -> None:
    """Delete every row belonging to *org_id*, children before parents."""
    org = session.get(Organization, org_id)
    if org is None:
        return

    store_ids = select(Store.id).where(Store.org_id == org_id)
    camera_ids = (
        select(Camera.id)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
    )
    zone_ids = (
        select(Zone.id)
        .join(Camera, Zone.camera_id == Camera.id)
        .join(Store, Camera.store_id == Store.id)
        .where(Store.org_id == org_id)
    )

    session.exec(delete(ProcessingRun).where(col(ProcessingRun.camera_id).in_(camera_ids)))
    session.exec(
        delete(Event).where(
            or_(
                col(Event.camera_id).in_(camera_ids),
                col(Event.zone_id).in_(zone_ids),
            )
        )
    )

    metadata_store_id = Alert.metadata_["store_id"].as_string()
    session.exec(
        delete(Alert).where(
            or_(
                col(Alert.camera_id).in_(camera_ids),
                col(Alert.zone_id).in_(zone_ids),
                and_(
                    Alert.camera_id.is_(None),  # type: ignore[union-attr]
                    Alert.zone_id.is_(None),  # type: ignore[union-attr]
                    metadata_store_id.in_(store_ids),
                ),
            )
        )
    )

    session.exec(
        delete(AlertRule).where(
            or_(
                AlertRule.org_id == org_id,
                col(AlertRule.store_id).in_(store_ids),
                col(AlertRule.zone_id).in_(zone_ids),
                col(AlertRule.camera_id).in_(camera_ids),
            )
        )
    )

    session.exec(delete(DwellEventRow).where(col(DwellEventRow.zone_id).in_(zone_ids)))
    session.exec(delete(ZoneMetric).where(col(ZoneMetric.zone_id).in_(zone_ids)))
    session.exec(delete(QueueMetric).where(col(QueueMetric.zone_id).in_(zone_ids)))
    session.exec(delete(ZoneShape).where(col(ZoneShape.camera_id).in_(camera_ids)))
    session.exec(delete(Zone).where(col(Zone.camera_id).in_(camera_ids)))
    session.exec(delete(CountingLine).where(col(CountingLine.camera_id).in_(camera_ids)))
    session.exec(delete(Track).where(col(Track.camera_id).in_(camera_ids)))
    session.exec(delete(VisitorMetric).where(col(VisitorMetric.store_id).in_(store_ids)))
    session.exec(
        delete(OccupancyMetric).where(
            or_(
                col(OccupancyMetric.store_id).in_(store_ids),
                col(OccupancyMetric.camera_id).in_(camera_ids),
            )
        )
    )
    session.exec(delete(Camera).where(col(Camera.store_id).in_(store_ids)))
    session.exec(delete(Store).where(Store.org_id == org_id))
    session.exec(delete(User).where(User.org_id == org_id))
    session.delete(org)
