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
import type { CameraSourceType, CameraStatus, Point, Shape, ZoneShape, ZoneType } from "@/lib/types";
import {
  createCountingLine,
  deleteCountingLine,
  getCountingLines,
  updateCountingLine,
} from "@/lib/api/lines";

export { SHAPE_COLORS, ZONE_TYPE_COLORS, ZONE_TYPES };

export type ZonesLinesCameraOption = {
  id: string;
  label: string;
  status: CameraStatus;
  sourceType: CameraSourceType;
};

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

function mapShapesSafe(
  zones: BackendZoneShape[],
  lines: BackendCountingLine[],
): Shape[] {
  const mapped: Shape[] = [];

  for (const zone of zones) {
    try {
      mapped.push(mapZoneShape(zone));
    } catch (err) {
      console.error(`Failed to map zone shape "${zone.id}"`, err);
    }
  }

  for (const line of lines) {
    try {
      mapped.push(mapCountingLine(line));
    } catch (err) {
      console.error(`Failed to map counting line "${line.id}"`, err);
    }
  }

  return mapped;
}

async function listAllCameras(): Promise<BackendCamera[]> {
  return apiRequest<BackendCamera[]>("/api/cameras");
}

export async function getAllShapes(options?: { includeDisabled?: boolean }): Promise<Shape[]> {
  const query = options?.includeDisabled ? { include_disabled: true } : undefined;
  const [zones, lines] = await Promise.all([
    apiRequest<BackendZoneShape[]>("/api/zones", { query }),
    apiRequest<BackendCountingLine[]>("/api/lines", { query }),
  ]);
  return mapShapesSafe(zones, lines);
}

export async function getCamerasList(): Promise<ZonesLinesCameraOption[]> {
  const cameras = await listAllCameras();
  return cameras.map((camera) => ({
    id: camera.id,
    label: `${camera.name}${camera.location ? ` (${camera.location})` : ""}`,
    status: (camera.status as CameraStatus) ?? "offline",
    sourceType: (camera.source_type ?? "live") as CameraSourceType,
  }));
}

export async function getZoneShapes(camera_id: string): Promise<ZoneShape[]> {
  const zones = await apiRequest<BackendZoneShape[]>("/api/zones", {
    query: { camera_id },
  });
  return zones.map((zone) => mapZoneShape(zone));
}

/** Zones + counting lines for one camera (editor hydration after save/reload). */
export async function getShapesForCamera(
  camera_id: string,
  options?: { includeDisabled?: boolean },
): Promise<Shape[]> {
  const query: Record<string, string | boolean> = { camera_id };
  if (options?.includeDisabled) {
    query.include_disabled = true;
  }
  const [zones, lines] = await Promise.all([
    apiRequest<BackendZoneShape[]>("/api/zones", { query }),
    apiRequest<BackendCountingLine[]>("/api/lines", { query }),
  ]);
  return mapShapesSafe(zones, lines);
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
): Promise<ZoneShape> {
  const body: Record<string, unknown> = {};
  if (data.name !== undefined) body.name = data.name;
  if (data.type !== undefined) body.type = frontendZoneTypeToBackend(data.type);
  if (data.points !== undefined) {
    body.polygon_points = data.points.map((point) => denormalizePoint(point));
  }

  const updated = await apiRequest<BackendZoneShape>(`/api/zones/${id}`, {
    method: "PUT",
    body,
  });
  return mapZoneShape(updated);
}

/**
 * Throws on failure rather than swallowing errors — callers (`handleDeleteShape`,
 * `syncCameraShapes`) must not remove the shape from local state unless this
 * actually persisted, otherwise a failed DELETE looks like a successful one
 * until the next reload/refetch brings the shape back.
 */
export async function deleteZone(id: string): Promise<void> {
  await apiRequest<void>(`/api/zones/${id}`, { method: "DELETE" });
}

// Backwards compatibility for lines.ts during migration — no shared in-memory store.
export function __getShapes(): Shape[] {
  throw new Error("__getShapes is not available with the live API backend");
}

export function __setShapes(_next: Shape[]): void {
  throw new Error("__setShapes is not available with the live API backend");
}

export { getCountingLines };

function isActiveShape(shape: Shape): boolean {
  return shape.status !== "disabled";
}

/** Persist create/update/delete for one camera's shapes vs last saved snapshot. */
export async function syncCameraShapes(
  cameraId: string,
  current: Shape[],
  baseline: Shape[],
): Promise<void> {
  const activeCurrent = current.filter(isActiveShape);
  const activeBaseline = baseline.filter(isActiveShape);

  if (activeCurrent.length === 0 && activeBaseline.length > 0) {
    throw new Error(
      "No shapes to save for this camera. Redraw the zone or reload the page, then try Save again.",
    );
  }

  const baselineIds = new Set(activeBaseline.map((shape) => shape.id));
  const currentIds = new Set(activeCurrent.map((shape) => shape.id));

  for (const shape of activeBaseline) {
    if (!currentIds.has(shape.id)) {
      if (shape.kind === "zone") {
        await deleteZone(shape.id);
      } else {
        await deleteCountingLine(shape.id);
      }
    }
  }

  for (const shape of activeCurrent) {
    if (shape.cameraId !== cameraId) continue;

    if (baselineIds.has(shape.id)) {
      if (shape.kind === "zone") {
        if (shape.points.length < 3) {
          throw new Error(`Zone "${shape.name}" must have at least 3 points`);
        }
        await updateZone(shape.id, {
          name: shape.name,
          type: shape.type,
          points: shape.points,
        });
      } else {
        const updatedLine = await updateCountingLine(shape.id, {
          name: shape.name,
          points: shape.points,
          insideSide: shape.insideSide,
        });
        if (!updatedLine) {
          throw new Error(`Failed to update counting line "${shape.name}"`);
        }
      }
      continue;
    }

    if (shape.kind === "zone") {
      if (shape.points.length < 3) {
        throw new Error(`Zone "${shape.name}" must have at least 3 points`);
      }
      await createZone({
        id: shape.id,
        cameraId: shape.cameraId,
        name: shape.name,
        type: shape.type,
        points: shape.points,
        color: shape.color,
      });
    } else {
      await createCountingLine({
        id: shape.id,
        cameraId: shape.cameraId,
        name: shape.name,
        points: shape.points,
        insideSide: shape.insideSide,
        color: shape.color,
      });
    }
  }
}
