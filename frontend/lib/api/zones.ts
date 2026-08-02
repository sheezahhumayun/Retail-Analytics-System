import { apiRequest } from "@/lib/api/client";
import {
  mapCountingLine,
  mapZoneShape,
  type BackendCountingLine,
  type BackendCamera,
  type BackendZoneShape,
} from "@/lib/api/mappers";
import {
  SHAPE_COLORS,
  ZONE_TYPE_COLORS,
  ZONE_TYPES,
} from "@/lib/zones-lines-data";
import type { Point, Shape, ZoneShape, ZoneType } from "@/lib/types";
import { getCountingLines } from "@/lib/api/lines";

export { SHAPE_COLORS, ZONE_TYPE_COLORS, ZONE_TYPES };

export type ZonesLinesCameraOption = { id: string; label: string };

export type CreateZoneData = Omit<ZoneShape, "kind" | "id" | "color"> & {
  id?: string;
  color?: string;
};

export type UpdateZoneData = Partial<
  Pick<ZoneShape, "name" | "type" | "points" | "color" | "cameraId">
>;

function frontendZoneTypeToBackend(type: ZoneType): string {
  if (type === "checkout") return "checkout_queue";
  return type;
}

function denormalizePoint(point: Point, width = 640, height = 360): [number, number] {
  return [(point.x / 100) * width, (point.y / 100) * height];
}

async function listAllCameras(): Promise<BackendCamera[]> {
  return apiRequest<BackendCamera[]>("/api/cameras");
}

export async function getAllShapes(): Promise<Shape[]> {
  // Two list calls total — not N per camera (camera_id is optional on both endpoints).
  const [zones, lines] = await Promise.all([
    apiRequest<BackendZoneShape[]>("/api/zones"),
    apiRequest<BackendCountingLine[]>("/api/lines"),
  ]);
  return [...zones.map(mapZoneShape), ...lines.map(mapCountingLine)];
}

export async function getCamerasList(): Promise<ZonesLinesCameraOption[]> {
  const cameras = await listAllCameras();
  return cameras.map((camera) => ({
    id: camera.id,
    label: `${camera.name}${camera.location ? ` (${camera.location})` : ""}`,
  }));
}

export async function getZoneShapes(camera_id: string): Promise<ZoneShape[]> {
  const zones = await apiRequest<BackendZoneShape[]>("/api/zones", {
    query: { camera_id },
  });
  return zones.map(mapZoneShape);
}

export async function createZone(data: CreateZoneData): Promise<ZoneShape> {
  const id =
    data.id ??
    `zone_${data.cameraId}_${Date.now().toString(36)}`.replace(/[^a-zA-Z0-9_-]/g, "_");
  const created = await apiRequest<BackendZoneShape>("/api/zones", {
    method: "POST",
    body: {
      id,
      camera_id: data.cameraId,
      name: data.name,
      type: frontendZoneTypeToBackend(data.type),
      polygon_points: data.points.map((point) => denormalizePoint(point)),
    },
  });
  return mapZoneShape(created);
}

export async function updateZone(
  id: string,
  data: UpdateZoneData,
): Promise<ZoneShape | null> {
  const body: Record<string, unknown> = {};
  if (data.name !== undefined) body.name = data.name;
  if (data.type !== undefined) body.type = frontendZoneTypeToBackend(data.type);
  if (data.points !== undefined) {
    body.polygon_points = data.points.map((point) => denormalizePoint(point));
  }

  try {
    const updated = await apiRequest<BackendZoneShape>(`/api/zones/${id}`, {
      method: "PUT",
      body,
    });
    return mapZoneShape(updated);
  } catch {
    return null;
  }
}

export async function deleteZone(id: string): Promise<boolean> {
  try {
    await apiRequest<void>(`/api/zones/${id}`, { method: "DELETE" });
    return true;
  } catch {
    return false;
  }
}

// Backwards compatibility for lines.ts during migration — no shared in-memory store.
export function __getShapes(): Shape[] {
  throw new Error("__getShapes is not available with the live API backend");
}

export function __setShapes(_next: Shape[]): void {
  throw new Error("__setShapes is not available with the live API backend");
}

export { getCountingLines };
