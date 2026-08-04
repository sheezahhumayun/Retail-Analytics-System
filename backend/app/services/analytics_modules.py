"""API helpers for per-camera analytics module gating."""

from __future__ import annotations

from analytics.modules import (
    ALL_ANALYTICS_MODULES,
    MODULE_DWELL,
    MODULE_ENTRY_EXIT,
    MODULE_HEATMAP,
    MODULE_OCCUPANCY,
    MODULE_QUEUES,
    MODULE_ZONES,
    module_enabled,
    normalize_modules,
)
from sqlmodel import Session, select

from database.models import Camera, Zone

from ..exceptions import ApiError


def validate_analytics_modules(modules: list[str]) -> list[str]:
    """Normalize module list or raise ``ApiError`` for unknown names."""
    unknown = sorted({m for m in modules if m not in ALL_ANALYTICS_MODULES})
    if unknown:
        raise ApiError(
            422,
            "validation_error",
            "Request validation failed",
            details=[
                {
                    "type": "value_error",
                    "loc": ["body", "analytics_modules"],
                    "msg": f"Unknown analytics module(s): {', '.join(unknown)}",
                    "input": modules,
                }
            ],
        )
    return normalize_modules(modules)


def camera_has_module(camera: Camera, module: str) -> bool:
    return module_enabled(camera.analytics_modules, module)


def store_has_module(session: Session, store_id: str, module: str) -> bool:
    cameras = session.exec(
        select(Camera).where(Camera.store_id == store_id, Camera.status != "disabled")
    ).all()
    return any(camera_has_module(cam, module) for cam in cameras)


def require_camera_module(camera: Camera, module: str) -> None:
    if not camera_has_module(camera, module):
        raise ApiError(
            403,
            "analytics_module_disabled",
            f"Analytics module '{module}' is not enabled for camera '{camera.id}'",
            details={
                "camera_id": camera.id,
                "module": module,
                "enabled_modules": normalize_modules(camera.analytics_modules),
            },
        )


def require_store_module(session: Session, store_id: str, module: str) -> None:
    if not store_has_module(session, store_id, module):
        raise ApiError(
            403,
            "analytics_module_disabled",
            f"No camera in store '{store_id}' has analytics module '{module}' enabled",
            details={"store_id": store_id, "module": module},
        )


def require_zone_module(session: Session, zone: Zone, module: str) -> None:
    camera = session.get(Camera, zone.camera_id)
    if camera is None:
        raise ApiError(404, "camera_not_found", f"Camera '{zone.camera_id}' not found")
    require_camera_module(camera, module)
