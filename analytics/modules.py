"""Per-camera analytics module identifiers and gating helpers (PRD §8)."""

from __future__ import annotations

from typing import Iterable

MODULE_ENTRY_EXIT = "entry_exit"
MODULE_OCCUPANCY = "occupancy"
MODULE_ZONES = "zones"
MODULE_DWELL = "dwell"
MODULE_HEATMAP = "heatmap"
MODULE_QUEUES = "queues"

ALL_ANALYTICS_MODULES: frozenset[str] = frozenset(
    {
        MODULE_ENTRY_EXIT,
        MODULE_OCCUPANCY,
        MODULE_ZONES,
        MODULE_DWELL,
        MODULE_HEATMAP,
        MODULE_QUEUES,
    }
)

QUEUE_ZONE_TYPES: frozenset[str] = frozenset({"queue", "checkout", "waiting"})


def normalize_modules(modules: Iterable[str] | None) -> list[str]:
    """Return a sorted, de-duplicated list of known module ids."""
    if not modules:
        return []
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in modules:
        name = str(raw).strip()
        if name in ALL_ANALYTICS_MODULES and name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def module_enabled(modules: Iterable[str] | None, module: str) -> bool:
    enabled = set(normalize_modules(modules))
    return module in enabled


def infer_default_modules(
    *,
    has_counting_line: bool = False,
    zone_types: Iterable[str] = (),
) -> list[str]:
    """Infer sensible defaults from existing camera geometry (migration / seed)."""
    inferred: set[str] = set()
    types = {str(t).strip().lower() for t in zone_types}

    if has_counting_line:
        inferred.add(MODULE_ENTRY_EXIT)
        inferred.add(MODULE_OCCUPANCY)

    if types:
        inferred.add(MODULE_ZONES)
        inferred.add(MODULE_DWELL)
        inferred.add(MODULE_HEATMAP)

    if types & QUEUE_ZONE_TYPES:
        inferred.add(MODULE_QUEUES)

    return sorted(inferred)


def zones_for_enabled_modules(
    zones: list,
    modules: Iterable[str] | None,
) -> list:
    """Zones passed to :class:`ZoneDetector` — only when a module needs geometry."""
    enabled = set(normalize_modules(modules))
    if not enabled:
        return []

    from analytics.queues.types import is_queue_zone

    selected: list = []
    for zone in zones:
        if not getattr(zone, "analytics_enabled", True):
            continue
        if MODULE_ZONES in enabled or MODULE_DWELL in enabled:
            selected.append(zone)
        elif MODULE_QUEUES in enabled and is_queue_zone(zone):
            selected.append(zone)
    return selected
