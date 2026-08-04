"use client";

import { useMemo } from "react";

import type {
  Camera,
  DataRow,
  HeatmapCamera,
  ScopeCamera,
  StatSummary,
  Store,
  ZoneRow,
} from "@/lib/types";

export function getStoreCameraIds(store: Store | null): string[] {
  return store?.cameras.map((camera) => camera.id) ?? [];
}

export function filterLiveCameras(
  cameras: Camera[],
  cameraId: string | null,
  storeCameraIds: string[],
): Camera[] {
  if (cameraId) {
    return cameras.filter((camera) => camera.id === cameraId);
  }
  if (storeCameraIds.length > 0) {
    return cameras.filter((camera) => storeCameraIds.includes(camera.id));
  }
  return cameras;
}

export function filterHeatmapCameras(
  cameras: HeatmapCamera[],
  cameraId: string | null,
  storeCameraIds: string[],
): HeatmapCamera[] {
  if (cameraId) {
    const match = cameras.filter((camera) => camera.id === cameraId);
    return match.length > 0 ? match : cameras;
  }
  if (storeCameraIds.length > 0) {
    const filtered = cameras.filter((camera) => storeCameraIds.includes(camera.id));
    return filtered.length > 0 ? filtered : cameras;
  }
  return cameras;
}

/** Global scope is the outer filter; pageCamera narrows within allowed ids. */
export function resolveEffectiveCameraId(
  globalCameraId: string | null,
  pageCameraId: string | null,
  allowedIds: string[],
): string {
  if (pageCameraId && allowedIds.includes(pageCameraId)) return pageCameraId;
  if (globalCameraId && allowedIds.includes(globalCameraId)) {
    return globalCameraId;
  }
  return allowedIds[0] ?? pageCameraId ?? globalCameraId ?? "";
}

export function resolveZoneId(
  zoneId: string | null,
  camera: ScopeCamera | null,
  store: Store | null,
): string {
  if (zoneId) return zoneId;
  if (camera?.zones[0]?.id) return camera.zones[0].id;
  if (store) {
    for (const scopedCamera of store.cameras) {
      if (scopedCamera.zones[0]?.id) return scopedCamera.zones[0].id;
    }
  }
  return "store1";
}

export function filterZonePerformanceRows(
  rows: ZoneRow[],
  zoneId: string | null,
  storeId: string | null,
): ZoneRow[] {
  if (zoneId) {
    const match = rows.find((row) => row.id === zoneId);
    return match ? [match] : rows;
  }
  if (storeId) {
    return rows;
  }
  return rows;
}

export type CustomerFlowCamera = { id: string; label: string };

export function filterCustomerFlowCameras(
  cameras: CustomerFlowCamera[],
  globalCameraId: string | null,
  storeCameraIds: string[],
): CustomerFlowCamera[] {
  if (globalCameraId) {
    const match = cameras.filter((camera) => camera.id === globalCameraId);
    if (match.length > 0) return match;
  }
  if (storeCameraIds.length > 0) {
    const filtered = cameras.filter((camera) => storeCameraIds.includes(camera.id));
    if (filtered.length > 0) return filtered;
  }
  return cameras;
}

export function resolveCustomerFlowCameraId(
  globalCameraId: string | null,
  pageCameraId: string,
  allowedIds: string[],
): string {
  if (allowedIds.includes(pageCameraId)) return pageCameraId;
  if (globalCameraId && allowedIds.includes(globalCameraId)) {
    return globalCameraId;
  }
  return allowedIds[0] ?? pageCameraId;
}

/** Aggregate zones from all cameras in the current store for the scope selector. */
export function zonesForScope(
  store: Store | null,
  camera: ScopeCamera | null,
): Array<{ id: string; name: string; type?: string }> {
  if (camera) return camera.zones;
  if (!store) return [];
  const seen = new Map<string, { id: string; name: string; type?: string }>();
  for (const storeCamera of store.cameras) {
    for (const zone of storeCamera.zones) {
      seen.set(zone.id, zone);
    }
  }
  return [...seen.values()];
}
