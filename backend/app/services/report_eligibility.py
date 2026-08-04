"""Scope and exclusion metadata for store-wide reports (analytics_modules gating)."""

from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session, col, select

from analytics.modules import QUEUE_ZONE_TYPES

from database.models import Camera, Zone

from ..exceptions import ApiError
from ..schemas.extended.reports import ReportCoverage, ReportExclusion
from .analytics_modules import (
    MODULE_DWELL,
    MODULE_ENTRY_EXIT,
    MODULE_HEATMAP,
    MODULE_OCCUPANCY,
    MODULE_QUEUES,
    MODULE_ZONES,
    camera_has_module,
    require_camera_module,
)

REPORT_TYPE_MODULE: dict[str, str] = {
    "traffic": MODULE_ENTRY_EXIT,
    "occupancy": MODULE_OCCUPANCY,
    "zones": MODULE_ZONES,
    "dwell": MODULE_DWELL,
    "queues": MODULE_QUEUES,
}

MODULE_LABELS: dict[str, str] = {
    MODULE_ENTRY_EXIT: "entry/exit",
    MODULE_OCCUPANCY: "occupancy",
    MODULE_ZONES: "zone analytics",
    MODULE_DWELL: "dwell analytics",
    MODULE_HEATMAP: "heatmap",
    MODULE_QUEUES: "queue analytics",
}


@dataclass(frozen=True, slots=True)
class ReportScope:
    module: str
    cameras_in_scope: list[Camera]
    eligible_cameras: list[Camera]
    zones_in_scope: list[Zone]
    eligible_zones: list[Zone]
    coverage: ReportCoverage
    exclusions: list[ReportExclusion]
    footnotes: list[str]


def _cameras_in_scope(
    session: Session,
    store_id: str,
    camera_id: str | None,
) -> list[Camera]:
    stmt = select(Camera).where(Camera.store_id == store_id, Camera.status != "disabled")
    if camera_id is not None:
        stmt = stmt.where(Camera.id == camera_id)
    return list(session.exec(stmt).all())


def _zones_in_scope(
    session: Session,
    store_id: str,
    camera_id: str | None,
) -> list[Zone]:
    camera_ids = [c.id for c in _cameras_in_scope(session, store_id, camera_id)]
    if not camera_ids:
        return []
    return list(session.exec(select(Zone).where(col(Zone.camera_id).in_(camera_ids))).all())


def _zone_eligible_for_module(zone: Zone, camera: Camera, module: str) -> bool:
    if not camera_has_module(camera, module):
        return False
    if module == MODULE_QUEUES:
        return (
            zone.analytics_enabled
            and str(zone.zone_type).strip().lower() in QUEUE_ZONE_TYPES
        )
    return True


def resolve_report_scope(
    session: Session,
    report_type: str,
    store_id: str,
    camera_id: str | None = None,
) -> ReportScope:
    if report_type not in REPORT_TYPE_MODULE:
        raise ApiError(400, "invalid_report_type", f"Unknown report type: {report_type}")

    module = REPORT_TYPE_MODULE[report_type]
    cameras = _cameras_in_scope(session, store_id, camera_id)
    if camera_id is not None:
        camera = session.get(Camera, camera_id)
        if camera is None:
            raise ApiError(404, "camera_not_found", f"Camera '{camera_id}' not found")
        if camera.store_id != store_id:
            raise ApiError(
                400,
                "invalid_scope",
                f"Camera '{camera_id}' does not belong to store '{store_id}'",
            )
        require_camera_module(camera, module)

    camera_by_id = {c.id: c for c in cameras}
    eligible_cameras = [c for c in cameras if camera_has_module(c, module)]
    excluded_cameras = [c for c in cameras if not camera_has_module(c, module)]

    zones = _zones_in_scope(session, store_id, camera_id)
    eligible_zones: list[Zone] = []
    excluded_zones: list[Zone] = []
    for zone in zones:
        camera = camera_by_id.get(zone.camera_id)
        if camera is None:
            continue
        if _zone_eligible_for_module(zone, camera, module):
            eligible_zones.append(zone)
        else:
            excluded_zones.append(zone)

    exclusions: list[ReportExclusion] = []
    label = MODULE_LABELS.get(module, module)
    for camera in excluded_cameras:
        exclusions.append(
            ReportExclusion(
                kind="camera",
                id=camera.id,
                name=camera.name,
                module=module,
                reason=f"{label} not enabled",
            )
        )
    for zone in excluded_zones:
        camera = camera_by_id.get(zone.camera_id)
        cam_name = camera.name if camera else zone.camera_id
        if camera and not camera_has_module(camera, module):
            reason = f"{label} not enabled for camera {cam_name}"
        elif module == MODULE_QUEUES:
            reason = f"not a queue zone (camera {cam_name})"
        else:
            reason = f"excluded from {label} scope"
        exclusions.append(
            ReportExclusion(
                kind="zone",
                id=zone.id,
                name=zone.name,
                module=module,
                reason=reason,
            )
        )

    footnotes: list[str] = []
    if excluded_cameras:
        names = ", ".join(c.name for c in excluded_cameras)
        footnotes.append(f"{label} not enabled for cameras: {names}")
    zone_only_excluded = [
        z for z in excluded_zones if camera_by_id.get(z.camera_id) and camera_has_module(
            camera_by_id[z.camera_id], module
        )
    ]
    if zone_only_excluded and module == MODULE_QUEUES:
        names = ", ".join(z.name for z in zone_only_excluded)
        footnotes.append(f"Non-queue zones excluded from queue totals: {names}")

    coverage = ReportCoverage(
        module=module,
        cameras_in_scope=len(cameras),
        cameras_eligible=len(eligible_cameras),
        zones_in_scope=len(zones),
        zones_eligible=len(eligible_zones),
    )
    if cameras and len(eligible_cameras) < len(cameras):
        footnotes.insert(
            0,
            f"{label} tracked at {len(eligible_cameras)} of {len(cameras)} cameras in scope",
        )

    return ReportScope(
        module=module,
        cameras_in_scope=cameras,
        eligible_cameras=eligible_cameras,
        zones_in_scope=zones,
        eligible_zones=eligible_zones,
        coverage=coverage,
        exclusions=exclusions,
        footnotes=footnotes,
    )


def eligible_cameras_for_store(
    session: Session,
    store_id: str,
    module: str,
    camera_id: str | None = None,
) -> list[Camera]:
    """Cameras in scope that have ``module`` enabled."""
    return [
        camera
        for camera in _cameras_in_scope(session, store_id, camera_id)
        if camera_has_module(camera, module)
    ]


def eligible_camera_ids(scope: ReportScope) -> list[str]:
    return [c.id for c in scope.eligible_cameras]


def eligible_zone_ids(scope: ReportScope) -> list[str]:
    return [z.id for z in scope.eligible_zones]
