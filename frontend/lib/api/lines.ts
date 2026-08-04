import { apiRequest } from "@/lib/api/client";
import {
  mapCountingLine,
  type BackendCountingLine,
} from "@/lib/api/mappers";
import { SHAPE_COLORS } from "@/lib/zones-lines-data";
import type { LineShape, Point } from "@/lib/types";

export type CreateCountingLineData = Omit<LineShape, "kind" | "id" | "color"> & {
  id?: string;
  color?: string;
};

export type UpdateCountingLineData = Partial<
  Pick<LineShape, "name" | "points" | "insideSide" | "color" | "cameraId">
>;

function denormalizePoint(point: Point, width = 640, height = 360): { x: number; y: number } {
  return {
    x: (point.x / 100) * width,
    y: (point.y / 100) * height,
  };
}

export async function getCountingLines(camera_id: string): Promise<LineShape[]> {
  const lines = await apiRequest<BackendCountingLine[]>("/api/lines", {
    query: { camera_id },
  });
  return lines.map(mapCountingLine);
}

export async function createCountingLine(
  data: CreateCountingLineData,
): Promise<LineShape> {
  const id =
    data.id ??
    `line_${data.cameraId}_${Date.now().toString(36)}`.replace(/[^a-zA-Z0-9_-]/g, "_");
  const created = await apiRequest<BackendCountingLine>("/api/lines", {
    method: "POST",
    body: {
      id,
      camera_id: data.cameraId,
      name: data.name,
      point_a: denormalizePoint(data.points[0]),
      point_b: denormalizePoint(data.points[1]),
      direction:
        data.insideSide === "right" ? "right_is_inside" : "left_is_inside",
    },
  });
  return mapCountingLine(created);
}

export async function updateCountingLine(
  id: string,
  data: UpdateCountingLineData,
): Promise<LineShape | null> {
  const body: Record<string, unknown> = {};
  if (data.name !== undefined) body.name = data.name;
  if (data.points !== undefined) {
    body.point_a = denormalizePoint(data.points[0]);
    body.point_b = denormalizePoint(data.points[1]);
  }
  if (data.insideSide !== undefined) {
    body.direction =
      data.insideSide === "right" ? "right_is_inside" : "left_is_inside";
  }

  try {
    const updated = await apiRequest<BackendCountingLine>(`/api/lines/${id}`, {
      method: "PUT",
      body,
    });
    return mapCountingLine(updated);
  } catch {
    return null;
  }
}

/** Throws on failure — see `deleteZone` in `zones.ts` for why this must not swallow errors. */
export async function deleteCountingLine(id: string): Promise<void> {
  await apiRequest<void>(`/api/lines/${id}`, { method: "DELETE" });
}

export { SHAPE_COLORS };
